#!/usr/bin/env python3
"""Generate final Round 5 candidates from cumulative Bug2Scenario feedback.

The original seed and original Phase 1 pattern remain authoritative.  Every
same-seed candidate from Rounds 1--4 is retained as feedback, including failed,
boundary, and strictly preserved outcomes.  Round 5
uses this history without modifying any prior-round generator.
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
import run_round2_feedback_generation as r2
import run_round3_feedback_generation as r3
import run_round4_feedback_generation as r4


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "processed" / "experiments"
ROUND4_SOURCE_ROOT = EXPERIMENTS / "round4_feedback"
ROUND5_ROOT = EXPERIMENTS / "round5_feedback"
PROMPT_DIR = ROUND5_ROOT / "prompts"
API_OUTPUT_DIR = ROUND5_ROOT / "api_outputs"
CANDIDATE_DIR = ROUND5_ROOT / "candidates"
METADATA_DIR = ROUND5_ROOT / "metadata"
RESULTS_CSV = ROUND5_ROOT / "round5_generation_results.csv"
MANIFEST_CSV = ROUND5_ROOT / "Round5_manifest.csv"
ROUND4_MANUAL_JSON = ROUND4_SOURCE_ROOT / "round4_manual_feedback.json"

DEFAULT_PSSD_DIR = Path("<PSSD_ROOT>/Round5_JSON")
DEFAULT_PSSD_RUNS_DIR = Path("<PSSD_ROOT>/Round5_RUNS")
DEFAULT_MODEL = "claude-sonnet-4-5"
DEFAULT_CASES = [
    "case_024",
    "case_037",
    "case_039",
    "case_061",
    "case_094",
    "case_147",
]


def normalize_manual_result(value: Any, execution_status: str) -> str:
    label = str(value or "").strip().lower()
    if label in {"yes", "strictly preserved", "strictly_preserved"}:
        return "strictly_preserved"
    if label in {"?", "？", "uncertain", "partial or boundary", "partial_or_boundary"}:
        return "partial_or_boundary"
    if label in {"no", "not preserved", "not_preserved"}:
        return "not_preserved"
    if execution_status == "crash_or_minimal_artifacts":
        return "not_preserved_due_to_crash_or_missing_evidence"
    return "not_reviewed"


def load_round4_manual_rows(cases: list[str]) -> dict[str, list[dict[str, Any]]]:
    rows = json.loads(ROUND4_MANUAL_JSON.read_text(encoding="utf-8"))
    wanted = set(cases)
    grouped: dict[str, list[dict[str, Any]]] = {case_id: [] for case_id in cases}
    for row in rows:
        case_id = str(row.get("case_id", ""))
        if case_id in wanted:
            grouped[case_id].append(row)
    missing = [case_id for case_id, items in grouped.items() if len(items) != 6]
    if missing:
        detail = ", ".join(f"{case_id}={len(grouped[case_id])}" for case_id in missing)
        raise RuntimeError(f"Expected six Round 4 rows per seed; found {detail}")
    return grouped


def load_round4_specs(case_id: str, model_name: str) -> list[dict[str, Any]]:
    path = ROUND4_SOURCE_ROOT / "api_outputs" / f"{case_id}__{b2s.safe_name(model_name)}.json"
    payload = b2s.load_json(path)
    specs = (payload.get("parsed_response") or {}).get("candidate_specs") or []
    if len(specs) != 6:
        raise RuntimeError(f"Expected six Round 4 specs in {path}; found {len(specs)}")
    return specs


def compact_spec(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": spec.get("candidate_id"),
        "high_level_variant": r2.compact_text(spec.get("high_level_variant"), 260),
        "mutation_intent": r2.compact_text(spec.get("mutation_intent"), 360),
        "expected_oracle": spec.get("expected_oracle"),
        "modifications": spec.get("modifications") or {},
    }


def build_round4_feedback(
    case_id: str, model_name: str, rows: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    specs = load_round4_specs(case_id, model_name)
    ordered = sorted(rows, key=lambda row: str(row.get("candidate", "")))
    feedback: list[dict[str, Any]] = []
    for index, row in enumerate(ordered):
        execution_status = str(row.get("execution_status", ""))
        feedback.append(
            {
                "round": 4,
                "generator": model_name,
                "candidate_spec": compact_spec(specs[index]),
                "execution": {
                    "status": execution_status,
                    "expected_oracle_codes": row.get("expected_oracle", ""),
                    "observed_oracle_codes": row.get("observed_oracle", ""),
                    "oracle_match_status": row.get("oracle_match_status", ""),
                    "events": {
                        "collision": row.get("event_crash", ""),
                        "stuck": row.get("event_stuck", ""),
                        "lane_invasion": row.get("event_lane_invasion", ""),
                        "red_light": row.get("event_red", ""),
                    },
                    "artifact_counts": {
                        "bags": row.get("bag_count", 0),
                        "scores": row.get("score_count", 0),
                        "cameras": row.get("camera_count", 0),
                    },
                },
                "manual_review": {
                    "preservation_result": normalize_manual_result(
                        row.get("manual_preservation_result"), execution_status
                    ),
                    "observed_failure_type": row.get("manual_failure_type", ""),
                    "notes": r2.compact_text(row.get("manual_notes"), 500),
                },
                "memory_role": "historical_outcome_not_authoritative_target",
            }
        )
    return feedback


def build_prompt(
    case_id: str,
    model_name: str,
    phase1: dict[str, Any],
    seed: dict[str, Any],
    round1_feedback: list[dict[str, Any]],
    round2_feedback: list[dict[str, Any]],
    round3_feedback: list[dict[str, Any]],
    round4_feedback: list[dict[str, Any]],
) -> str:
    feedback_history = (
        [{"round": 1, **record} for record in round1_feedback]
        + [{"round": 2, **record} for record in round2_feedback]
        + round3_feedback
        + round4_feedback
    )
    payload = {
        "case_id": case_id,
        "model_name": model_name,
        "authoritative_original_target": {
            "original_phase1_output_from_seed_bug_and_trace_evidence": r2.compact_phase1(
                phase1
            ),
            "original_seed_scenario": b2s.compact_seed(seed),
        },
        "feedback_memory": {
            "record_policy": "retain_failed_boundary_and_successful_same_seed_attempts",
            "records": feedback_history,
        },
    }
    return "\n".join(
        [
            "You are the final Round 5 feedback-guided scenario amplifier for Bug2Scenario.",
            "The ORIGINAL seed case and its ORIGINAL Phase 1 root-cause pattern are the authoritative target.",
            "The original seed is known to be the correct failure case. Preserve its causal mechanism, including multiple interacting conditions when the original pattern is composite.",
            "The feedback memory contains all same-seed outcomes from Rounds 1 through 4: failures, partial/boundary cases, and any successful records. Preserve every record and use its manual result when selecting the next mutation.",
            "Do not redefine the target root cause from any historical candidate, a matching oracle label alone, or a different failure observed in a prior round.",
            "A partial/boundary result is useful evidence but is not a recovered seed and must not be treated as success.",
            "Generate six genuinely distinct candidates anchored to the original seed while avoiding repetition of prior failed mutations and using boundary evidence constructively.",
            "Return exactly one JSON object and no markdown.",
            "Return exactly six candidate_specs named cand_001 through cand_006.",
            "Use the same candidate schema and conservative numeric bounds as prior rounds:",
            "- actor x/y offsets within [-8, 8] meters and speed_delta within [-3, 3]",
            "- mission x/y offsets within [-5, 5] meters or keep_original=true",
            "- weather deltas within [-20, 20]",
            "- puddle level_delta within [-0.2, 0.2] and size_scale within [0.8, 1.2]",
            "- do not invent actors, puddles, maps, oracle labels, or unsupported fields",
            "- keep strings concise and output valid JSON",
            "",
            "Required output schema:",
            b2s.phase2_schema_text(),
            "",
            "Input JSON:",
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        ]
    )


def validate_response(parsed: Any, case_id: str) -> tuple[bool, list[str]]:
    valid, errors = b2s.validate_phase2_response(parsed, case_id, 6)
    if not valid or not isinstance(parsed, dict):
        return valid, errors
    expected_ids = [f"cand_{index:03d}" for index in range(1, 7)]
    actual_ids = [
        spec.get("candidate_id")
        for spec in parsed.get("candidate_specs", [])
        if isinstance(spec, dict)
    ]
    if actual_ids != expected_ids:
        errors.append(f"candidate_ids must be {expected_ids}; got {actual_ids}")
    return not errors, errors


def candidate_filename(case_id: str, index: int) -> str:
    return f"{case_id}__Round5_{index:02d}.json"


def run_case(
    case_id: str,
    model: dict[str, Any],
    round1_rows: list[dict[str, str]],
    round2_rows: list[dict[str, Any]],
    round3_rows: list[dict[str, Any]],
    round4_rows: list[dict[str, Any]],
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

    phase1_path = r2.PHASE1_OUTPUT_DIR / f"{case_id}__{b2s.safe_name(model_name)}.json"
    phase1 = b2s.load_json(phase1_path)
    seed = b2s.seed_scenario_from_error(case_id, b2s.read_error_json_from_zip(case_id))
    round1 = r2.round1_feedback(case_id, round1_rows)
    round2 = r3.build_round2_feedback(case_id, model_name, round2_rows)
    round3 = r4.build_round3_feedback(case_id, model_name, round3_rows)
    round4 = build_round4_feedback(case_id, model_name, round4_rows)
    prompt = build_prompt(
        case_id, model_name, phase1, seed, round1, round2, round3, round4
    )
    prompt_path = PROMPT_DIR / f"{case_id}.md"
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")

    item: dict[str, Any] = {
        "case_id": case_id,
        "model_name": model_name,
        "workflow": "round5_cumulative_feedback_guided_b2s",
        "authoritative_target": "original_seed_and_original_phase1_root_cause",
        "status": "dry_run" if not execute else "started",
        "schema_valid": False,
        "schema_errors": [],
        "num_round1_feedback_records": len(round1),
        "num_round2_feedback_records": len(round2),
        "num_round3_feedback_records": len(round3),
        "num_round4_feedback_records": len(round4),
        "num_candidates_requested": 6,
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
    raw_response = ""
    raw_payload: Any = None
    usage: dict[str, Any] = {}
    parsed: Any = None
    schema_valid = False
    schema_errors: list[str] = []
    last_error = ""
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
            scenario["name"] = f"bug2scenario-{case_id}-Round5-{index:02d}"
            pre_valid, errors, warnings = b2s.pre_validate_scenario(seed, scenario)
            pre_valid_count += int(pre_valid)
            json_path = CANDIDATE_DIR / candidate_filename(case_id, index)
            metadata_path = METADATA_DIR / candidate_filename(case_id, index).replace(
                ".json", ".metadata.json"
            )
            b2s.write_json(json_path, scenario)
            b2s.write_json(
                metadata_path,
                {
                    "case_id": case_id,
                    "round": 5,
                    "model_name": model_name,
                    "candidate_index": index,
                    "candidate_spec": spec,
                    "applied_modifications": applied,
                    "pre_validation": {
                        "pre_valid": pre_valid,
                        "errors": errors,
                        "warnings": warnings,
                    },
                    "authoritative_original_phase1_output": str(phase1_path),
                    "round1_feedback_count": len(round1),
                    "round2_feedback_count": len(round2),
                    "round3_feedback_count": len(round3),
                    "round4_feedback_count": len(round4),
                    "feedback_memory_policy": "all_same_seed_outcomes_retained",
                    "round5_api_output": str(output_path),
                },
            )
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


def sync_to_pssd(results: list[dict[str, Any]], pssd_dir: Path) -> int:
    pssd_dir.mkdir(parents=True, exist_ok=True)
    copied = 0
    for item in results:
        for record in item.get("candidate_records") or []:
            source = Path(record["json_path"])
            shutil.copyfile(source, pssd_dir / source.name)
            copied += 1
    return copied


def write_tables(results: list[dict[str, Any]], pssd_dir: Path | None) -> None:
    ROUND5_ROOT.mkdir(parents=True, exist_ok=True)
    fields = [
        "case_id",
        "model_name",
        "status",
        "schema_valid",
        "num_round1_feedback_records",
        "num_round2_feedback_records",
        "num_round3_feedback_records",
        "num_round4_feedback_records",
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
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in sorted(results, key=lambda row: row.get("case_id", "")):
            usage = item.get("usage") or {}
            writer.writerow(
                {
                    **{key: item.get(key) for key in fields if key not in {
                        "prompt_tokens", "completion_tokens", "total_tokens"
                    }},
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                }
            )

    with MANIFEST_CSV.open("w", newline="", encoding="utf-8") as handle:
        fields = ["round", "case_id", "candidate_index", "model_name", "local_json", "pssd_json", "pre_valid"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in sorted(results, key=lambda row: row.get("case_id", "")):
            for index, record in enumerate(item.get("candidate_records") or [], start=1):
                local_path = Path(record["json_path"])
                writer.writerow(
                    {
                        "round": 5,
                        "case_id": item.get("case_id"),
                        "candidate_index": index,
                        "model_name": item.get("model_name"),
                        "local_json": str(local_path),
                        "pssd_json": str(pssd_dir / local_path.name) if pssd_dir else "",
                        "pre_valid": record.get("pre_valid"),
                    }
                )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--rerun", action="store_true")
    parser.add_argument("--cases", nargs="+", default=DEFAULT_CASES)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--max-output-tokens", type=int, default=8192)
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
    round1_rows = r2.load_round1_review_rows(cases)
    round2_rows = r3.load_round2_manual_rows(cases)
    round3_rows = r4.load_round3_manual_rows(cases)
    round4_rows = load_round4_manual_rows(cases)
    api_key, key_source = b2s.load_api_key(config, use_dotenv=not args.no_dotenv)
    if args.execute and not api_key:
        raise SystemExit("Missing API key. Export OPAPI_KEY or allow the configured .env.")

    DEFAULT_PSSD_RUNS_DIR.mkdir(parents=True, exist_ok=True)
    generation = config.get("default_generation", {})
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {
            pool.submit(
                run_case,
                case_id,
                model,
                round1_rows[case_id],
                round2_rows[case_id],
                round3_rows[case_id],
                round4_rows[case_id],
                args.execute,
                args.rerun,
                args.max_output_tokens,
                api_key,
                config["base_url"],
                int(generation.get("timeout", 120)),
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
                    "num_round2_feedback_records": 2,
                    "num_round3_feedback_records": 6,
                    "num_round4_feedback_records": 6,
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
                f"pre_valid={item.get('num_pre_valid', 0)}",
                flush=True,
            )

    pssd_dir = args.pssd_dir if args.sync_pssd else None
    copied = sync_to_pssd(results, args.pssd_dir) if args.sync_pssd else 0
    write_tables(results, pssd_dir)
    print(f"Wrote {RESULTS_CSV}")
    print(f"Wrote {MANIFEST_CSV}")
    print(f"PSSD JSON copied: {copied}")
    print(f"PSSD runs directory: {DEFAULT_PSSD_RUNS_DIR}")
    print(f"API key source: {key_source if args.execute else 'not_used_dry_run'}")
    return 0 if all(item.get("status") in {"completed", "dry_run"} for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
