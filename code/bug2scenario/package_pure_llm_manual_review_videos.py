#!/usr/bin/env python3
"""Package Pure-LLM review-pool videos onto PSSD for manual inspection."""

from __future__ import annotations

import csv
import shutil
from pathlib import Path


PROJECT_ROOT = Path("<WORKSPACE_ROOT>")
PSSD_REVIEW_ROOT = Path("<PSSD_ROOT>/PURE_LLM_MANUAL_REVIEW_VIDEOS")
EXECUTION_CSV = PROJECT_ROOT / "processed" / "experiments" / "pure_llm_execution_review" / "pure_llm_phase3_execution_results.csv"

MODEL_SHORT = {
    "ark-deepseek-r1-250528": "deepseek",
    "ark-doubao-seed-2.0-lite-260215": "doubao",
    "claude-sonnet-4-5": "claude",
    "gemini-2.5-pro": "gemini",
    "gpt-4o-2024-11-20": "gpt4o",
    "gpt-5.1": "gpt51",
}


def safe_token(text: str, limit: int = 40) -> str:
    keep = []
    for ch in text:
        if ch.isalnum() or ch in "._+-":
            keep.append(ch)
        else:
            keep.append("_")
    out = "".join(keep).strip("_")
    return out[:limit] or "unknown"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    rows = read_rows(EXECUTION_CSV)
    review = [row for row in rows if row["post_execution_category_prelim"] == "needs same-root-cause review"]

    videos_dir = PSSD_REVIEW_ROOT / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)

    for old in videos_dir.glob("*.mp4"):
        old.unlink()

    review_rows: list[dict[str, str]] = []
    manifest_rows: list[dict[str, str]] = []
    missing_rows: list[dict[str, str]] = []

    for idx, row in enumerate(review, start=1):
        candidate = row["candidate_id"]
        case_id = row["case_id"]
        model = row["model"]
        model_short = MODEL_SHORT.get(model, safe_token(model, 18))
        exp = row["expected_oracle_codes"] or "none"
        obs = row["observed_oracle_codes"] or "none"
        match = row["oracle_match_status"]
        run_dir = Path(row["run_dir"])
        local_paths: dict[str, str] = {"front": "", "rear": ""}

        for src in sorted((run_dir / "camera").glob("*.mp4")):
            view = "front" if src.name.endswith("-front.mp4") else "rear" if src.name.endswith("-rear.mp4") else "view"
            dst_name = (
                f"pure_review_{idx:03d}__{case_id}__{model_short}__"
                f"exp={safe_token(exp, 12)}_obs={safe_token(obs, 12)}__{safe_token(match, 24)}__{view}.mp4"
            )
            dst = videos_dir / dst_name
            shutil.copy2(src, dst)
            local_paths[view] = str(dst)
            manifest_rows.append(
                {
                    "review_id": f"pure_review_{idx:03d}",
                    "candidate_id": candidate,
                    "case_id": case_id,
                    "model": model,
                    "view": view,
                    "source_path": str(src),
                    "review_video_path": str(dst),
                }
            )

        if not local_paths["front"] or not local_paths["rear"]:
            missing_rows.append(
                {
                    "review_id": f"pure_review_{idx:03d}",
                    "candidate_id": candidate,
                    "case_id": case_id,
                    "model": model,
                    "camera_count": row["camera_count"],
                    "run_dir": row["run_dir"],
                }
            )

        review_rows.append(
            {
                "review_id": f"pure_review_{idx:03d}",
                "candidate_id": candidate,
                "case_id": case_id,
                "model": model,
                "seed_group": row["seed_group"],
                "expected_oracle_codes": row["expected_oracle_codes"],
                "observed_oracle_codes": row["observed_oracle_codes"],
                "oracle_match_status": match,
                "execution_status": row["execution_status"],
                "post_execution_category_prelim": row["post_execution_category_prelim"],
                "bag_count": row["bag_count"],
                "score_count": row["score_count"],
                "camera_count": row["camera_count"],
                "event_crash": row["event_crash"],
                "event_stuck": row["event_stuck"],
                "event_lane_invasion": row["event_lane_invasion"],
                "event_red": row["event_red"],
                "event_other": row["event_other"],
                "num_frames": row["num_frames"],
                "elapsed_time": row["elapsed_time"],
                "front_video": local_paths["front"],
                "rear_video": local_paths["rear"],
                "run_dir": row["run_dir"],
                "manual_same_root_cause": "",
                "manual_failure_type": "",
                "manual_confidence": "",
                "manual_checked": "",
                "manual_notes": "",
            }
        )

    review_fields = [
        "review_id",
        "candidate_id",
        "case_id",
        "model",
        "seed_group",
        "expected_oracle_codes",
        "observed_oracle_codes",
        "oracle_match_status",
        "execution_status",
        "post_execution_category_prelim",
        "bag_count",
        "score_count",
        "camera_count",
        "event_crash",
        "event_stuck",
        "event_lane_invasion",
        "event_red",
        "event_other",
        "num_frames",
        "elapsed_time",
        "front_video",
        "rear_video",
        "run_dir",
        "manual_same_root_cause",
        "manual_failure_type",
        "manual_confidence",
        "manual_checked",
        "manual_notes",
    ]
    manifest_fields = ["review_id", "candidate_id", "case_id", "model", "view", "source_path", "review_video_path"]
    missing_fields = ["review_id", "candidate_id", "case_id", "model", "camera_count", "run_dir"]

    write_csv(PSSD_REVIEW_ROOT / "pure_llm_manual_review_table.csv", review_rows, review_fields)
    write_csv(PSSD_REVIEW_ROOT / "video_manifest.csv", manifest_rows, manifest_fields)
    write_csv(PSSD_REVIEW_ROOT / "missing_videos.csv", missing_rows, missing_fields)

    (PSSD_REVIEW_ROOT / "README.txt").write_text(
        "\n".join(
            [
                "Pure-LLM manual review video package",
                "",
                "Contents:",
                "- videos/: front/rear mp4 files for Pure-LLM root-cause review pool.",
                "- pure_llm_manual_review_table.csv: one row per candidate for manual labels.",
                "- video_manifest.csv: one row per copied video.",
                "- missing_videos.csv: candidates missing front or rear video.",
                "",
                "Manual columns:",
                "- manual_same_root_cause: yes / no / uncertain.",
                "- manual_failure_type: short label such as same_collision, different_red_light, no_failure, invalid.",
                "- manual_confidence: high / medium / low.",
                "- manual_checked: yes after inspection.",
                "- manual_notes: short reason.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(PSSD_REVIEW_ROOT)
    print(f"review_candidates={len(review_rows)}")
    print(f"copied_videos={len(manifest_rows)}")
    print(f"missing_video_candidates={len(missing_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
