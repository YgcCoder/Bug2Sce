#!/usr/bin/env python3
"""Prepare the local Round 2 video package and manual-review CSV.

PSSD execution artifacts are read-only inputs.  The local package uses one
stable review_id per candidate so the video filenames and review table match.
"""

from __future__ import annotations

import csv
import json
import os
import shutil
from pathlib import Path
from typing import Any

import parse_pure_llm_phase3_results as phase3


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "processed" / "experiments"
PSSD_JSON = Path("<PSSD_ROOT>/Round2_JSON")
PSSD_RUNS = Path("<PSSD_ROOT>/Round2_RUNS")
OUTPUT_ROOT = Path(
    "<WORKSPACE_ROOT>/round2_videos"
)
VIDEO_DIR = OUTPUT_ROOT / "videos"
MISSING_DIR = OUTPUT_ROOT / "missing_video"
REVIEW_CSV = OUTPUT_ROOT / "review_checklist.csv"
MANIFEST_CSV = OUTPUT_ROOT / "video_manifest.csv"
MISSING_CSV = OUTPUT_ROOT / "missing_videos.csv"

MODEL = "claude-sonnet-4-5"
EVENT_ORDER = [("crash", "C"), ("stuck", "S"), ("lane_invasion", "L"), ("red", "R")]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8", errors="ignore"))


def first_json(path: Path) -> tuple[dict[str, Any] | None, str]:
    files = sorted(p for p in path.glob("*.json") if not p.name.startswith("._"))
    if not files:
        return None, ""
    try:
        return load_json(files[0]), str(files[0])
    except Exception:  # noqa: BLE001
        return None, str(files[0])


def root_cause_pattern(case_id: str) -> str:
    path = EXPERIMENTS / "phase1_api_outputs" / f"{case_id}__claude-sonnet-4-5.json"
    if not path.exists():
        return ""
    return str((load_json(path).get("parsed_response") or {}).get("root_cause_pattern", ""))


def round2_spec(case_id: str, index: int) -> dict[str, Any]:
    path = (
        EXPERIMENTS
        / "round2_feedback"
        / "metadata"
        / f"{case_id}__Round2_{index:02d}.metadata.json"
    )
    return (load_json(path).get("candidate_spec") or {}) if path.exists() else {}


def link_or_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return
    try:
        os.link(source, destination)
    except OSError:
        shutil.copyfile(source, destination)


def status_hint(status: str, expected: str, observed: str, pattern: str) -> str:
    if status == "crash_or_minimal_artifacts":
        return "无视频/主要证据，先标 not preserved 或在备注写 crash；该 seed 需进入下一轮。"
    if not observed:
        return f"未检测到 oracle。看视频是否仍出现 seed 机制；expected={expected}。"
    return (
        f"核对视频是否保持 seed 机制，不要只按 oracle 判断。expected={expected}, "
        f"observed={observed}. Seed pattern: {pattern}"
    )


