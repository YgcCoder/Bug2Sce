#!/usr/bin/env python3
"""Pre-batch parser for Bug2Scenario Phase 3 execution outputs.

This script is intentionally separate from earlier Phase 3 scripts. It reads the
current PSSD outputs and creates conservative CSV/Markdown artifacts for:

- execution result parsing
- expected-vs-observed oracle comparison
- same-root-cause review triage
- repair/rerun candidate selection

It does not modify B2S_JSON, B2S_RUNS, or prior processed outputs.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_PROJECT_ROOT = Path("<WORKSPACE_ROOT>")
DEFAULT_PSSD_ROOT = Path("<PSSD_ROOT>")

LABEL_COLUMNS = ["Collision", "Stuck", "Lane Invasion", "Red"]
LABEL_TO_CODE = {
    "Collision": "C",
    "Stuck": "S",
    "Lane Invasion": "L",
    "Red": "R",
}
EVENT_TO_CODE = {
    "crash": "C",
    "stuck": "S",
    "lane_invasion": "L",
    "red": "R",
}
CANDIDATE_RE = re.compile(r"case_(\d+)__model_(.+)__cand_(\d+)$")


@dataclass(frozen=True)
class SeedLabel:
    case_id: str
    index: str
    group: str
    expected_codes: set[str]
    rationale: str


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def safe_json_load(path: Path) -> tuple[dict[str, Any] | list[Any] | None, str]:
    try:
        with path.open(encoding="utf-8") as f:
            return json.load(f), ""
    except Exception as exc:  # noqa: BLE001 - audit output should capture any parse failure.
        return None, str(exc)


def expected_codes_from_row(row: dict[str, str]) -> set[str]:
    codes: set[str] = set()
    for label in LABEL_COLUMNS:
        try:
            val = int(float(row.get(label, "0") or 0))
        except ValueError:
            val = 0
        if val:
            codes.add(LABEL_TO_CODE[label])
    return codes


def load_seed_labels(path: Path) -> dict[str, SeedLabel]:
    rows = read_csv_rows(path)
    out: dict[str, SeedLabel] = {}
    for row in rows:
        case_id = row.get("Case ID") or f"case_{int(float(row['Index'])):03d}"
        index = str(int(float(row.get("Index", "0"))))
        out[case_id] = SeedLabel(
            case_id=case_id,
            index=index,
            group=str(row.get("Group", "")),
            expected_codes=expected_codes_from_row(row),
            rationale=str(row.get("Selection Rationale", "")),
        )
    return out


def load_rerun_audit(path: Path) -> dict[str, dict[str, str]]:
    return {row["candidate"]: row for row in read_csv_rows(path) if row.get("candidate")}


def load_phase2_rows(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    out: dict[tuple[str, str], dict[str, str]] = {}
    for row in read_csv_rows(path):
        case_id = row.get("case_id", "")
        if case_id and not case_id.startswith("case_"):
            case_id = f"case_{int(case_id):03d}"
        model = row.get("model_name", "")
        out[(case_id, model)] = row
    return out


def load_root_cause_patterns(phase1_dir: Path) -> dict[tuple[str, str], str]:
    patterns: dict[tuple[str, str], str] = {}
    for path in phase1_dir.glob("case_*__*.json"):
        stem = path.stem
        if "__" not in stem:
            continue
        case_id, model = stem.split("__", 1)
        obj, err = safe_json_load(path)
        if err or not isinstance(obj, dict):
            continue
        parsed = obj.get("parsed_response")
        if isinstance(parsed, dict):
            pattern = parsed.get("root_cause_pattern") or parsed.get("possible_root_cause_pattern") or ""
        else:
            pattern = ""
        if pattern:
            patterns[(case_id, model)] = one_line(str(pattern), 360)
    return patterns


def one_line(text: str, limit: int = 240) -> str:
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def file_count(path: Path) -> int:
    if not path.is_dir():
        return 0
    return sum(1 for p in path.rglob("*") if p.is_file())


def allocated_size_kb(path: Path) -> int:
    if not path.is_dir():
        return 0
    total = 0
    for p in path.rglob("*"):
        if p.is_file():
            try:
                total += p.stat().st_blocks * 512
            except OSError:
                pass
    return total // 1024


def first_json_in(path: Path) -> tuple[dict[str, Any] | None, str, str]:
    files = sorted(path.glob("*.json")) if path.is_dir() else []
    if not files:
        return None, "", ""
    obj, err = safe_json_load(files[0])
    return obj if isinstance(obj, dict) else None, str(files[0]), err


def parse_candidate_name(candidate_id: str) -> tuple[str, str, str]:
    match = CANDIDATE_RE.fullmatch(candidate_id)
    if not match:
        return "case_unknown", "unknown", "unknown"
    case_num, model, cand_num = match.groups()
    return f"case_{int(case_num):03d}", model, f"cand_{int(cand_num):03d}"


def observed_codes_from_events(events: dict[str, Any]) -> set[str]:
    codes = set()
    for event_key, code in EVENT_TO_CODE.items():
        if events.get(event_key) is True:
            codes.add(code)
    return codes


def compare_expected_observed(expected: set[str], observed: set[str]) -> str:
    if not observed:
        return "no_observed_oracle"
    if observed == expected:
        return "exact_oracle_match"
    if expected and expected.issubset(observed):
        return "observed_superset_contains_expected"
    if observed & expected:
        return "partial_oracle_overlap"
    return "different_oracle_symptom"


def classify_execution(
    *,
    json_ok: bool,
    run_exists: bool,
    rerun_status: str,
    observed_codes: set[str],
    has_bag: bool,
    has_score: bool,
    has_camera: bool,
    has_error_json: bool,
    event_other: str,
) -> str:
    if not json_ok:
        return "invalid_json_syntax"
    if not run_exists:
        return "missing_execution_output"
    if "spawn_failure" in rerun_status:
        return "invalid_scenario_spawn_failure"
    if "hang" in rerun_status:
        return "execution_hang"
    if observed_codes:
        return "oracle_triggered"
    if has_error_json and event_other == "goal":
        return "no_failure_reached_goal"
    if has_bag and has_error_json:
        return "trace_ready_no_oracle"
    if has_score or has_camera:
        return "partial_artifacts_no_oracle"
    return "minimal_artifacts_unknown"


def root_cause_review_priority(execution_status: str, oracle_match: str, has_bag: bool) -> str:
    if execution_status == "invalid_scenario_spawn_failure":
        return "repair_or_count_invalid"
    if execution_status == "execution_hang":
        return "manual_review_hang_or_stuck"
    if execution_status == "oracle_triggered":
        if oracle_match in {"exact_oracle_match", "observed_superset_contains_expected"}:
            return "high_priority_same_root_cause_review"
        if oracle_match == "partial_oracle_overlap":
            return "medium_priority_partial_match_review"
        return "different_failure_or_manual_check"
    if execution_status in {"no_failure_reached_goal", "trace_ready_no_oracle"}:
        return "likely_no_failure_check_trace"
    if has_bag:
        return "trace_available_review"
    return "low_evidence_unknown"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=DEFAULT_PROJECT_ROOT)
    parser.add_argument("--pssd-root", type=Path, default=DEFAULT_PSSD_ROOT)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    project_root: Path = args.project_root
    pssd_root: Path = args.pssd_root
    output_dir: Path = args.output_dir or project_root / "processed" / "experiments" / "main_evaluation_prebatch"

    json_dir = pssd_root / "B2S_JSON"
    runs_dir = pssd_root / "B2S_RUNS"
    selected_path = project_root / "processed" / "experiments" / "selected_30_drivefuzz_seeds.csv"
    rerun_audit_path = project_root / "processed" / "experiments" / "phase3_rerun_23_audit.csv"
    phase2_path = project_root / "processed" / "experiments" / "phase2_generation_results.csv"
    phase1_dir = project_root / "processed" / "experiments" / "phase1_api_outputs"

    seed_labels = load_seed_labels(selected_path)
    rerun_audit = load_rerun_audit(rerun_audit_path)
    phase2_rows = load_phase2_rows(phase2_path)
    root_patterns = load_root_cause_patterns(phase1_dir)

    json_paths = sorted(json_dir.glob("*.json"))
    run_dirs = {p.name: p for p in runs_dir.iterdir() if p.is_dir()} if runs_dir.exists() else {}

    results: list[dict[str, Any]] = []
    for json_path in json_paths:
        candidate_id = json_path.stem
        case_id, model, candidate_index = parse_candidate_name(candidate_id)
        seed = seed_labels.get(case_id)
        expected_codes = seed.expected_codes if seed else set()
        expected_group = seed.group if seed else ""

        _, json_parse_error = safe_json_load(json_path)
        json_ok = not json_parse_error
        run_dir = run_dirs.get(candidate_id)
        run_exists = run_dir is not None

        if run_dir:
            bag_files = sorted((run_dir / "rosbags").glob("*.bag"))
            score_files = sorted((run_dir / "scores").glob("*.json"))
            camera_files = sorted((run_dir / "camera").glob("*.mp4"))
            queue_files = sorted((run_dir / "queue").glob("*.json"))
            cov_files = sorted((run_dir / "cov").glob("*.json"))
            error_obj, error_path, error_parse_error = first_json_in(run_dir / "errors")
        else:
            bag_files = score_files = camera_files = queue_files = cov_files = []
            error_obj, error_path, error_parse_error = None, "", ""

        score_obj, score_path, score_parse_error = first_json_in(run_dir / "scores") if run_dir else (None, "", "")
        events = error_obj.get("events", {}) if isinstance(error_obj, dict) else {}
        observed_codes = observed_codes_from_events(events if isinstance(events, dict) else {})
        event_other = str(events.get("other", "")) if isinstance(events, dict) else ""
        rerun = rerun_audit.get(candidate_id, {})
        rerun_status = rerun.get("status_before_final_parsing", "")

        execution_status = classify_execution(
            json_ok=json_ok,
            run_exists=run_exists,
            rerun_status=rerun_status,
            observed_codes=observed_codes,
            has_bag=bool(bag_files),
            has_score=bool(score_files),
            has_camera=bool(camera_files),
            has_error_json=bool(error_path),
            event_other=event_other,
        )
        oracle_match = compare_expected_observed(expected_codes, observed_codes)
        review_priority = root_cause_review_priority(execution_status, oracle_match, bool(bag_files))
        phase2 = phase2_rows.get((case_id, model), {})

        if execution_status == "invalid_scenario_spawn_failure":
            post_category_prelim = "invalid scenario"
        elif execution_status in {"no_failure_reached_goal", "trace_ready_no_oracle"}:
            post_category_prelim = "no-failure scenario"
        elif execution_status == "oracle_triggered" and oracle_match == "different_oracle_symptom":
            post_category_prelim = "different-failure scenario"
        elif execution_status == "oracle_triggered":
            post_category_prelim = "needs same-root-cause review"
        elif execution_status == "execution_hang":
            post_category_prelim = "unknown / hang"
        else:
            post_category_prelim = "unknown / incomplete evidence"

        score_summary = ""
        if isinstance(score_obj, dict):
            score_summary = "; ".join(f"{k}={v}" for k, v in score_obj.items())

        results.append(
            {
                "candidate_id": candidate_id,
                "case_id": case_id,
                "model": model,
                "candidate_index": candidate_index,
                "seed_group": expected_group,
                "expected_oracle_codes": "+".join(sorted(expected_codes)),
                "observed_oracle_codes": "+".join(sorted(observed_codes)),
                "oracle_match_status": oracle_match,
                "execution_status": execution_status,
                "post_execution_category_prelim": post_category_prelim,
                "review_priority": review_priority,
                "json_parse_ok": json_ok,
                "json_parse_error": json_parse_error,
                "run_output_exists": run_exists,
                "run_dir": str(run_dir) if run_dir else "",
                "size_kb": allocated_size_kb(run_dir) if run_dir else 0,
                "file_count": file_count(run_dir) if run_dir else 0,
                "bag_count": len(bag_files),
                "score_count": len(score_files),
                "camera_count": len(camera_files),
                "error_json_count": 1 if error_path else 0,
                "queue_json_count": len(queue_files),
                "cov_json_count": len(cov_files),
                "error_json_path": error_path,
                "error_json_parse_error": error_parse_error,
                "score_json_path": score_path,
                "score_json_parse_error": score_parse_error,
                "event_crash": events.get("crash", "") if isinstance(events, dict) else "",
                "event_stuck": events.get("stuck", "") if isinstance(events, dict) else "",
                "event_lane_invasion": events.get("lane_invasion", "") if isinstance(events, dict) else "",
                "event_red": events.get("red", "") if isinstance(events, dict) else "",
                "event_speeding": events.get("speeding", "") if isinstance(events, dict) else "",
                "event_other": event_other,
                "num_frames": error_obj.get("num_frames", "") if isinstance(error_obj, dict) else "",
                "elapsed_time": error_obj.get("elapsed_time", "") if isinstance(error_obj, dict) else "",
                "score_summary": score_summary,
                "phase2_status": phase2.get("status", ""),
                "phase2_schema_valid": phase2.get("schema_valid", ""),
                "phase2_num_pre_valid": phase2.get("num_pre_valid", ""),
                "phase1_ready": phase2.get("phase1_ready", ""),
                "root_cause_pattern_summary": root_patterns.get((case_id, model), ""),
                "rerun_23_status": rerun_status,
                "rerun_23_observed_issue": rerun.get("observed_issue", ""),
                "suggested_next_action": suggest_next_action(execution_status, oracle_match, review_priority),
            }
        )

    result_fields = list(results[0].keys()) if results else []
    write_csv(output_dir / "phase3_execution_results_prebatch.csv", results, result_fields)

    by_model = summarize_by(results, "model")
    by_case = summarize_by(results, "case_id")
    write_csv(output_dir / "phase3_summary_by_model_prebatch.csv", by_model)
    write_csv(output_dir / "phase3_summary_by_case_prebatch.csv", by_case)

    review_rows = [
        r
        for r in results
        if r["review_priority"]
        in {
            "high_priority_same_root_cause_review",
            "medium_priority_partial_match_review",
            "different_failure_or_manual_check",
            "manual_review_hang_or_stuck",
            "likely_no_failure_check_trace",
        }
    ]
    review_fields = [
        "candidate_id",
        "case_id",
        "model",
        "candidate_index",
        "seed_group",
        "expected_oracle_codes",
        "observed_oracle_codes",
        "oracle_match_status",
        "execution_status",
        "post_execution_category_prelim",
        "review_priority",
        "bag_count",
        "score_count",
        "camera_count",
        "event_other",
        "num_frames",
        "elapsed_time",
        "root_cause_pattern_summary",
        "suggested_next_action",
    ]
    write_csv(output_dir / "root_cause_review_sheet_prebatch.csv", review_rows, review_fields)

    repair_rows = [
        r
        for r in results
        if r["execution_status"] in {"invalid_scenario_spawn_failure", "missing_execution_output", "invalid_json_syntax"}
        or r["review_priority"] == "repair_or_count_invalid"
    ]
    repair_fields = [
        "candidate_id",
        "case_id",
        "model",
        "candidate_index",
        "seed_group",
        "execution_status",
        "rerun_23_observed_issue",
        "json_parse_ok",
        "run_output_exists",
        "suggested_next_action",
        "run_dir",
    ]
    write_csv(output_dir / "repair_or_rerun_candidates_prebatch.csv", repair_rows, repair_fields)

    write_report(output_dir / "phase3_prebatch_report.md", results, by_model, by_case, review_rows, repair_rows, output_dir)
    print(f"Wrote {output_dir}")
    return 0


def suggest_next_action(execution_status: str, oracle_match: str, review_priority: str) -> str:
    if execution_status == "invalid_json_syntax":
        return "repair JSON generation before rerun"
    if execution_status == "missing_execution_output":
        return "rerun candidate"
    if execution_status == "invalid_scenario_spawn_failure":
        return "repair actor placement or count as invalid scenario"
    if execution_status == "execution_hang":
        return "inspect score/camera; classify hang as stuck/no-failure/unknown before rerun"
    if execution_status == "oracle_triggered":
        if oracle_match in {"exact_oracle_match", "observed_superset_contains_expected"}:
            return "manual same-root-cause review using trace/root-cause pattern"
        if oracle_match == "partial_oracle_overlap":
            return "manual review; observed oracle only partially matches seed"
        return "likely different-failure; confirm manually"
    if execution_status in {"no_failure_reached_goal", "trace_ready_no_oracle"}:
        return "likely no-failure; confirm no oracle evidence"
    if review_priority == "low_evidence_unknown":
        return "low evidence; inspect artifacts or rerun if needed"
    return "parse available artifacts"


def summarize_by(results: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in results:
        groups[str(row[key])].append(row)
    out: list[dict[str, Any]] = []
    for group, rows in sorted(groups.items()):
        exec_counts = Counter(r["execution_status"] for r in rows)
        match_counts = Counter(r["oracle_match_status"] for r in rows)
        review_counts = Counter(r["review_priority"] for r in rows)
        out.append(
            {
                key: group,
                "total": len(rows),
                "json_valid": sum(1 for r in rows if r["json_parse_ok"]),
                "output_dirs": sum(1 for r in rows if r["run_output_exists"]),
                "has_rosbag": sum(1 for r in rows if int(r["bag_count"]) > 0),
                "has_score": sum(1 for r in rows if int(r["score_count"]) > 0),
                "has_camera": sum(1 for r in rows if int(r["camera_count"]) > 0),
                "oracle_triggered": exec_counts["oracle_triggered"],
                "exact_oracle_match": match_counts["exact_oracle_match"],
                "observed_superset_contains_expected": match_counts["observed_superset_contains_expected"],
                "partial_oracle_overlap": match_counts["partial_oracle_overlap"],
                "different_oracle_symptom": match_counts["different_oracle_symptom"],
                "no_observed_oracle": match_counts["no_observed_oracle"],
                "spawn_failure": exec_counts["invalid_scenario_spawn_failure"],
                "execution_hang": exec_counts["execution_hang"],
                "no_failure_reached_goal": exec_counts["no_failure_reached_goal"],
                "trace_ready_no_oracle": exec_counts["trace_ready_no_oracle"],
                "partial_artifacts_no_oracle": exec_counts["partial_artifacts_no_oracle"],
                "high_priority_review": review_counts["high_priority_same_root_cause_review"],
                "medium_priority_review": review_counts["medium_priority_partial_match_review"],
                "different_failure_review": review_counts["different_failure_or_manual_check"],
                "hang_review": review_counts["manual_review_hang_or_stuck"],
            }
        )
    return out


def pct(num: int, den: int) -> str:
    if den == 0:
        return "0.0%"
    return f"{num / den:.1%}"


def write_report(
    path: Path,
    results: list[dict[str, Any]],
    by_model: list[dict[str, Any]],
    by_case: list[dict[str, Any]],
    review_rows: list[dict[str, Any]],
    repair_rows: list[dict[str, Any]],
    output_dir: Path,
) -> None:
    total = len(results)
    exec_counts = Counter(r["execution_status"] for r in results)
    match_counts = Counter(r["oracle_match_status"] for r in results)
    category_counts = Counter(r["post_execution_category_prelim"] for r in results)
    review_counts = Counter(r["review_priority"] for r in results)
    now = datetime.now(timezone.utc).isoformat()

    with path.open("w", encoding="utf-8") as f:
        f.write("# Phase 3 Pre-Batch Parsing Report\n\n")
        f.write(f"Generated: {now}\n\n")
        f.write("This report is generated by `scripts/phase3_prebatch_parse_results.py`. It does not modify prior scripts or PSSD artifacts.\n\n")
        f.write("## Headline\n\n")
        f.write(f"- Total candidates: {total}\n")
        f.write(f"- JSON-valid candidates: {sum(1 for r in results if r['json_parse_ok'])} / {total} ({pct(sum(1 for r in results if r['json_parse_ok']), total)})\n")
        f.write(f"- Execution output directories: {sum(1 for r in results if r['run_output_exists'])} / {total} ({pct(sum(1 for r in results if r['run_output_exists']), total)})\n")
        f.write(f"- Candidates with rosbag: {sum(1 for r in results if int(r['bag_count']) > 0)} / {total}\n")
        f.write(f"- Candidates with score JSON: {sum(1 for r in results if int(r['score_count']) > 0)} / {total}\n")
        f.write(f"- Candidates with camera videos: {sum(1 for r in results if int(r['camera_count']) > 0)} / {total}\n")
        f.write(f"- Candidates needing same-root-cause/manual review: {len(review_rows)}\n")
        f.write(f"- Candidates for repair/rerun consideration: {len(repair_rows)}\n\n")

        f.write("## Execution Status Counts\n\n")
        f.write("| Status | Count | Ratio |\n|---|---:|---:|\n")
        for status, count in exec_counts.most_common():
            f.write(f"| {status} | {count} | {pct(count, total)} |\n")

        f.write("\n## Expected-vs-Observed Oracle Match\n\n")
        f.write("| Match status | Count | Ratio |\n|---|---:|---:|\n")
        for status, count in match_counts.most_common():
            f.write(f"| {status} | {count} | {pct(count, total)} |\n")

        f.write("\n## Preliminary Post-Execution Categories\n\n")
        f.write("| Category | Count | Ratio |\n|---|---:|---:|\n")
        for status, count in category_counts.most_common():
            f.write(f"| {status} | {count} | {pct(count, total)} |\n")

        f.write("\n## Review Priority Counts\n\n")
        f.write("| Review priority | Count | Ratio |\n|---|---:|---:|\n")
        for status, count in review_counts.most_common():
            f.write(f"| {status} | {count} | {pct(count, total)} |\n")

        f.write("\n## Model Summary\n\n")
        model_fields = [
            "model",
            "total",
            "oracle_triggered",
            "exact_oracle_match",
            "observed_superset_contains_expected",
            "partial_oracle_overlap",
            "different_oracle_symptom",
            "spawn_failure",
            "execution_hang",
            "high_priority_review",
        ]
        f.write("| " + " | ".join(model_fields) + " |\n")
        f.write("|" + "|".join(["---"] + ["---:"] * (len(model_fields) - 1)) + "|\n")
        for row in by_model:
            f.write("| " + " | ".join(str(row.get(k, "")) for k in model_fields) + " |\n")

        f.write("\n## Files\n\n")
        for name in [
            "phase3_execution_results_prebatch.csv",
            "phase3_summary_by_model_prebatch.csv",
            "phase3_summary_by_case_prebatch.csv",
            "root_cause_review_sheet_prebatch.csv",
            "repair_or_rerun_candidates_prebatch.csv",
        ]:
            f.write(f"- `{output_dir / name}`\n")

        f.write("\n## Recommended Next Step\n\n")
        f.write("Do not launch broad API or simulator reruns yet. First inspect `root_cause_review_sheet_prebatch.csv` and `repair_or_rerun_candidates_prebatch.csv`. ")
        f.write("The former is the candidate pool for same-root-cause labeling; the latter is the small set that may need actor-placement repair or targeted rerun.\n")


if __name__ == "__main__":
    raise SystemExit(main())
