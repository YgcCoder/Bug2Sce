#!/usr/bin/env python3
"""Build a complete 180-candidate Pure-LLM manual-review package locally.

Unlike the earlier 72-candidate review-pool package, this package retains every
executed candidate, including no-oracle, no-failure, different-failure, crash,
and invalid outcomes. Existing PSSD artifacts are read-only inputs.
"""

from __future__ import annotations

import csv
import os
import shutil
from pathlib import Path


PROJECT_ROOT = Path("<WORKSPACE_ROOT>")
EXECUTION_CSV = (
    PROJECT_ROOT
    / "processed"
    / "experiments"
    / "pure_llm_execution_review"
    / "pure_llm_phase3_execution_results.csv"
)
OLD_72_ROOT = Path("<WORKSPACE_ROOT>/pure_llm_videos")
OUTPUT_ROOT = Path("<WORKSPACE_ROOT>/pure_llm_all180_videos")

MODEL_SHORT = {
    "ark-deepseek-r1-250528": "deepseek",
    "ark-doubao-seed-2.0-lite-260215": "doubao",
    "claude-sonnet-4-5": "claude",
    "gemini-2.5-pro": "gemini",
    "gpt-4o-2024-11-20": "gpt4o",
    "gpt-5.1": "gpt51",
}

MANUAL_FIELDS = [
    "manual_same_root_cause",
    "manual_failure_type",
    "manual_confidence",
    "manual_checked",
    "manual_notes",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def safe_token(text: str, limit: int = 36) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "._+-=" else "_" for ch in text)
    return cleaned.strip("_")[:limit] or "none"


def existing_72_by_candidate() -> dict[str, dict[str, str]]:
    rows = read_rows(OLD_72_ROOT / "review_checklist.csv")
    return {row["candidate_id"]: row for row in rows}


def existing_manual_by_candidate() -> dict[str, dict[str, str]]:
    rows = read_rows(OUTPUT_ROOT / "review_checklist.csv")
    return {
        row["candidate_id"]: {field: row.get(field, "") for field in MANUAL_FIELDS}
        for row in rows
        if row.get("candidate_id")
    }


def decision_hint(row: dict[str, str]) -> str:
    category = row["post_execution_category_prelim"]
    if category == "needs same-root-cause review":
        return "查看前后视视频，判断是否与 seed 保持同一根因；不能只按 oracle 标签判断。"
    if category == "different failure":
        return "自动结果认为 failure 类型偏离；仍查看视频并记录人工判断。"
    if category == "invalid / crash":
        return "执行异常或证据极少；若无视频，按日志状态标 invalid/uncertain 并说明原因。"
    return "自动 oracle 未触发或证据不完整；仍查看视频，记录实际 failure、无 failure 或不确定。"