def main() -> int:
    selected = {
        row["Case ID"]: row
        for row in read_csv(EXPERIMENTS / "selected_30_drivefuzz_seeds.csv")
    }
    run_dirs = sorted(
        path for path in PSSD_RUNS.glob("case_*__Round2_*") if path.is_dir()
    )
    if len(run_dirs) != 18:
        raise RuntimeError(f"Expected 18 Round 2 run directories, found {len(run_dirs)}")

    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    MISSING_DIR.mkdir(parents=True, exist_ok=True)
    review_rows: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    missing_rows: list[dict[str, Any]] = []

    for sequence, run_dir in enumerate(run_dirs, start=1):
        review_id = f"{sequence:03d}"
        case_id, suffix = run_dir.name.split("__Round2_")
        candidate_index = int(suffix)
        candidate = f"Round2_{candidate_index:02d}"
        seed = selected[case_id]
        expected = seed.get("Group", "")
        pattern = root_cause_pattern(case_id)
        spec = round2_spec(case_id, candidate_index)
        candidate_json = PSSD_JSON / f"{case_id}__Round2_{candidate_index:02d}.json"

        error_obj, error_path = first_json(run_dir / "errors")
        score_obj, score_path = first_json(run_dir / "scores")
        events = error_obj.get("events", {}) if isinstance(error_obj, dict) else {}
        events = events if isinstance(events, dict) else {}
        observed = "+".join(code for key, code in EVENT_ORDER if events.get(key) is True)
        oracle_match = phase3.compare_expected_observed(
            set(expected.split("+")) if expected else set(),
            set(observed.split("+")) if observed else set(),
        )

        bag_files = sorted((run_dir / "rosbags").glob("*.bag"))
        score_files = sorted((run_dir / "scores").glob("*.json"))
        camera_files = sorted(
            p for p in (run_dir / "camera").glob("*.mp4") if not p.name.startswith("._")
        )
        status = phase3.classify(
            json_ok=candidate_json.exists(),
            run_exists=True,
            has_error=bool(error_path),
            has_bag=bool(bag_files),
            has_score=bool(score_files),
            has_camera=bool(camera_files),
            observed=set(observed.split("+")) if observed else set(),
            event_other=str(events.get("other", "")),
        )
        category = phase3.preliminary_category(status, oracle_match)

        local_videos = {"front": "", "rear": ""}
        for view in ("front", "rear"):
            source = next((p for p in camera_files if p.name.endswith(f"-{view}.mp4")), None)
            if source is None:
                continue
            filename = (
                f"review_{review_id}__{case_id}__{candidate}__"
                f"exp={expected or 'none'}_obs={observed or 'none'}__{view}.mp4"
            )
            destination = VIDEO_DIR / filename
            link_or_copy(source, destination)
            local_videos[view] = str(destination)
            manifest_rows.append(
                {
                    "review_id": review_id,
                    "candidate_id": run_dir.name,
                    "case_id": case_id,
                    "candidate": candidate,
                    "view": view,
                    "source_path": str(source),
                    "local_video_path": str(destination),
                }
            )

        missing_views = [view for view, path in local_videos.items() if not path]
        if missing_views:
            marker = MISSING_DIR / f"review_{review_id}__{run_dir.name}__NO_VIDEO.txt"
            marker.write_text(
                f"review_id={review_id}\ncandidate_id={run_dir.name}\n"
                f"missing_views={','.join(missing_views)}\nexecution_status={status}\n"
                f"run_dir={run_dir}\n",
                encoding="utf-8",
            )
            missing_rows.append(
                {
                    "review_id": review_id,
                    "candidate_id": run_dir.name,
                    "case_id": case_id,
                    "candidate": candidate,
                    "missing_views": ",".join(missing_views),
                    "execution_status": status,
                    "run_dir": str(run_dir),
                    "marker": str(marker),
                }
            )

        score_summary = ""
        if isinstance(score_obj, dict):
            score_summary = "; ".join(f"{key}={value}" for key, value in score_obj.items())
        review_rows.append(
            {
                "review_id": review_id,
                "candidate_id": run_dir.name,
                "case_id": case_id,
                "round": 2,
                "model": MODEL,
                "candidate": candidate,
                "expected_oracle_codes": expected,
                "observed_oracle_codes": observed,
                "oracle_match_status": oracle_match,
                "execution_status": status,
                "preliminary_category": category,
                "expected_root_cause_pattern": pattern,
                "round2_high_level_variant": spec.get("high_level_variant", ""),
                "round2_mutation_intent": spec.get("mutation_intent", ""),
                "decision_hint_zh": status_hint(status, expected, observed, pattern),
                "event_crash": events.get("crash", ""),
                "event_stuck": events.get("stuck", ""),
                "event_lane_invasion": events.get("lane_invasion", ""),
                "event_red": events.get("red", ""),
                "event_other": events.get("other", ""),
                "num_frames": error_obj.get("num_frames", "") if isinstance(error_obj, dict) else "",
                "elapsed_time": error_obj.get("elapsed_time", "") if isinstance(error_obj, dict) else "",
                "bag_count": len(bag_files),
                "score_count": len(score_files),
                "camera_count": len(camera_files),
                "score_summary": score_summary,
                "front_video": local_videos["front"],
                "rear_video": local_videos["rear"],
                "candidate_json": str(candidate_json),
                "error_json": error_path,
                "score_json": score_path,
                "run_dir": str(run_dir),
                "manual_preservation_result": "",
                "manual_failure_type": "",
                "manual_checked": "",
                "manual_notes": "",
            }
        )

    review_fields = list(review_rows[0])
    manifest_fields = list(manifest_rows[0]) if manifest_rows else []
    missing_fields = list(missing_rows[0]) if missing_rows else []
    write_csv(REVIEW_CSV, review_rows, review_fields)
    write_csv(MANIFEST_CSV, manifest_rows, manifest_fields)
    write_csv(MISSING_CSV, missing_rows, missing_fields)
    (OUTPUT_ROOT / "README.txt").write_text(
        "Round 2 manual review package\n\n"
        "Open review_checklist.xlsx and the videos folder. Video filenames use the same review_id as the worksheet.\n"
        "Fill manual_preservation_result with strictly preserved, partial or boundary, or not preserved.\n"
        "Fill manual_failure_type, manual_checked=yes, and manual_notes when useful.\n"
        "case_039 candidates have no videos and are represented by missing_video markers.\n",
        encoding="utf-8",
    )
    print(f"review_rows={len(review_rows)}")
    print(f"video_files={len(manifest_rows)}")
    print(f"missing_candidates={len(missing_rows)}")
    print(REVIEW_CSV)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
