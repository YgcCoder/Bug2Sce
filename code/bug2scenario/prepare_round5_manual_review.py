#!/usr/bin/env python3
"""Prepare the local Round 5 video package and manual-review CSV."""

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
PSSD_JSON = Path("<PSSD_ROOT>/Round5_JSON")
PSSD_RUNS = Path("<PSSD_ROOT>/Round5_RUNS")
OUTPUT_ROOT = Path(
    "<WORKSPACE_ROOT>/round5_videos"
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


def round5_spec(case_id: str, index: int) -> dict[str, Any]:
    path = (
        EXPERIMENTS
        / "round5_feedback"
        / "metadata"
        / f"{case_id}__Round5_{index:02d}.metadata.json"
    )
    return (load_json(path).get("candidate_spec") or {}) if path.exists() else {}


def link_or_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size == source.stat().st_size:
        return
    if destination.exists():
        destination.unlink()
    try:
        os.link(source, destination)
    except OSError:
        shutil.copyfile(source, destination)


def status_hint(status: str, expected: str, observed: str, pattern: str) -> str:
    if status == "missing_execution_output":
        return "未执行/无输出目录，无法人工判断；不要标为保持成功。"
    if status == "crash_or_minimal_artifacts":
        return "无视频/主要证据，标 not preserved 或在备注写 crash；该 seed 仍未恢复。"
    if not observed:
        return f"未检测到 oracle。看视频是否仍出现原始 seed 机制；expected={expected}。"
    return (
        f"核对视频是否保持原始 seed 机制，不要只按 oracle 判断。expected={expected}, "
        f"observed={observed}. Seed pattern: {pattern}"
    )


def main() -> int:
    selected = {
        row["Case ID"]: row
        for row in read_csv(EXPERIMENTS / "selected_30_drivefuzz_seeds.csv")
    }
    candidate_jsons = sorted(
        path for path in PSSD_JSON.glob("case_*__Round5_*.json") if path.is_file()
    )
    if len(candidate_jsons) != 36:
        raise RuntimeError(f"Expected 36 Round 5 JSON files, found {len(candidate_jsons)}")

    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    MISSING_DIR.mkdir(parents=True, exist_ok=True)
    review_rows: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    missing_rows: list[dict[str, Any]] = []

    for sequence, candidate_json in enumerate(candidate_jsons, start=1):
        review_id = f"{sequence:03d}"
        case_id, suffix = candidate_json.stem.split("__Round5_")
        candidate_index = int(suffix)
        candidate = f"Round5_{candidate_index:02d}"
        run_dir = PSSD_RUNS / candidate_json.stem
        run_exists = run_dir.is_dir()
        seed = selected[case_id]
        expected = seed.get("Group", "")
        pattern = root_cause_pattern(case_id)
        spec = round5_spec(case_id, candidate_index)

        error_obj, error_path = first_json(run_dir / "errors") if run_exists else (None, "")
        score_obj, score_path = first_json(run_dir / "scores") if run_exists else (None, "")
        events = error_obj.get("events", {}) if isinstance(error_obj, dict) else {}
        events = events if isinstance(events, dict) else {}
        observed = "+".join(code for key, code in EVENT_ORDER if events.get(key) is True)
        oracle_match = phase3.compare_expected_observed(
            set(expected.split("+")) if expected else set(),
            set(observed.split("+")) if observed else set(),
        )

        bag_files = sorted((run_dir / "rosbags").glob("*.bag")) if run_exists else []
        score_files = sorted((run_dir / "scores").glob("*.json")) if run_exists else []
        camera_files = sorted(
            p for p in (run_dir / "camera").glob("*.mp4") if not p.name.startswith("._")
        ) if run_exists else []
        status = phase3.classify(
            json_ok=candidate_json.exists(),
            run_exists=run_exists,
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
                "round": 5,
                "model": MODEL,
                "candidate": candidate,
                "expected_oracle_codes": expected,
                "observed_oracle_codes": observed,
                "oracle_match_status": oracle_match,
                "execution_status": status,
                "preliminary_category": category,
                "expected_root_cause_pattern": pattern,
                "round5_high_level_variant": spec.get("high_level_variant", ""),
                "round5_mutation_intent": spec.get("mutation_intent", ""),
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

    write_csv(REVIEW_CSV, review_rows, list(review_rows[0]))
    write_csv(MANIFEST_CSV, manifest_rows, list(manifest_rows[0]))
    write_csv(MISSING_CSV, missing_rows, list(missing_rows[0]))
    (OUTPUT_ROOT / "README.txt").write_text(
        "Round 5 manual review package\n\n"
        "Open review_checklist.xlsx and the videos folder. Video filenames use the same review_id as the worksheet.\n"
        "Fill manual_preservation_result with strictly preserved, partial or boundary, or not preserved.\n"
        "Fill manual_failure_type, manual_checked=yes, and manual_notes when useful.\n"
        "This is the final planned feedback round. After review, freeze RQ4 results; do not create Round 6.\n",
        encoding="utf-8",
    )
    print(f"review_rows={len(review_rows)}")
    print(f"video_files={len(manifest_rows)}")
    print(f"missing_candidates={len(missing_rows)}")
    print(REVIEW_CSV)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
