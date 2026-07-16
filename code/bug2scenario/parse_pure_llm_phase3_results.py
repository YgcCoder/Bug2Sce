#!/usr/bin/env python3
"""Parse Pure-LLM Phase 3 DriveFuzz execution outputs.

This script is read-only with respect to PSSD. It audits the Pure-LLM baseline
run directories and writes local CSV/Markdown summaries for the RQ3 comparison.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("<WORKSPACE_ROOT>")
PSSD_ROOT = Path("<PSSD_ROOT>")

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
PURE_RE = re.compile(r"case_(\d+)__model_(.+)__cand_(\d+)$")


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = fieldnames or (list(rows[0].keys()) if rows else [])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def safe_json(path: Path) -> tuple[dict[str, Any] | None, str]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)
    return obj if isinstance(obj, dict) else None, ""


def first_json(path: Path) -> tuple[dict[str, Any] | None, str, str]:
    files = sorted(path.glob("*.json")) if path.is_dir() else []
    if not files:
        return None, "", ""
    obj, err = safe_json(files[0])
    return obj, str(files[0]), err


def parse_name(stem: str) -> tuple[str, str, str]:
    match = PURE_RE.fullmatch(stem)
    if not match:
        return "case_unknown", "unknown", "unknown"
    case_num, model, cand_num = match.groups()
    return f"case_{int(case_num):03d}", model, f"cand_{int(cand_num):03d}"


def expected_codes(row: dict[str, str]) -> set[str]:
    out: set[str] = set()
    for col in LABEL_COLUMNS:
        try:
            val = int(float(row.get(col, "0") or 0))
        except ValueError:
            val = 0
        if val:
            out.add(LABEL_TO_CODE[col])
    return out


def observed_codes(events: dict[str, Any]) -> set[str]:
    return {code for key, code in EVENT_TO_CODE.items() if events.get(key) is True}


def compare_expected_observed(expected: set[str], observed: set[str]) -> str:
    if not observed:
        return "no_observed_oracle"
    if observed == expected:
        return "exact_oracle_match"
    if expected and expected.issubset(observed):
        return "observed_superset_contains_expected"
    if expected & observed:
        return "partial_oracle_overlap"
    return "different_oracle_symptom"


def file_count(path: Path) -> int:
    if not path.is_dir():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def size_kb(path: Path) -> int:
    if not path.is_dir():
        return 0
    total = 0
    for item in path.rglob("*"):
        if not item.is_file():
            continue
        try:
            total += item.stat().st_blocks * 512
        except OSError:
            pass
    return total // 1024


def classify(
    *,
    json_ok: bool,
    run_exists: bool,
    has_error: bool,
    has_bag: bool,
    has_score: bool,
    has_camera: bool,
    observed: set[str],
    event_other: str,
) -> str:
    if not json_ok:
        return "invalid_json_syntax"
    if not run_exists:
        return "missing_execution_output"
    if observed:
        return "oracle_triggered"
    if has_error and event_other == "goal":
        return "no_failure_reached_goal"
    if has_bag and has_error:
        return "trace_ready_no_oracle"
    if has_score or has_camera:
        return "partial_artifacts_no_oracle"
    if not has_error and not has_score and not has_camera:
        return "crash_or_minimal_artifacts"
    return "minimal_artifacts_unknown"


def preliminary_category(execution_status: str, oracle_match: str) -> str:
    if execution_status in {"invalid_json_syntax", "missing_execution_output", "crash_or_minimal_artifacts"}:
        return "invalid / crash"
    if execution_status in {"no_failure_reached_goal", "trace_ready_no_oracle", "partial_artifacts_no_oracle"}:
        return "no observed oracle / incomplete"
    if execution_status == "oracle_triggered" and oracle_match == "different_oracle_symptom":
        return "different failure"
    if execution_status == "oracle_triggered":
        return "needs same-root-cause review"
    return "unknown"


def pct(num: int, den: int) -> str:
    return "0.0%" if den == 0 else f"{num / den:.1%}"


def summarize(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row[key])].append(row)
    out: list[dict[str, Any]] = []
    for group, items in sorted(grouped.items()):
        exec_counts = Counter(row["execution_status"] for row in items)
        match_counts = Counter(row["oracle_match_status"] for row in items)
        cat_counts = Counter(row["post_execution_category_prelim"] for row in items)
        out.append(
            {
                key: group,
                "total": len(items),
                "json_valid": sum(bool(row["json_parse_ok"]) for row in items),
                "output_dirs": sum(bool(row["run_output_exists"]) for row in items),
                "has_rosbag": sum(int(row["bag_count"]) > 0 for row in items),
                "has_score": sum(int(row["score_count"]) > 0 for row in items),
                "has_camera": sum(int(row["camera_count"]) > 0 for row in items),
                "oracle_triggered": exec_counts["oracle_triggered"],
                "exact_oracle_match": match_counts["exact_oracle_match"],
                "observed_superset_contains_expected": match_counts["observed_superset_contains_expected"],
                "partial_oracle_overlap": match_counts["partial_oracle_overlap"],
                "different_oracle_symptom": match_counts["different_oracle_symptom"],
                "no_observed_oracle": match_counts["no_observed_oracle"],
                "invalid_crash": cat_counts["invalid / crash"],
                "no_observed_oracle_or_incomplete": cat_counts["no observed oracle / incomplete"],
                "needs_same_root_cause_review": cat_counts["needs same-root-cause review"],
                "different_failure": cat_counts["different failure"],
            }
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--pssd-root", type=Path, default=PSSD_ROOT)
    parser.add_argument("--json-dir", type=Path, default=None)
    parser.add_argument("--runs-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args()

    project_root = args.project_root
    pssd_root = args.pssd_root
    json_dir = args.json_dir or pssd_root / "PURE_LLM_JSON"
    runs_dir = args.runs_dir or pssd_root / "PURE_LLM_RUNS"
    output_dir = args.output_dir or project_root / "processed" / "experiments" / "pure_llm_execution_review"

    selected_rows = {
        row["Case ID"]: row
        for row in read_csv(project_root / "processed" / "experiments" / "selected_30_drivefuzz_seeds.csv")
        if row.get("Case ID")
    }

    json_paths = sorted(path for path in json_dir.glob("case_*.json") if not path.name.startswith("._"))
    run_dirs = {path.name: path for path in runs_dir.iterdir() if path.is_dir()} if runs_dir.exists() else {}

    rows: list[dict[str, Any]] = []
    for json_path in json_paths:
        candidate_id = json_path.stem
        case_id, model, cand = parse_name(candidate_id)
        seed = selected_rows.get(case_id, {})
        expected = expected_codes(seed)
        _, json_error = safe_json(json_path)
        json_ok = not json_error
        run_dir = run_dirs.get(candidate_id)

        if run_dir:
            bag_files = sorted((run_dir / "rosbags").glob("*.bag"))
            score_files = sorted((run_dir / "scores").glob("*.json"))
            camera_files = sorted((run_dir / "camera").glob("*.mp4"))
            queue_files = sorted((run_dir / "queue").glob("*.json"))
            cov_files = sorted((run_dir / "cov").glob("*.json"))
            error_obj, error_path, error_parse_error = first_json(run_dir / "errors")
            score_obj, score_path, score_parse_error = first_json(run_dir / "scores")
        else:
            bag_files = score_files = camera_files = queue_files = cov_files = []
            error_obj, error_path, error_parse_error = None, "", ""
            score_obj, score_path, score_parse_error = None, "", ""

        events = error_obj.get("events", {}) if isinstance(error_obj, dict) else {}
        events = events if isinstance(events, dict) else {}
        observed = observed_codes(events)
        event_other = str(events.get("other", ""))
        match = compare_expected_observed(expected, observed)
        status = classify(
            json_ok=json_ok,
            run_exists=run_dir is not None,
            has_error=bool(error_path),
            has_bag=bool(bag_files),
            has_score=bool(score_files),
            has_camera=bool(camera_files),
            observed=observed,
            event_other=event_other,
        )
        category = preliminary_category(status, match)
        score_summary = ""
        if isinstance(score_obj, dict):
            score_summary = "; ".join(f"{key}={value}" for key, value in score_obj.items())

        rows.append(
            {
                "candidate_id": candidate_id,
                "method": "Pure-LLM",
                "case_id": case_id,
                "model": model,
                "candidate_index": cand,
                "seed_group": seed.get("Group", ""),
                "expected_oracle_codes": "+".join(sorted(expected)),
                "observed_oracle_codes": "+".join(sorted(observed)),
                "oracle_match_status": match,
                "execution_status": status,
                "post_execution_category_prelim": category,
                "json_parse_ok": json_ok,
                "json_parse_error": json_error,
                "run_output_exists": run_dir is not None,
                "run_dir": str(run_dir) if run_dir else "",
                "size_kb": size_kb(run_dir) if run_dir else 0,
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
                "event_crash": events.get("crash", ""),
                "event_stuck": events.get("stuck", ""),
                "event_lane_invasion": events.get("lane_invasion", ""),
                "event_red": events.get("red", ""),
                "event_speeding": events.get("speeding", ""),
                "event_other": event_other,
                "num_frames": error_obj.get("num_frames", "") if isinstance(error_obj, dict) else "",
                "elapsed_time": error_obj.get("elapsed_time", "") if isinstance(error_obj, dict) else "",
                "score_summary": score_summary,
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "pure_llm_phase3_execution_results.csv", rows)
    by_model = summarize(rows, "model")
    by_case = summarize(rows, "case_id")
    write_csv(output_dir / "pure_llm_phase3_summary_by_model.csv", by_model)
    write_csv(output_dir / "pure_llm_phase3_summary_by_case.csv", by_case)

    total = len(rows)
    exec_counts = Counter(row["execution_status"] for row in rows)
    match_counts = Counter(row["oracle_match_status"] for row in rows)
    cat_counts = Counter(row["post_execution_category_prelim"] for row in rows)
    artifact_lines = [
        ("output directories", sum(row["run_output_exists"] for row in rows)),
        ("camera videos", sum(int(row["camera_count"]) > 0 for row in rows)),
        ("rosbags", sum(int(row["bag_count"]) > 0 for row in rows)),
        ("score files", sum(int(row["score_count"]) > 0 for row in rows)),
        ("error JSON files", sum(int(row["error_json_count"]) > 0 for row in rows)),
    ]

    report = output_dir / "pure_llm_phase3_report.md"
    with report.open("w", encoding="utf-8") as handle:
        handle.write("# Pure-LLM Phase 3 Execution Audit\n\n")
        handle.write(f"Generated: {datetime.now(timezone.utc).isoformat()}\n\n")
        handle.write(f"- JSON dir: `{json_dir}`\n")
        handle.write(f"- Runs dir: `{runs_dir}`\n")
        handle.write(f"- Total Pure-LLM candidates: {total}\n")
        handle.write(f"- JSON-valid candidates: {sum(row['json_parse_ok'] for row in rows)} / {total}\n\n")

        handle.write("## Artifact Availability\n\n")
        handle.write("| Artifact | Candidate count | Ratio |\n|---|---:|---:|\n")
        for name, count in artifact_lines:
            handle.write(f"| {name} | {count} | {pct(count, total)} |\n")

        handle.write("\n## Execution Status Counts\n\n")
        handle.write("| Status | Count | Ratio |\n|---|---:|---:|\n")
        for status, count in exec_counts.most_common():
            handle.write(f"| {status} | {count} | {pct(count, total)} |\n")

        handle.write("\n## Oracle Match Counts\n\n")
        handle.write("| Match status | Count | Ratio |\n|---|---:|---:|\n")
        for status, count in match_counts.most_common():
            handle.write(f"| {status} | {count} | {pct(count, total)} |\n")

        handle.write("\n## Preliminary Categories\n\n")
        handle.write("| Category | Count | Ratio |\n|---|---:|---:|\n")
        for status, count in cat_counts.most_common():
            handle.write(f"| {status} | {count} | {pct(count, total)} |\n")

        handle.write("\n## Model Summary\n\n")
        fields = [
            "model",
            "total",
            "has_rosbag",
            "has_camera",
            "oracle_triggered",
            "exact_oracle_match",
            "observed_superset_contains_expected",
            "partial_oracle_overlap",
            "different_oracle_symptom",
            "invalid_crash",
            "no_observed_oracle_or_incomplete",
            "needs_same_root_cause_review",
        ]
        handle.write("| " + " | ".join(fields) + " |\n")
        handle.write("|" + "|".join(["---"] + ["---:"] * (len(fields) - 1)) + "|\n")
        for row in by_model:
            handle.write("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |\n")

        handle.write("\n## Files\n\n")
        for name in [
            "pure_llm_phase3_execution_results.csv",
            "pure_llm_phase3_summary_by_model.csv",
            "pure_llm_phase3_summary_by_case.csv",
        ]:
            handle.write(f"- `{output_dir / name}`\n")

    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