def link_or_copy(source: Path, destination: Path) -> None:
    if destination.exists():
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def main() -> int:
    execution_rows = read_rows(EXECUTION_CSV)
    if len(execution_rows) != 180:
        raise RuntimeError(f"Expected 180 execution rows, found {len(execution_rows)}")

    old_72 = existing_72_by_candidate()
    old_manual = existing_manual_by_candidate()
    videos_dir = OUTPUT_ROOT / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)

    review_rows: list[dict[str, str]] = []
    manifest_rows: list[dict[str, str]] = []
    missing_rows: list[dict[str, str]] = []

    for index, row in enumerate(execution_rows, start=1):
        review_id = f"{index:03d}"
        candidate_id = row["candidate_id"]
        model_short = MODEL_SHORT.get(row["model"], safe_token(row["model"], 18))
        expected = row["expected_oracle_codes"] or "none"
        observed = row["observed_oracle_codes"] or "none"
        match = row["oracle_match_status"] or "unknown"
        local_paths = {"front": "", "rear": ""}

        sources: dict[str, Path] = {}
        prior = old_72.get(candidate_id, {})
        for view in ("front", "rear"):
            prior_path = Path(prior.get(f"{view}_video", "")) if prior.get(f"{view}_video") else None
            if prior_path and prior_path.exists():
                sources[view] = prior_path

        run_camera = Path(row["run_dir"]) / "camera"
        for source in sorted(run_camera.glob("*.mp4")):
            if source.name.startswith("._"):
                continue
            if source.name.endswith("-front.mp4"):
                sources.setdefault("front", source)
            elif source.name.endswith("-rear.mp4"):
                sources.setdefault("rear", source)

        for view in ("front", "rear"):
            source = sources.get(view)
            if not source:
                continue
            filename = (
                f"review_{review_id}__{row['case_id']}__model_{model_short}__cand_001__"
                f"exp={safe_token(expected, 12)}_obs={safe_token(observed, 12)}__"
                f"{safe_token(match, 28)}__{view}.mp4"
            )
            destination = videos_dir / filename
            link_or_copy(source, destination)
            local_paths[view] = str(destination)
            manifest_rows.append(
                {
                    "review_id": review_id,
                    "candidate_id": candidate_id,
                    "case_id": row["case_id"],
                    "model": row["model"],
                    "view": view,
                    "source_path": str(source),
                    "local_video_path": str(destination),
                }
            )

        if not local_paths["front"] or not local_paths["rear"]:
            missing_rows.append(
                {
                    "review_id": review_id,
                    "candidate_id": candidate_id,
                    "case_id": row["case_id"],
                    "model": row["model"],
                    "execution_status": row["execution_status"],
                    "post_execution_category_prelim": row["post_execution_category_prelim"],
                    "camera_count": row["camera_count"],
                    "run_dir": row["run_dir"],
                }
            )

        manual = old_manual.get(candidate_id, {field: "" for field in MANUAL_FIELDS})
        review_rows.append(
            {
                "review_id": review_id,
                "candidate_id": candidate_id,
                "case_id": row["case_id"],
                "model": row["model"],
                "candidate": row["candidate_index"],
                "seed_group": row["seed_group"],
                "expected_oracle_codes": row["expected_oracle_codes"],
                "observed_oracle_codes": row["observed_oracle_codes"],
                "oracle_match_status": row["oracle_match_status"],
                "execution_status": row["execution_status"],
                "post_execution_category_prelim": row["post_execution_category_prelim"],
                "decision_hint_zh": decision_hint(row),
                "json_parse_ok": row["json_parse_ok"],
                "run_output_exists": row["run_output_exists"],
                "bag_count": row["bag_count"],
                "score_count": row["score_count"],
                "camera_count": row["camera_count"],
                "event_crash": row["event_crash"],
                "event_stuck": row["event_stuck"],
                "event_lane_invasion": row["event_lane_invasion"],
                "event_red": row["event_red"],
                "event_speeding": row["event_speeding"],
                "event_other": row["event_other"],
                "num_frames": row["num_frames"],
                "elapsed_time": row["elapsed_time"],
                "front_video": local_paths["front"],
                "rear_video": local_paths["rear"],
                "run_dir": row["run_dir"],
                **manual,
            }
        )

    review_fields = list(review_rows[0])
    manifest_fields = list(manifest_rows[0])
    missing_fields = list(missing_rows[0])
    write_rows(OUTPUT_ROOT / "review_checklist.csv", review_rows, review_fields)
    write_rows(OUTPUT_ROOT / "video_manifest.csv", manifest_rows, manifest_fields)
    write_rows(OUTPUT_ROOT / "missing_videos.csv", missing_rows, missing_fields)

    (OUTPUT_ROOT / "README.txt").write_text(
        "\n".join(
            [
                "Pure-LLM complete 180-candidate manual review package",
                "",
                "This package includes all 180 executed candidates, not only the 72-item automatic review pool.",
                f"Candidates: {len(review_rows)}",
                f"Copied or linked videos: {len(manifest_rows)}",
                f"Candidates without a complete front/rear pair: {len(missing_rows)}",
                "",
                "Workflow: inspect both views, fill the five manual_* columns, save, then delete only the local pair.",
                "PSSD execution artifacts are source evidence and must not be deleted.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"output={OUTPUT_ROOT}")
    print(f"review_rows={len(review_rows)}")
    print(f"video_files={len(manifest_rows)}")
    print(f"missing_candidates={len(missing_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
