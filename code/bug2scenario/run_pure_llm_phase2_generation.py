#!/usr/bin/env python3
"""Generate Pure-LLM baseline DriveFuzz JSONs for the matched RQ3 experiment.

This script is separate from `run_phase2_generation.py`.

Baseline design:
- same 30 selected seed failures;
- same 6 LLM backbones;
- one candidate per seed-model pair, i.e. 180 candidates;
- no Phase 1 root-cause pattern, critical-window evidence, or preservation
  constraints in the prompt;
- same local concretization and lightweight pre-validation as Bug2Scenario.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from openai import OpenAI


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import run_phase2_generation as b2s  # noqa: E402


PROCESSED = ROOT / "processed"
EXPERIMENTS = PROCESSED / "experiments"
CONFIG_PATH = EXPERIMENTS / "llm_backbone_config.yaml"
SELECTED_CSV = EXPERIMENTS / "selected_30_drivefuzz_seeds.csv"

PURE_OUTPUT_DIR = EXPERIMENTS / "pure_llm_phase2_api_outputs"
PURE_PROMPT_DIR = EXPERIMENTS / "pure_llm_phase2_api_prompts"
PURE_CANDIDATE_DIR = EXPERIMENTS / "pure_llm_phase2_candidates"
PURE_RESULTS_CSV = EXPERIMENTS / "pure_llm_phase2_generation_results.csv"
PURE_REPORT_MD = EXPERIMENTS / "pure_llm_phase2_generation_report.md"
PSSD_JSON_DIR = Path("<PSSD_ROOT>/PURE_LLM_JSON")

COMPSAC_ENV = Path("<PRIVATE_CONFIG_ROOT>/compsac26-1原始代码/.env")


def load_config() -> dict[str, Any]:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def load_dotenv_value(path: Path, key: str) -> str | None:
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        if name.strip() == key:
            return value.strip().strip('"').strip("'")
    return None


def load_api_key(config: dict[str, Any], use_dotenv: bool) -> tuple[str | None, str]:
    env_name = config.get("api_key_env", "OPAPI_KEY")
    value = os.environ.get(env_name)
    if value:
        return value, f"env:{env_name}"
    if use_dotenv:
        value = load_dotenv_value(COMPSAC_ENV, env_name)
        if value:
            return value, str(COMPSAC_ENV)
    return None, "missing"


def model_map(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {model["name"]: model for model in config.get("models", [])}


def load_selected_cases() -> list[str]:
    with SELECTED_CSV.open(newline="", encoding="utf-8-sig") as handle:
        return [row["Case ID"] for row in csv.DictReader(handle) if row.get("Case ID")]


def selected_row_index() -> dict[str, dict[str, str]]:
    with SELECTED_CSV.open(newline="", encoding="utf-8-sig") as handle:
        return {row["Case ID"]: row for row in csv.DictReader(handle) if row.get("Case ID")}


def label_text(row: dict[str, str]) -> dict[str, Any]:
    labels = {
        "collision": int(float(row.get("Collision", "0") or 0)),
        "stuck": int(float(row.get("Stuck", "0") or 0)),
        "lane_invasion": int(float(row.get("Lane Invasion", "0") or 0)),
        "red_light": int(float(row.get("Red", "0") or 0)),
        "group": row.get("Group", ""),
    }
    return labels


def pure_schema_text() -> str:
    return """{
  "case_id": "case_XXX",
  "candidate_specs": [
    {
      "candidate_id": "cand_001",
      "high_level_variant": "under 20 words",
      "mutation_intent": "under 30 words",
      "expected_oracle": "collision | red_light | lane_invasion | stuck | compound | unknown",
      "modifications": {
        "weather_delta": {"rain": 0, "fog": 0, "wetness": 0, "puddle": 0},
        "actor_mutations": [
          {"actor_index": 0, "position_offset": {"x": 0.0, "y": 0.0}, "speed_delta": 0.0}
        ],
        "puddle_mutations": [
          {"puddle_index": 0, "location_offset": {"x": 0.0, "y": 0.0}, "level_delta": 0.0, "size_scale": 1.0}
        ],
        "mission_mutation": {"keep_original": true, "spawn_offset": {"x": 0.0, "y": 0.0}, "destination_offset": {"x": 0.0, "y": 0.0}}
      },
      "pre_execution_validation_rules": ["under 18 words"],
      "post_execution_validation_rules": ["under 18 words"],
      "uncertainty": ["under 18 words"]
    }
  ]
}"""


def build_prompt(case_id: str, model_name: str, seed: dict[str, Any], row: dict[str, str]) -> str:
    return "\n".join(
        [
            "You are the Pure-LLM baseline scenario generator for an Autoware DriveFuzz experiment.",
            "Task: generate one high-level candidate scenario spec from only the seed scenario summary and failure label.",
            "",
            "Important baseline rule:",
            "- Do not use root-cause patterns, critical-window evidence, trace evidence, or preservation constraints.",
            "- You only know the seed scenario and the DriveFuzz symptom label.",
            "- Generate candidate specs only; local rule-based code will concretize them into DriveFuzz-style JSON.",
            "",
            "Formatting and safety rules:",
            "- Return exactly one JSON object. Do not use markdown fences.",
            "- Generate exactly 1 candidate_specs item.",
            "- Do not invent new oracle labels beyond the provided fault label.",
            "- Keep actor position offsets within [-8, 8] meters on x/y.",
            "- Keep actor speed_delta within [-3, 3].",
            "- Keep mission spawn/destination offsets within [-5, 5] meters, or set keep_original=true.",
            "- Keep weather deltas conservative: each weather_delta should be within [-20, 20].",
            "- Keep puddle level_delta within [-0.2, 0.2] and size_scale within [0.8, 1.2].",
            "- Keep every string short. Do not write explanatory paragraphs.",
            "- Use plain ASCII quotes and valid JSON syntax only.",
            "- Do not include trailing commas, comments, markdown, or extra keys.",
            "",
            "Return JSON schema:",
            pure_schema_text(),
            "",
            "Input JSON:",
            json.dumps(
                {
                    "case_id": case_id,
                    "model_name": model_name,
                    "fault_label": label_text(row),
                    "seed_scenario": b2s.compact_seed(seed),
                    "baseline_input_limitation": "No root-cause pattern, no critical-window trace evidence, no preservation constraints.",
                },
                ensure_ascii=False,
                separators=(",", ":"),
            ),
        ]
    )


def extract_json(text: str) -> Any:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
        stripped = re.sub(r"\s*```$", "", stripped)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(stripped[start : end + 1])
        except json.JSONDecodeError:
            return None
    return None


def validate_response(parsed: Any, case_id: str) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not isinstance(parsed, dict):
        return False, ["parsed response is not a JSON object"]
    if parsed.get("case_id") != case_id:
        errors.append(f"case_id mismatch: expected {case_id}, got {parsed.get('case_id')}")
    specs = parsed.get("candidate_specs")
    if not isinstance(specs, list):
        errors.append("candidate_specs must be a list")
    elif len(specs) != 1:
        errors.append(f"candidate_specs length must be 1, got {len(specs)}")
    return not errors, errors


def out_path(case_id: str, model_name: str) -> Path:
    return PURE_OUTPUT_DIR / f"{case_id}__{b2s.safe_name(model_name)}.json"


def prompt_path(case_id: str, model_name: str) -> Path:
    return PURE_PROMPT_DIR / f"{case_id}__{b2s.safe_name(model_name)}.md"


def candidate_json_path(model_name: str, case_id: str) -> Path:
    return PURE_CANDIDATE_DIR / b2s.safe_name(model_name) / "json" / case_id / f"{case_id}__model_{b2s.safe_name(model_name)}__cand_001.json"


def candidate_metadata_path(model_name: str, case_id: str) -> Path:
    return PURE_CANDIDATE_DIR / b2s.safe_name(model_name) / "metadata" / case_id / f"{case_id}__model_{b2s.safe_name(model_name)}__cand_001.metadata.json"


def build_request_params(model: dict[str, Any], prompt: str, max_tokens_override: int | None) -> dict[str, Any]:
    max_tokens = max_tokens_override or int(model.get("max_tokens", 0) or 0) or 2048
    params: dict[str, Any] = {
        "model": model["model_id"],
        "messages": [
            {"role": "system", "content": "You are a strict JSON generator for a Pure-LLM ADS scenario baseline."},
            {"role": "user", "content": prompt},
        ],
    }
    params[model.get("token_parameter") or "max_tokens"] = max_tokens
    if not model.get("omit_temperature"):
        params["temperature"] = 0.2
    return params


def call_model(client: OpenAI, model: dict[str, Any], prompt: str, max_tokens_override: int | None) -> tuple[str, Any, dict[str, int | None]]:
    response = client.chat.completions.create(**build_request_params(model, prompt, max_tokens_override))
    content = response.choices[0].message.content or ""
    usage = response.usage
    usage_dict = {
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "completion_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }
    raw = response.model_dump() if hasattr(response, "model_dump") else json.loads(response.model_dump_json())
    return content, raw, usage_dict


def run_one(
    *,
    case_id: str,
    model: dict[str, Any],
    selected_rows: dict[str, dict[str, str]],
    client_args: dict[str, Any],
    execute: bool,
    rerun: bool,
    max_tokens: int | None,
) -> dict[str, Any]:
    model_name = model["name"]
    output = out_path(case_id, model_name)
    if output.exists() and not rerun:
        try:
            existing = json.loads(output.read_text(encoding="utf-8"))
            existing["skipped_existing"] = True
            return existing
        except json.JSONDecodeError:
            pass

    started = time.time()
    error_json = b2s.read_error_json_from_zip(case_id)
    seed = b2s.seed_scenario_from_error(case_id, error_json)
    prompt = build_prompt(case_id, model_name, seed, selected_rows[case_id])
    prompt_path(case_id, model_name).parent.mkdir(parents=True, exist_ok=True)
    prompt_path(case_id, model_name).write_text(prompt, encoding="utf-8")

    item: dict[str, Any] = {
        "case_id": case_id,
        "model_name": model_name,
        "workflow": "pure_llm_phase2_baseline",
        "status": "dry_run" if not execute else "started",
        "schema_valid": False,
        "schema_errors": [],
        "num_candidates_requested": 1,
        "num_candidates_written": 0,
        "num_pre_valid": 0,
        "candidate_records": [],
        "prompt_path": str(prompt_path(case_id, model_name)),
        "output_path": str(output),
        "prompt_estimated_tokens": math.ceil(len(prompt) / 4),
        "usage": {},
        "raw_response": "",
        "parsed_response": None,
        "raw_api_payload": None,
        "error_message": "",
        "elapsed_sec": None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    try:
        if execute:
            client = OpenAI(**client_args)
            raw_response = ""
            raw_payload = None
            usage = {}
            last_exc: Exception | None = None
            for attempt in range(1, 4):
                try:
                    raw_response, raw_payload, usage = call_model(client, model, prompt, max_tokens)
                    last_exc = None
                    break
                except Exception as exc:  # noqa: BLE001
                    last_exc = exc
                    time.sleep(min(20, 2 * attempt))
            if last_exc is not None:
                raise last_exc
        else:
            raw_response = json.dumps({"case_id": case_id, "candidate_specs": []})
            raw_payload = None
            usage = {}

        parsed = extract_json(raw_response)
        schema_valid, schema_errors = validate_response(parsed, case_id)
        item.update(
            {
                "status": "completed" if schema_valid else "schema_error",
                "schema_valid": schema_valid,
                "schema_errors": schema_errors,
                "usage": usage,
                "raw_response": raw_response,
                "parsed_response": parsed,
                "raw_api_payload": raw_payload,
            }
        )

        if schema_valid and isinstance(parsed, dict):
            spec = parsed["candidate_specs"][0]
            scenario, applied = b2s.apply_candidate_spec(seed, case_id, model_name, spec, 1)
            scenario["name"] = f"purellm-{case_id}-{b2s.safe_name(model_name)}-cand_001"
            pre_valid, errors, warnings = b2s.pre_validate_scenario(seed, scenario)
            json_path = candidate_json_path(model_name, case_id)
            metadata_path = candidate_metadata_path(model_name, case_id)
            b2s.write_json(json_path, scenario)
            b2s.write_json(
                metadata_path,
                {
                    "case_id": case_id,
                    "model_name": model_name,
                    "workflow": "pure_llm_phase2_baseline",
                    "candidate_index": 1,
                    "candidate_spec": spec,
                    "applied_modifications": applied,
                    "pre_validation": {"pre_valid": pre_valid, "errors": errors, "warnings": warnings},
                    "prompt_path": str(prompt_path(case_id, model_name)),
                    "phase2_output_path": str(output),
                    "baseline_note": "Pure-LLM baseline: prompt used no root-cause pattern or critical-window evidence.",
                },
            )
            item["candidate_records"].append(
                {
                    "json_path": str(json_path),
                    "metadata_path": str(metadata_path),
                    "case_id": case_id,
                    "model_name": model_name,
                    "candidate_index": 1,
                    "candidate_spec": spec,
                    "applied_modifications": applied,
                    "pre_validation": {"pre_valid": pre_valid, "errors": errors, "warnings": warnings},
                }
            )
            item["num_candidates_written"] = 1
            item["num_pre_valid"] = 1 if pre_valid else 0
    except Exception as exc:  # noqa: BLE001
        item["status"] = "error"
        item["error_message"] = repr(exc)

    item["elapsed_sec"] = round(time.time() - started, 3)
    b2s.write_json(output, item)
    return item


def collect_results() -> list[dict[str, Any]]:
    rows = []
    if not PURE_OUTPUT_DIR.exists():
        return rows
    for path in sorted(PURE_OUTPUT_DIR.glob("*.json")):
        try:
            rows.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return rows


def write_results_csv() -> None:
    fields = [
        "case_id",
        "model_name",
        "workflow",
        "status",
        "schema_valid",
        "num_candidates_requested",
        "num_candidates_written",
        "num_pre_valid",
        "prompt_estimated_tokens",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "error_message",
        "output_path",
        "timestamp",
    ]
    with PURE_RESULTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in collect_results():
            usage = item.get("usage") or {}
            writer.writerow(
                {
                    "case_id": item.get("case_id"),
                    "model_name": item.get("model_name"),
                    "workflow": item.get("workflow"),
                    "status": item.get("status"),
                    "schema_valid": item.get("schema_valid"),
                    "num_candidates_requested": item.get("num_candidates_requested"),
                    "num_candidates_written": item.get("num_candidates_written"),
                    "num_pre_valid": item.get("num_pre_valid"),
                    "prompt_estimated_tokens": item.get("prompt_estimated_tokens"),
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                    "error_message": item.get("error_message"),
                    "output_path": item.get("output_path"),
                    "timestamp": item.get("timestamp"),
                }
            )


def sync_to_pssd() -> int:
    PSSD_JSON_DIR.mkdir(parents=True, exist_ok=True)
    count = 0
    for path in PURE_CANDIDATE_DIR.glob("*/json/case_*/*.json"):
        target = PSSD_JSON_DIR / path.name
        shutil.copy2(path, target)
        count += 1
    return count


def write_report(pssd_count: int | None = None) -> None:
    rows = collect_results()
    total = len(rows)
    completed = sum(1 for row in rows if row.get("status") == "completed")
    schema_valid = sum(1 for row in rows if row.get("schema_valid") is True)
    written = sum(int(row.get("num_candidates_written") or 0) for row in rows)
    pre_valid = sum(int(row.get("num_pre_valid") or 0) for row in rows)
    errors = [row for row in rows if row.get("status") != "completed"]
    lines = [
        "# Pure-LLM Phase 2 Baseline Generation Report",
        "",
        f"- Tasks present: {total} / 180",
        f"- Completed tasks: {completed} / 180",
        f"- Schema-valid tasks: {schema_valid} / 180",
        f"- Candidate JSONs written: {written} / 180",
        f"- Pre-valid candidate JSONs: {pre_valid} / 180",
    ]
    if pssd_count is not None:
        lines.append(f"- JSONs synced to PSSD: {pssd_count}")
        lines.append(f"- PSSD JSON dir: `{PSSD_JSON_DIR}`")
    lines.extend(
        [
            "",
            "## Output Locations",
            "",
            f"- API outputs: `{PURE_OUTPUT_DIR}`",
            f"- Prompts: `{PURE_PROMPT_DIR}`",
            f"- Local candidate JSONs: `{PURE_CANDIDATE_DIR}`",
            f"- Summary CSV: `{PURE_RESULTS_CSV}`",
        ]
    )
    if errors:
        lines.extend(["", "## Non-completed Tasks", ""])
        for row in errors[:50]:
            lines.append(f"- `{row.get('case_id')}` / `{row.get('model_name')}`: {row.get('status')} {row.get('error_message')}")
    PURE_REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--rerun", action="store_true")
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--models", nargs="+")
    parser.add_argument("--cases", nargs="+")
    parser.add_argument("--sync-pssd", action="store_true")
    parser.add_argument("--use-dotenv", action="store_true", default=True)
    parser.add_argument("--max-tokens", type=int, default=2048)
    args = parser.parse_args()

    config = load_config()
    model_index = model_map(config)
    model_names = args.models or [model["name"] for model in config.get("models", [])]
    missing_models = [name for name in model_names if name not in model_index]
    if missing_models:
        raise SystemExit(f"Unknown models: {missing_models}")

    cases = args.cases or load_selected_cases()
    selected_rows = selected_row_index()
    tasks = [(case_id, model_index[model_name]) for model_name in model_names for case_id in cases]

    api_key, key_source = load_api_key(config, args.use_dotenv)
    if args.execute and not api_key:
        raise SystemExit(f"Missing API key: {key_source}")
    client_args = {"api_key": api_key or "dry-run", "base_url": config["base_url"], "timeout": config.get("default_generation", {}).get("timeout", 120)}

    print(f"Pure-LLM tasks: {len(tasks)}; workers={args.workers}; execute={args.execute}; key={key_source}")
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = [
            executor.submit(
                run_one,
                case_id=case_id,
                model=model,
                selected_rows=selected_rows,
                client_args=client_args,
                execute=args.execute,
                rerun=args.rerun,
                max_tokens=args.max_tokens,
            )
            for case_id, model in tasks
        ]
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(f"[{len(results):03d}/{len(tasks):03d}] {result.get('case_id')} {result.get('model_name')} {result.get('status')} written={result.get('num_candidates_written')} err={result.get('error_message') or ''}")

    write_results_csv()
    pssd_count = sync_to_pssd() if args.sync_pssd else None
    write_report(pssd_count)
    print(PURE_REPORT_MD)
    if pssd_count is not None:
        print(PSSD_JSON_DIR, pssd_count)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
