#!/usr/bin/env python3
"""Build a 360-row manual review table for Phase 3 candidates.

This creates a reviewer-facing CSV with all candidates, automatic parsing
signals, and empty manual-label columns. It does not modify PSSD artifacts.
"""

from __future__ import annotations

import csv
from pathlib import Path


PROJECT_ROOT = Path("<WORKSPACE_ROOT>")
PREBATCH_DIR = PROJECT_ROOT / "processed" / "experiments" / "main_evaluation_prebatch"
INPUT_CSV = PREBATCH_DIR / "phase3_execution_results_prebatch.csv"
OUTPUT_CSV = PREBATCH_DIR / "phase3_360_manual_review_table.csv"
README = PREBATCH_DIR / "phase3_360_manual_review_table_README.md"


MODEL_ORDER = [
    "ark-deepseek-r1-250528",
    "ark-doubao-seed-2.0-lite-260215",
    "claude-sonnet-4-5",
    "gemini-2.5-pro",
    "gpt-4o-2024-11-20",
    "gpt-5.1",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def boolish_count(row: dict[str, str], key: str) -> int:
    try:
        return int(float(row.get(key, "0") or 0))
    except ValueError:
        return 0


def auto_needs_manual(row: dict[str, str]) -> str:
    priority = row.get("review_priority", "")
    status = row.get("execution_status", "")
    if priority in {
        "high_priority_same_root_cause_review",
        "medium_priority_partial_match_review",
        "different_failure_or_manual_check",
        "manual_review_hang_or_stuck",
        "likely_no_failure_check_trace",
    }:
        return "yes"
    if status in {"invalid_scenario_spawn_failure", "partial_artifacts_no_oracle"}:
        return "optional"
    return "no"


def default_manual_category(row: dict[str, str]) -> str:
    status = row.get("execution_status", "")
    priority = row.get("review_priority", "")
    prelim = row.get("post_execution_category_prelim", "")
    if status == "invalid_scenario_spawn_failure":
        return "invalid scenario"
    if status == "no_failure_reached_goal":
        return "no-failure scenario"
    if status == "execution_hang":
        return "unknown"
    if priority == "different_failure_or_manual_check":
        return "different-failure scenario"
    if priority == "high_priority_same_root_cause_review":
        return "needs review"
    if priority == "medium_priority_partial_match_review":
        return "needs review"
    if prelim:
        return prelim
    return "needs review"


def default_loop2_action(row: dict[str, str]) -> str:
    status = row.get("execution_status", "")
    priority = row.get("review_priority", "")
    if status == "invalid_scenario_spawn_failure":
        return "repair_and_regenerate"
    if status == "execution_hang":
        return "regenerate_with_constraints"
    if priority == "different_failure_or_manual_check":
        return "regenerate_with_stricter_oracle_match"
    if priority == "high_priority_same_root_cause_review":
        return "keep_as_positive_if_confirmed"
    if priority == "medium_priority_partial_match_review":
        return "review_then_decide"
    if status == "no_failure_reached_goal":
        return "optional_regenerate"
    return "review_then_decide"


def case_sort_key(row: dict[str, str]) -> tuple[int, int, int]:
    case_id = row["case_id"].replace("case_", "")
    model = row["model"]
    cand = row["candidate_index"].replace("cand_", "")
    return (int(case_id), MODEL_ORDER.index(model) if model in MODEL_ORDER else 99, int(cand))


def main() -> int:
    rows = read_csv(INPUT_CSV)
    rows.sort(key=case_sort_key)

    output_fields = [
        "review_id",
        "global_candidate_index",
        "candidate_id",
        "case_id",
        "seed_group",
        "model",
        "candidate_index",
        "expected_oracle_codes",
        "observed_oracle_codes",
        "oracle_match_status",
        "auto_execution_status",
        "auto_prelim_category",
        "auto_review_priority",
        "auto_needs_manual_review",
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
        "rerun_23_observed_issue",
        "suggested_next_action",
        "root_cause_pattern_summary",
        "run_dir",
        "manual_final_category",
        "manual_same_root_cause",
        "manual_failure_type",
        "manual_confidence",
        "manual_checked",
        "manual_reviewer",
        "manual_notes",
        "loop2_action",
        "loop2_feedback_for_llm",
    ]

    out_rows: list[dict[str, str]] = []
    for i, row in enumerate(rows, start=1):
        out_rows.append(
            {
                "review_id": f"review_{i:03d}",
                "global_candidate_index": str(i),
                "candidate_id": row.get("candidate_id", ""),
                "case_id": row.get("case_id", ""),
                "seed_group": row.get("seed_group", ""),
                "model": row.get("model", ""),
                "candidate_index": row.get("candidate_index", ""),
                "expected_oracle_codes": row.get("expected_oracle_codes", ""),
                "observed_oracle_codes": row.get("observed_oracle_codes", ""),
                "oracle_match_status": row.get("oracle_match_status", ""),
                "auto_execution_status": row.get("execution_status", ""),
                "auto_prelim_category": row.get("post_execution_category_prelim", ""),
                "auto_review_priority": row.get("review_priority", ""),
                "auto_needs_manual_review": auto_needs_manual(row),
                "bag_count": str(boolish_count(row, "bag_count")),
                "score_count": str(boolish_count(row, "score_count")),
                "camera_count": str(boolish_count(row, "camera_count")),
                "event_crash": str(row.get("event_crash", "")),
                "event_stuck": str(row.get("event_stuck", "")),
                "event_lane_invasion": str(row.get("event_lane_invasion", "")),
                "event_red": str(row.get("event_red", "")),
                "event_other": str(row.get("event_other", "")),
                "num_frames": str(row.get("num_frames", "")),
                "elapsed_time": str(row.get("elapsed_time", "")),
                "rerun_23_observed_issue": row.get("rerun_23_observed_issue", ""),
                "suggested_next_action": row.get("suggested_next_action", ""),
                "root_cause_pattern_summary": row.get("root_cause_pattern_summary", ""),
                "run_dir": row.get("run_dir", ""),
                "manual_final_category": default_manual_category(row),
                "manual_same_root_cause": "",
                "manual_failure_type": "",
                "manual_confidence": "",
                "manual_checked": "no",
                "manual_reviewer": "",
                "manual_notes": "",
                "loop2_action": default_loop2_action(row),
                "loop2_feedback_for_llm": "",
            }
        )

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(out_rows)

    with README.open("w", encoding="utf-8") as f:
        f.write("# Phase 3 360-Row Manual Review Table\n\n")
        f.write("This table lists every Phase 3 candidate exactly once. It is intended for human post-execution classification before the next LLM regeneration loop.\n\n")
        f.write("## Manual Columns\n\n")
        f.write("- `manual_final_category`: choose one of `same-root-cause failure`, `different-failure scenario`, `no-failure scenario`, `invalid scenario`, or `unknown`.\n")
        f.write("- `manual_same_root_cause`: use `yes`, `no`, or `uncertain`.\n")
        f.write("- `manual_failure_type`: use C/S/L/R combinations or a short free-text type.\n")
        f.write("- `manual_confidence`: use high/medium/low.\n")
        f.write("- `manual_checked`: set to yes after review.\n")
        f.write("- `manual_notes`: write the human evidence judgment.\n")
        f.write("- `loop2_action`: decide whether to keep, repair, regenerate, or discard for the next LLM loop.\n")
        f.write("- `loop2_feedback_for_llm`: short instruction to feed into the next generation prompt.\n\n")
        f.write("## Output\n\n")
        f.write(f"- CSV: `{OUTPUT_CSV}`\n")

    print(OUTPUT_CSV)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

