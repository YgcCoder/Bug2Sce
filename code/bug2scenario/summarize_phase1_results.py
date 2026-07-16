#!/usr/bin/env python3
"""Summarize Phase 1 API outputs by model and overall."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "processed" / "experiments"
OUTPUT_DIR = EXPERIMENTS / "phase1_api_outputs"
SELECTED_CSV = EXPERIMENTS / "selected_30_drivefuzz_seeds.csv"


def safe_model_name(name: str) -> str:
    return name.replace("/", "_").replace(":", "_")


def load_selected_cases() -> list[str]:
    with SELECTED_CSV.open(newline="", encoding="utf-8-sig") as handle:
        return [f"case_{int(row['Index']):03d}" for row in csv.DictReader(handle) if row.get("Index")]


def load_output(case_id: str, model_name: str) -> dict[str, Any] | None:
    path = OUTPUT_DIR / f"{case_id}__{safe_model_name(model_name)}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_model(model_name: str, cases: list[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case_id in cases:
        item = load_output(case_id, model_name)
        if item is None:
            rows.append(
                {
                    "case_id": case_id,
                    "model_name": model_name,
                    "status": "missing",
                    "schema_valid": "",
                    "quality_flags": "",
                    "total_tokens": 0,
                    "fault_layer": "",
                    "confidence": "",
                    "ready_for_phase2_generation": "",
                    "num_preservation_constraints": 0,
                    "num_uncertainty": 0,
                    "root_cause_pattern": "",
                    "output_path": "",
                }
            )
            continue
        parsed = item.get("parsed_response") or {}
        usage = item.get("usage") or {}
        rows.append(
            {
                "case_id": case_id,
                "model_name": model_name,
                "status": item.get("status"),
                "schema_valid": item.get("schema_valid"),
                "quality_flags": "; ".join(item.get("quality_flags") or []),
                "total_tokens": usage.get("total_tokens") or 0,
                "fault_layer": parsed.get("fault_layer"),
                "confidence": parsed.get("confidence"),
                "ready_for_phase2_generation": parsed.get("ready_for_phase2_generation"),
                "num_preservation_constraints": len(parsed.get("preservation_constraints") or []),
                "num_uncertainty": len(parsed.get("uncertainty") or []),
                "root_cause_pattern": parsed.get("root_cause_pattern"),
                "output_path": str(OUTPUT_DIR / f"{case_id}__{safe_model_name(model_name)}.json"),
            }
        )
    summary = {
        "model_name": model_name,
        "num_cases": len(rows),
        "status": Counter(str(row["status"]) for row in rows),
        "schema_valid": Counter(str(row["schema_valid"]) for row in rows),
        "quality_flagged": sum(1 for row in rows if row["quality_flags"]),
        "fault_layer": Counter(str(row["fault_layer"]) for row in rows),
        "confidence": Counter(str(row["confidence"]) for row in rows),
        "ready_for_phase2_generation": Counter(str(row["ready_for_phase2_generation"]) for row in rows),
        "total_tokens": sum(int(row["total_tokens"] or 0) for row in rows),
    }
    return rows, summary


def write_model_summary(model_name: str, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    safe = safe_model_name(model_name)
    csv_path = EXPERIMENTS / f"phase1_model_summary__{safe}.csv"
    md_path = EXPERIMENTS / f"phase1_model_summary__{safe}.md"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        f"# Phase 1 Model Summary: {model_name}",
        "",
        f"- Cases: `{summary['num_cases']}`",
        f"- Status: `{dict(summary['status'])}`",
        f"- Schema valid: `{dict(summary['schema_valid'])}`",
        f"- Quality-flagged cases: `{summary['quality_flagged']}`",
        f"- Total tokens: `{summary['total_tokens']}`",
        f"- Fault layer distribution: `{dict(summary['fault_layer'])}`",
        f"- Confidence distribution: `{dict(summary['confidence'])}`",
        f"- Ready for Phase 2 distribution: `{dict(summary['ready_for_phase2_generation'])}`",
        "",
        "## Cases",
        "",
        "| Case | Status | Schema | Fault Layer | Confidence | Ready | Flags |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['case_id']} | {row['status']} | {row['schema_valid']} | {row['fault_layer']} | {row['confidence']} | {row['ready_for_phase2_generation']} | {row['quality_flags']} |"
        )
    md_path.write_text("\n".join(lines), encoding="utf-8")


def write_overall_summary(summaries: list[dict[str, Any]]) -> None:
    path = EXPERIMENTS / "phase1_overall_model_summary.md"
    lines = [
        "# Phase 1 Overall Model Summary",
        "",
        "| Model | Cases | Completed | Schema Valid | Quality Flags | Ready Yes | Ready Uncertain | Ready No | Total Tokens |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for summary in summaries:
        ready = summary["ready_for_phase2_generation"]
        lines.append(
            "| {model} | {cases} | {completed} | {schema_valid} | {flags} | {yes} | {uncertain} | {no} | {tokens} |".format(
                model=summary["model_name"],
                cases=summary["num_cases"],
                completed=summary["status"].get("completed", 0),
                schema_valid=summary["schema_valid"].get("True", 0),
                flags=summary["quality_flagged"],
                yes=ready.get("yes", 0),
                uncertain=ready.get("uncertain", 0),
                no=ready.get("no", 0),
                tokens=summary["total_tokens"],
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", required=True)
    args = parser.parse_args()
    cases = load_selected_cases()
    summaries = []
    for model_name in args.models:
        rows, summary = summarize_model(model_name, cases)
        write_model_summary(model_name, rows, summary)
        summaries.append(summary)
        print(model_name, dict(summary["status"]), dict(summary["ready_for_phase2_generation"]), "tokens", summary["total_tokens"])
    write_overall_summary(summaries)
    print(EXPERIMENTS / "phase1_overall_model_summary.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
