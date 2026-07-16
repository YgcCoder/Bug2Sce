#!/usr/bin/env python3
"""Generate Round 2 Bug2Scenario candidates with Round 1 feedback.

This script intentionally leaves the original Round 1 runners unchanged.  It
uses the same seed loader, candidate schema, deterministic concretizer, and
pre-execution validator as ``run_phase2_generation.py``.  The only experimental
difference is that Claude also receives the six models' Round 1 candidate specs,
execution summaries, and manual-review results for the same seed.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import shutil
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import OpenAI

import run_phase2_generation as b2s


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "processed" / "experiments"
ROUND2_ROOT = EXPERIMENTS / "round2_feedback"
PROMPT_DIR = ROUND2_ROOT / "prompts"
API_OUTPUT_DIR = ROUND2_ROOT / "api_outputs"
CANDIDATE_DIR = ROUND2_ROOT / "candidates"
METADATA_DIR = ROUND2_ROOT / "metadata"
RESULTS_CSV = ROUND2_ROOT / "round2_generation_results.csv"
MANIFEST_CSV = ROUND2_ROOT / "Round2_manifest.csv"

MANUAL_REVIEW_CSV = (
    EXPERIMENTS
    / "b2s_main_review"
    / "b2s_cand001_manual_review_normalized.csv"
)
PHASE1_OUTPUT_DIR = EXPERIMENTS / "phase1_api_outputs"
PHASE2_OUTPUT_DIR = EXPERIMENTS / "phase2_api_outputs"
DEFAULT_PSSD_DIR = Path("<PSSD_ROOT>/Round2_JSON")
DEFAULT_MODEL = "claude-sonnet-4-5"
DEFAULT_CASES = [
    "case_024",
    "case_037",
    "case_039",
    "case_061",
    "case_069",
    "case_094",
    "case_112",
    "case_118",
    "case_147",
]


def normalize_manual_label(value: str) -> str:
    label = (value or "").strip().lower()
    return {
        "yes": "strictly_preserved",
        "uncertain": "partial_or_boundary",
        "no": "not_preserved",
    }.get(label, label or "not_reviewed")


def compact_text(value: Any, max_chars: int = 500) -> str:
    text = str(value or "").strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def load_round1_review_rows(cases: list[str]) -> dict[str, list[dict[str, str]]]:
    wanted = set(cases)
    grouped: dict[str, list[dict[str, str]]] = {case_id: [] for case_id in cases}
    with MANUAL_REVIEW_CSV.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            case_id = row.get("case_id", "")
            if case_id in wanted:
                grouped[case_id].append(row)
    missing = [case_id for case_id, rows in grouped.items() if len(rows) != 6]
    if missing:
        details = ", ".join(f"{case_id}={len(grouped[case_id])}" for case_id in missing)
        raise RuntimeError(f"Expected six Round 1 review rows per seed; found {details}")
    return grouped


def load_round1_candidate_spec(case_id: str, model_name: str) -> dict[str, Any]:
    path = PHASE2_OUTPUT_DIR / f"{case_id}__{b2s.safe_name(model_name)}.json"
    if not path.exists():
        return {"source_missing": str(path)}
    payload = b2s.load_json(path)
    parsed = payload.get("parsed_response") or {}
    specs = parsed.get("candidate_specs") or []
    if not specs:
        return {"source_missing_candidate_spec": str(path)}
    spec = specs[0]
    return {
        "candidate_id": spec.get("candidate_id", "cand_001"),
        "high_level_variant": compact_text(spec.get("high_level_variant"), 240),
        "mutation_intent": compact_text(spec.get("mutation_intent"), 320),
        "expected_oracle": spec.get("expected_oracle", ""),
        "modifications": spec.get("modifications") or {},
    }


def round1_feedback(case_id: str, rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    feedback: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: item.get("model", "")):
        model_name = row.get("model", "")
        feedback.append(
            {
                "model": model_name,
                "round1_candidate_spec": load_round1_candidate_spec(case_id, model_name),
                "execution": {
                    "status": row.get("auto_execution_status", ""),
                    "expected_oracle_codes": row.get("expected_oracle_codes", ""),
                    "observed_oracle_codes": row.get("observed_oracle_codes", ""),
                    "oracle_match_status": row.get("oracle_match_status", ""),
                    "events": {
                        "collision": row.get("event_crash", ""),
                        "stuck": row.get("event_stuck", ""),
                        "lane_invasion": row.get("event_lane_invasion", ""),
                        "red_light": row.get("event_red", ""),
                    },
                },
                "automatic_analysis": {
                    "decision": row.get("auto_root_cause_decision", ""),
                    "reasons": compact_text(row.get("auto_root_cause_reasons"), 700),
                    "root_cause_pattern_summary": compact_text(
                        row.get("root_cause_pattern_summary"), 650
                    ),
                },
                "manual_review": {
                    "preservation_result": normalize_manual_label(
                        row.get("manual_same_root_cause_norm", "")
                    ),
                    "observed_failure_type": row.get("manual_failure_type", ""),
                    "notes": compact_text(row.get("manual_notes"), 400),
                },
            }
        )
    return feedback


def compact_phase1(phase1: dict[str, Any]) -> dict[str, Any]:
    parsed = phase1.get("parsed_response") or {}
    return {
        "fault_layer": parsed.get("fault_layer"),
        "fault_component": parsed.get("fault_component"),
        "causal_explanation": parsed.get("causal_explanation"),
        "root_cause_pattern": parsed.get("root_cause_pattern"),
        "preservation_constraints": parsed.get("preservation_constraints") or [],
        "modifiable_factors": parsed.get("modifiable_factors") or [],
        "non_modifiable_conditions": parsed.get("non_modifiable_conditions") or [],
        "uncertainty": parsed.get("uncertainty") or [],
        "notes_for_validator": parsed.get("notes_for_validator") or [],
        "ready_for_phase2_generation": parsed.get("ready_for_phase2_generation"),
    }


def build_prompt(
    case_id: str,
    model_name: str,
    phase1: dict[str, Any],
    seed: dict[str, Any],
    feedback: list[dict[str, Any]],
) -> str:
    input_payload = {
        "case_id": case_id,
        "model_name": model_name,
        "original_b2s_input": {
            "phase1_output_from_bug_and_trace_evidence": compact_phase1(phase1),
            "seed_scenario": b2s.compact_seed(seed),
        },
        "additional_round1_feedback": feedback,
    }
    return "\n".join(
        [
            "You are the Round 2 scenario amplifier for Bug2Scenario.",
            "Generate two new candidates using the original B2S input plus Round 1 feedback.",
            "The Round 1 feedback contains six models' candidate specs, execution results, automatic analysis, and manual review for the same seed.",
            "Use those records as additional evidence when choosing new mutations. Do not merely repeat a Round 1 candidate that was not strictly preserved.",
            "Do not treat an automatic or manual label as new simulator ground truth beyond the supplied evidence.",
            "Return exactly one JSON object and no markdown.",
            "Return exactly two candidate_specs named cand_001 and cand_002.",
            "Keep the original B2S root-cause-preservation objective.",
            "Use the same candidate schema and conservative numeric bounds as Round 1:",
            "- actor x/y offsets within [-8, 8] meters and speed_delta within [-3, 3]",
            "- mission x/y offsets within [-5, 5] meters or keep_original=true",
            "- weather deltas within [-20, 20]",
            "- puddle level_delta within [-0.2, 0.2] and size_scale within [0.8, 1.2]",
            "- do not invent actors, puddles, maps, oracle labels, or unsupported fields",
            "- keep strings concise and valid JSON syntax",
            "",
            "Required output schema:",
            b2s.phase2_schema_text(),
            "",
            "Input JSON:",
            json.dumps(input_payload, ensure_ascii=False, separators=(",", ":")),
        ]
    )


def validate_response(parsed: Any, case_id: str) -> tuple[bool, list[str]]:
    valid, errors = b2s.validate_phase2_response(parsed, case_id, 2)
    if not valid or not isinstance(parsed, dict):
        return valid, errors
    ids = [spec.get("candidate_id") for spec in parsed.get("candidate_specs", []) if isinstance(spec, dict)]
    if ids != ["cand_001", "cand_002"]:
        errors.append(f"candidate_ids must be cand_001,cand_002; got {ids}")
    return not errors, errors


def candidate_filename(case_id: str, index: int) -> str:
    return f"{case_id}__Round2_{index:02d}.json"


def run_case(
    case_id: str,
    model: dict[str, Any],
    reviews: list[dict[str, str]],
    execute: bool,
    rerun: bool,
    max_output_tokens: int,
    api_key: str | None,
    base_url: str,
    timeout: int,
) -> dict[str, Any]:
    model_name = model["name"]
    output_path = API_OUTPUT_DIR / f"{case_id}__{b2s.safe_name(model_name)}.json"
    if output_path.exists() and not rerun:
        existing = b2s.load_json(output_path)
        if existing.get("status") == "completed" and existing.get("schema_valid") is True:
            existing["skipped_existing"] = True
            return existing

    phase1_path = PHASE1_OUTPUT_DIR / f"{case_id}__{b2s.safe_name(model_name)}.json"
    if not phase1_path.exists():
        raise FileNotFoundError(f"Missing original B2S Phase 1 output: {phase1_path}")
    phase1 = b2s.load_json(phase1_path)
    seed = b2s.seed_scenario_from_error(case_id, b2s.read_error_json_from_zip(case_id))
    feedback = round1_feedback(case_id, reviews)
    prompt = build_prompt(case_id, model_name, phase1, seed, feedback)
    prompt_path = PROMPT_DIR / f"{case_id}.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")

    item: dict[str, Any] = {
        "case_id": case_id,
        "model_name": model_name,
        "workflow": "round2_feedback_guided_b2s",
        "experimental_difference": "six_models_round1_feedback_added_to_original_b2s_input",
        "status": "dry_run" if not execute else "started",
        "schema_valid": False,
        "schema_errors": [],
        "num_round1_feedback_records": len(feedback),
        "num_candidates_requested": 2,
        "num_candidates_written": 0,
        "num_pre_valid": 0,
        "prompt_path": str(prompt_path),
        "output_path": str(output_path),
        "prompt_estimated_tokens": math.ceil(len(prompt) / 4),
        "usage": {},
        "candidate_records": [],
        "raw_response": "",
        "parsed_response": None,
        "error_message": "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if not execute:
        API_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        b2s.write_json(output_path, item)
        return item

    if not api_key:
        raise RuntimeError("API key is required for --execute")
    started = time.time()
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
    last_error = ""
    raw_response = ""
    raw_payload: Any = None
    usage: dict[str, Any] = {}
    parsed: Any = None
    schema_valid = False
    schema_errors: list[str] = []
    for attempt in range(1, 4):
        try:
            raw_response, raw_payload, usage = b2s.call_model(
                client, model, prompt, max_output_tokens
            )
            parsed = b2s.extract_json(raw_response)
            schema_valid, schema_errors = validate_response(parsed, case_id)
            if schema_valid:
                last_error = ""
                break
            last_error = "; ".join(schema_errors)
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
        if attempt < 3:
            time.sleep(2 * attempt)

    item.update(
        {
            "status": "completed" if schema_valid else "schema_or_api_error",
            "schema_valid": schema_valid,
            "schema_errors": schema_errors,
            "usage": usage,
            "raw_response": raw_response,
            "parsed_response": parsed,
            "raw_api_payload": raw_payload,
            "error_message": last_error,
        }
    )

    if schema_valid and isinstance(parsed, dict):
        records = []
        pre_valid_count = 0
        for index, spec in enumerate(parsed["candidate_specs"], start=1):
            scenario, applied = b2s.apply_candidate_spec(
                seed, case_id, model_name, spec, index
            )
            scenario["name"] = f"bug2scenario-{case_id}-Round2-{index:02d}"
            pre_valid, errors, warnings = b2s.pre_validate_scenario(seed, scenario)
            pre_valid_count += int(pre_valid)
            json_path = CANDIDATE_DIR / candidate_filename(case_id, index)
            metadata_path = METADATA_DIR / candidate_filename(case_id, index).replace(
                ".json", ".metadata.json"
            )
            b2s.write_json(json_path, scenario)
            metadata = {
                "case_id": case_id,
                "round": 2,
                "model_name": model_name,
                "candidate_index": index,
                "candidate_spec": spec,
                "applied_modifications": applied,
                "pre_validation": {
                    "pre_valid": pre_valid,
                    "errors": errors,
                    "warnings": warnings,
                },
                "original_phase1_output": str(phase1_path),
                "round1_feedback_models": [entry["model"] for entry in feedback],
                "round2_api_output": str(output_path),
            }
            b2s.write_json(metadata_path, metadata)
            records.append(
                {
                    "json_path": str(json_path),
                    "metadata_path": str(metadata_path),
                    "pre_valid": pre_valid,
                    "pre_validation_errors": errors,
                    "pre_validation_warnings": warnings,
                }
            )
        item["candidate_records"] = records
        item["num_candidates_written"] = len(records)
        item["num_pre_valid"] = pre_valid_count

    item["elapsed_sec"] = round(time.time() - started, 3)
    API_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    b2s.write_json(output_path, item)
    return item


def write_tables(results: list[dict[str, Any]], pssd_dir: Path | None) -> None:
    ROUND2_ROOT.mkdir(parents=True, exist_ok=True)
    result_fields = [
        "case_id",
        "model_name",
        "status",
        "schema_valid",
        "num_round1_feedback_records",
        "num_candidates_written",
        "num_pre_valid",
        "prompt_estimated_tokens",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "elapsed_sec",
        "error_message",
    ]
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=result_fields)
        writer.writeheader()
        for item in sorted(results, key=lambda row: row.get("case_id", "")):
            usage = item.get("usage") or {}
            writer.writerow(
                {
                    "case_id": item.get("case_id"),
                    "model_name": item.get("model_name"),
                    "status": item.get("status"),
                    "schema_valid": item.get("schema_valid"),
                    "num_round1_feedback_records": item.get(
                        "num_round1_feedback_records"
                    ),
                    "num_candidates_written": item.get("num_candidates_written"),
                    "num_pre_valid": item.get("num_pre_valid"),
                    "prompt_estimated_tokens": item.get("prompt_estimated_tokens"),
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                    "elapsed_sec": item.get("elapsed_sec"),
                    "error_message": item.get("error_message"),
                }
            )

    manifest_fields = [
        "round",
        "case_id",
        "candidate_index",
        "model_name",
        "local_json",
        "pssd_json",
        "pre_valid",
    ]
    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=manifest_fields)
        writer.writeheader()
        for item in sorted(results, key=lambda row: row.get("case_id", "")):
            for index, record in enumerate(item.get("candidate_records") or [], start=1):
                local_path = Path(record["json_path"])
                writer.writerow(
                    {
                        "round": 2,
                        "case_id": item.get("case_id"),
                        "candidate_index": index,
                        "model_name": item.get("model_name"),
                        "local_json": str(local_path),
                        "pssd_json": str(pssd_dir / local_path.name) if pssd_dir else "",
                        "pre_valid": record.get("pre_valid"),
                    }
                )


def sync_to_pssd(results: list[dict[str, Any]], pssd_dir: Path) -> int:
    pssd_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for item in results:
        for record in item.get("candidate_records") or []:
            source = Path(record["json_path"])
            # copyfile avoids propagating macOS extended attributes to exFAT,
            # which otherwise creates misleading AppleDouble ``._*.json`` files.
            shutil.copyfile(source, pssd_dir / source.name)
            copied += 1
    return copied


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--rerun", action="store_true")
    parser.add_argument("--cases", nargs="+", default=DEFAULT_CASES)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--max-output-tokens", type=int, default=4096)
    parser.add_argument("--sync-pssd", action="store_true")
    parser.add_argument("--pssd-dir", type=Path, default=DEFAULT_PSSD_DIR)
    parser.add_argument("--no-dotenv", action="store_true")
    args = parser.parse_args()

    cases = [b2s.normalize_case(case_id) for case_id in args.cases]
    config = b2s.load_config()
    models = {model["name"]: model for model in config.get("models", [])}
    if args.model not in models:
        raise SystemExit(f"Unknown model: {args.model}")
    model = models[args.model]
    grouped_reviews = load_round1_review_rows(cases)
    api_key, key_source = b2s.load_api_key(
        config, use_dotenv=not args.no_dotenv
    )
    if args.execute and not api_key:
        raise SystemExit("Missing API key. Export OPAPI_KEY or allow the configured .env.")

    default_generation = config.get("default_generation", {})
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {
            pool.submit(
                run_case,
                case_id,
                model,
                grouped_reviews[case_id],
                args.execute,
                args.rerun,
                args.max_output_tokens,
                api_key,
                config["base_url"],
                int(default_generation.get("timeout", 120)),
            ): case_id
            for case_id in cases
        }
        for future in as_completed(futures):
            case_id = futures[future]
            try:
                item = future.result()
            except Exception as exc:  # noqa: BLE001
                item = {
                    "case_id": case_id,
                    "model_name": args.model,
                    "status": "error",
                    "schema_valid": False,
                    "num_round1_feedback_records": 6,
                    "num_candidates_written": 0,
                    "num_pre_valid": 0,
                    "usage": {},
                    "candidate_records": [],
                    "error_message": str(exc),
                }
            results.append(item)
            print(
                f"{case_id}: {item.get('status')} "
                f"candidates={item.get('num_candidates_written', 0)} "
                f"pre_valid={item.get('num_pre_valid', 0)}"
            )

    pssd_dir = args.pssd_dir if args.sync_pssd else None
    copied = sync_to_pssd(results, args.pssd_dir) if args.sync_pssd else 0
    write_tables(results, pssd_dir)
    print(f"Wrote {RESULTS_CSV}")
    print(f"Wrote {MANIFEST_CSV}")
    print(f"PSSD JSON copied: {copied}")
    print(f"API key source: {key_source if args.execute else 'not_used_dry_run'}")
    return 0 if all(item.get("status") in {"completed", "dry_run"} for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
