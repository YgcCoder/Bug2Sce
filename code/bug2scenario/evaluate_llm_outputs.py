#!/usr/bin/env python3
"""Parse and compare LLM outputs across proposal and pure-LLM workflows."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "processed"
LLM_OUTPUTS = PROCESSED / "llm_outputs"
LLM_EVAL = PROCESSED / "llm_evaluation"
WORKFLOWS = ["proposal", "pure_llm"]


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def cases_from_manual_review(selected_cases: list[str] | None = None) -> list[str]:
    rows = load_csv(PROCESSED / "manual_review_sheet.csv")
    case_ids = [row["case_id"] for row in rows]
    if selected_cases:
        selected = {f"case_{int(case):03d}" if not str(case).startswith("case_") else str(case) for case in selected_cases}
        case_ids = [case_id for case_id in case_ids if case_id in selected]
    return case_ids


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [line.strip() for line in value.splitlines() if line.strip()]
    return [value]


def value_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


def extract_pred(parsed: Any, key: str) -> Any:
    if isinstance(parsed, dict):
        return parsed.get(key)
    return None


def hallucination_flags(parsed: Any, raw_text: str, oracle_status: str, run_status: str) -> str:
    flags = []
    if run_status in {"dry_run", "skipped_no_api_key", "missing_prompt", "not_run"}:
        return ""
    text = (raw_text or "").lower()
    if oracle_status != "consistent":
        if "uncertain" not in text and "inconsist" not in text and "conflict" not in text:
            flags.append("oracle_conflict_not_mentioned")
    if isinstance(parsed, dict) and not parsed.get("fault_layer"):
        flags.append("missing_fault_layer")
    return "; ".join(flags)


def comparison_rows(selected_cases: list[str] | None = None) -> list[dict[str, Any]]:
    manual_rows = {row["case_id"]: row for row in load_csv(PROCESSED / "manual_review_sheet.csv")}
    oracle_rows = {row["case_id"]: row for row in load_csv(PROCESSED / "oracle_consistency.csv")}
    rows = []
    for case_id in cases_from_manual_review(selected_cases):
        dataset_group = manual_rows.get(case_id, {}).get("dataset_group", "unknown")
        oracle_status = oracle_rows.get(case_id, {}).get("consistency_status", "unknown")
        for workflow in WORKFLOWS:
            output = load_json(LLM_OUTPUTS / workflow / f"{case_id}_output.json")
            if not output:
                rows.append(
                    {
                        "case_id": case_id,
                        "dataset_group": dataset_group,
                        "oracle_consistency_status": oracle_status,
                        "workflow": workflow,
                        "status": "not_run",
                        "fault_layer_pred": "",
                        "fault_component_pred": "",
                        "has_causal_chain": "no",
                        "num_supporting_evidence": 0,
                        "num_uncertain_evidence": 0,
                        "mentions_uncertainty": "no",
                        "mentions_root_cause_pattern": "no",
                        "mentions_validation_rules": "no",
                        "hallucination_flags_if_detectable": "",
                        "suitable_for_Bug2Scenario": "",
                        "confidence_score": "",
                        "notes": "status=not_run",
                    }
                )
                continue
            status = output.get("status", "unknown")
            parsed = output.get("parsed_response")
            raw = output.get("raw_response", "")
            fault_layer = extract_pred(parsed, "fault_layer")
            fault_component = extract_pred(parsed, "fault_component")
            causal_chain = extract_pred(parsed, "causal_chain")
            support = as_list(extract_pred(parsed, "supporting_evidence"))
            uncertain = as_list(extract_pred(parsed, "uncertain_or_missing_evidence"))
            root_cause = extract_pred(parsed, "possible_root_cause_pattern")
            pre_rules = as_list(extract_pred(parsed, "pre_execution_validation_rules"))
            post_rules = as_list(extract_pred(parsed, "post_execution_validation_rules"))
            suitability = extract_pred(parsed, "whether_suitable_for_Bug2Scenario")
            confidence = extract_pred(parsed, "confidence_score")
            result_status = status
            notes = f"status={status}"
            if status in {"dry_run", "skipped_no_api_key", "missing_prompt"}:
                result_status = "not_run"
                fault_layer = ""
                fault_component = ""
                causal_chain = None
                support = []
                uncertain = []
                root_cause = None
                pre_rules = []
                post_rules = []
                suitability = ""
                confidence = ""
            rows.append(
                {
                    "case_id": case_id,
                    "dataset_group": dataset_group,
                    "oracle_consistency_status": oracle_status,
                    "workflow": workflow,
                    "status": result_status,
                    "fault_layer_pred": value_text(fault_layer),
                    "fault_component_pred": value_text(fault_component),
                    "has_causal_chain": "yes" if value_text(causal_chain).strip() else "no",
                    "num_supporting_evidence": len(support),
                    "num_uncertain_evidence": len(uncertain),
                    "mentions_uncertainty": "yes" if uncertain or "uncertain" in (raw or "").lower() else "no",
                    "mentions_root_cause_pattern": "yes" if value_text(root_cause).strip() else "no",
                    "mentions_validation_rules": "yes" if pre_rules or post_rules else "no",
                    "hallucination_flags_if_detectable": hallucination_flags(parsed, raw, oracle_status, status),
                    "suitable_for_Bug2Scenario": value_text(suitability),
                    "confidence_score": value_text(confidence),
                    "notes": notes,
                }
            )
    return rows


def write_comparison_table(rows: list[dict[str, Any]]) -> None:
    LLM_EVAL.mkdir(parents=True, exist_ok=True)
    path = LLM_EVAL / "llm_comparison_table.csv"
    fieldnames = [
        "case_id",
        "dataset_group",
        "oracle_consistency_status",
        "workflow",
        "status",
        "fault_layer_pred",
        "fault_component_pred",
        "has_causal_chain",
        "num_supporting_evidence",
        "num_uncertain_evidence",
        "mentions_uncertainty",
        "mentions_root_cause_pattern",
        "mentions_validation_rules",
        "hallucination_flags_if_detectable",
        "suitable_for_Bug2Scenario",
        "confidence_score",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_manual_evaluation(rows: list[dict[str, Any]]) -> None:
    path = LLM_EVAL / "manual_evaluation_sheet.csv"
    fieldnames = [
        "case_id",
        "workflow",
        "dataset_group",
        "oracle_consistency_status",
        "fault_layer_pred",
        "fault_component_pred",
        "causal_chain_score_1_to_5",
        "evidence_support_score_1_to_5",
        "hallucination_score_1_to_5",
        "root_cause_pattern_score_1_to_5",
        "scenario_amplification_usefulness_1_to_5",
        "human_notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "case_id": row["case_id"],
                    "workflow": row["workflow"],
                    "dataset_group": row["dataset_group"],
                    "oracle_consistency_status": row["oracle_consistency_status"],
                    "fault_layer_pred": row["fault_layer_pred"],
                    "fault_component_pred": row["fault_component_pred"],
                    "causal_chain_score_1_to_5": "",
                    "evidence_support_score_1_to_5": "",
                    "hallucination_score_1_to_5": "",
                    "root_cause_pattern_score_1_to_5": "",
                    "scenario_amplification_usefulness_1_to_5": "",
                    "human_notes": "",
                }
            )


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="*", help="Optional cases such as 001 024 027 013")
    args = parser.parse_args()

    rows = comparison_rows(args.cases)
    write_comparison_table(rows)
    write_manual_evaluation(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
