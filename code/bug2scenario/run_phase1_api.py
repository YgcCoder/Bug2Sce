#!/usr/bin/env python3
"""Run cost-controlled Phase 1 causal explanation with OpenAI-compatible APIs.

Default behavior is dry-run. Use --execute to spend API calls.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from openai import OpenAI


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "processed"
EXPERIMENTS = PROCESSED / "experiments"
CONFIG_PATH = EXPERIMENTS / "llm_backbone_config.yaml"
PHASE1_OUTPUT_DIR = EXPERIMENTS / "phase1_api_outputs"
PHASE1_PROMPT_DIR = EXPERIMENTS / "phase1_api_prompts"
RESULTS_CSV = EXPERIMENTS / "phase1_api_results.csv"
COST_SUMMARY_MD = EXPERIMENTS / "phase1_cost_summary.md"
COMPSAC_ENV = Path("<PRIVATE_CONFIG_ROOT>/compsac26-1原始代码/.env")

REQUIRED_RESPONSE_FIELDS = [
    "case_id",
    "fault_layer",
    "fault_component",
    "causal_explanation",
    "root_cause_pattern",
    "preservation_constraints",
    "uncertainty",
    "confidence",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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


def normalize_case(value: str) -> str:
    text = value.strip().lower().replace("case_", "")
    return f"case_{int(text):03d}"


def load_selected30_cases() -> list[str]:
    path = EXPERIMENTS / "selected_30_drivefuzz_seeds.csv"
    with path.open(newline="", encoding="utf-8") as f:
        return [row["Case ID"] for row in csv.DictReader(f) if row.get("Case ID")]


def model_map(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {model["name"]: model for model in config.get("models", [])}


def load_root_pattern_index() -> dict[str, dict[str, Any]]:
    path = EXPERIMENTS / "root_cause_patterns.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {item["case_id"]: item for item in data}


def trim_list(values: list[Any], limit: int = 8) -> list[Any]:
    return values[:limit] + ([f"... {len(values) - limit} more"] if len(values) > limit else [])


def compact_stats(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    keep = {}
    for key in ["min", "max", "mean", "last", "rows", "count_stats", "waypoint_count_stats"]:
        if key in value:
            keep[key] = value[key]
    return keep or value


def compact_collision_window(window: dict[str, Any]) -> dict[str, Any]:
    return {
        "collision_timestamp": window.get("collision_timestamp"),
        "window_start": window.get("window_start"),
        "window_end": window.get("window_end"),
        "collision_topic_exists": window.get("collision_topic_exists"),
        "error_json_crash": window.get("error_json_crash"),
        "ego_speed_before_collision": window.get("ego_speed_before_collision"),
        "ego_control_before_collision": {
            "vehicle_status_control_stats": window.get("ego_control_before_collision", {}).get("vehicle_status_control_stats"),
            "vehicle_cmd_stats": window.get("ego_control_before_collision", {}).get("vehicle_cmd_stats"),
        },
        "detected_object_count_before_collision": window.get("detected_object_count_before_collision"),
        "predicted_object_count_before_collision": window.get("predicted_object_count_before_collision"),
        "final_waypoints_before_collision": window.get("final_waypoints_before_collision"),
        "closest_available_object_info": window.get("closest_available_object_info"),
        "evidence_of_braking_or_stopping": window.get("evidence_of_braking_or_stopping"),
    }


def compact_critical_window(critical: dict[str, Any]) -> dict[str, Any]:
    compact = {
        "case_id": critical.get("case_id"),
        "dataset_group": critical.get("dataset_group"),
        "oracle_consistency_status": critical.get("oracle_consistency_status"),
        "error_json_events": critical.get("error_json_events"),
    }
    if "collision_window" in critical:
        compact["collision_window"] = compact_collision_window(critical["collision_window"])
    if "red_light_window" in critical:
        compact["red_light_window"] = critical["red_light_window"]
    if "stuck_window" in critical:
        compact["stuck_window"] = critical["stuck_window"]
    if "label_conflict" in critical:
        compact["label_conflict"] = critical["label_conflict"]
    return compact


def compact_trace_summary(llm_input: dict[str, Any]) -> dict[str, Any]:
    trace = llm_input.get("trace_summary", {})
    sensing = trace.get("sensing", {})
    perception = trace.get("perception", {})
    planning = trace.get("planning", {})
    actuation = trace.get("actuation", {})
    oracle = trace.get("oracle", {})
    return {
        "sensing": {
            "image_raw": {
                "exists": sensing.get("image_raw", {}).get("exists"),
                "decode_status": sensing.get("image_raw", {}).get("decode_status"),
                "shape": {
                    "height": sensing.get("image_raw", {}).get("height"),
                    "width": sensing.get("image_raw", {}).get("width"),
                    "encoding": sensing.get("image_raw", {}).get("encoding"),
                },
                "time_range": [
                    sensing.get("image_raw", {}).get("first_timestamp"),
                    sensing.get("image_raw", {}).get("last_timestamp"),
                ],
            },
            "points_raw": {
                "exists": sensing.get("points_raw", {}).get("exists"),
                "decode_status": sensing.get("points_raw", {}).get("decode_status"),
                "shape": {
                    "height": sensing.get("points_raw", {}).get("height"),
                    "width": sensing.get("points_raw", {}).get("width"),
                    "point_step": sensing.get("points_raw", {}).get("point_step"),
                },
                "time_range": [
                    sensing.get("points_raw", {}).get("first_timestamp"),
                    sensing.get("points_raw", {}).get("last_timestamp"),
                ],
            },
        },
        "perception": {
            "detection_objects": perception.get("detection_fusion_objects", perception.get("detection/fusion_tools/objects", {})),
            "prediction_objects": perception.get("prediction_objects", perception.get("prediction/motion_predictor/objects", {})),
            "current_pose": perception.get("current_pose", {}),
        },
        "planning": {
            "final_waypoints": planning.get("final_waypoints", {}),
            "lane_waypoints_array": planning.get("lane_waypoints_array", {}),
        },
        "actuation": {
            "vehicle_cmd": actuation.get("vehicle_cmd", {}),
            "vehicle_status": actuation.get("vehicle_status", {}),
        },
        "oracle": oracle,
    }


def build_case_evidence(case_id: str, root_patterns: dict[str, dict[str, Any]], include_manual_draft: bool) -> dict[str, Any]:
    llm_input = load_json(PROCESSED / "llm_inputs" / f"{case_id}.json")
    critical = load_json(PROCESSED / "critical_windows" / f"{case_id}_critical_window.json")
    root_pattern = root_patterns.get(case_id, {})
    evidence = {
        "case_id": case_id,
        "fault_label": llm_input.get("fault_label"),
        "oracle_consistency": llm_input.get("oracle_consistency"),
        "scenario_config": llm_input.get("scenario_config"),
        "available_topics": trim_list(llm_input.get("available_topics", []), 16),
        "critical_window_summary": compact_critical_window(critical),
        "trace_summary_compact": compact_trace_summary(llm_input),
        "known_limitations": trim_list(llm_input.get("known_limitations", []), 8),
        "manual_phase1_status": {
            "candidate_generation_status": root_pattern.get("candidate_generation_status"),
            "oracle_consistency_status": root_pattern.get("oracle_consistency_status"),
            "known_limitations": root_pattern.get("known_limitations", []),
        },
    }
    if include_manual_draft:
        evidence["manual_phase1_draft"] = {
            "causal_explanation": root_pattern.get("causal_explanation"),
            "root_cause_pattern": root_pattern.get("root_cause_pattern"),
            "preservation_constraints": root_pattern.get("preservation_constraints"),
        }
    return evidence


def phase1_schema_text() -> str:
    return """{
  "case_id": "case_XXX",
  "fault_layer": "sensing | perception | planning | actuation | simulator | map | unknown",
  "fault_component": "under 8 words or unknown",
  "causal_explanation": "one sentence under 35 words",
  "root_cause_pattern": "one sentence under 30 words or unknown",
  "preservation_constraints": ["max 3 items; each under 18 words"],
  "modifiable_factors": ["max 4 short factors"],
  "non_modifiable_conditions": ["max 3 items; each under 18 words"],
  "uncertainty": ["max 3 items; each under 18 words"],
  "evidence_support": [
    {"evidence_id": "short id", "claim": "under 18 words"}
  ],
  "confidence": "high | medium | low",
  "ready_for_phase2_generation": "yes | no | uncertain",
  "notes_for_validator": ["max 3 items; each under 18 words"]
}"""


def one_shot_style_reference() -> str:
    return """{
  "case_id": "case_EXAMPLE",
  "fault_layer": "unknown",
  "fault_component": "unknown",
  "causal_explanation": "The oracle confirms a collision near an actor, but module-level fault attribution is not directly supported.",
  "root_cause_pattern": "Preserve a nearby actor-route interaction before the same oracle symptom.",
  "preservation_constraints": [
    "Preserve the same oracle symptom.",
    "Keep actor near ego route.",
    "Check critical-window actor proximity."
  ],
  "modifiable_factors": ["actor_position", "weather", "puddles"],
  "non_modifiable_conditions": ["same oracle symptom", "nearby actor-route interaction"],
  "uncertainty": ["Module attribution is not directly supported."],
  "evidence_support": [
    {"evidence_id": "critical_window", "claim": "Nearby actor evidence exists before failure."}
  ],
  "confidence": "low",
  "ready_for_phase2_generation": "yes",
  "notes_for_validator": ["Require same oracle and preserved interaction."]
}"""


def build_prompt(case_id: str, evidence: dict[str, Any]) -> str:
    return "\n".join(
        [
            "You are the Phase 1 failure analyzer for Bug2Scenario.",
            "Task: infer a causal explanation and a root-cause pattern from the given DriveFuzz/Autoware evidence.",
            "",
            "Rules:",
            "- Return exactly one JSON object. Do not use markdown fences.",
            "- Use only the provided evidence. Do not invent sensor, perception, planning, control, map, or simulator facts.",
            "- Do not treat topic existence as proof that a module behaved correctly.",
            "- If Dataset.xlsx and error.json disagree, mark uncertainty and do not treat the dataset label as confirmed ground truth.",
            "- For red-light cases, do not infer route-light relation or stop-line crossing unless evidence is provided.",
            "- For lane invasion, do not infer lane-boundary crossing unless evidence is provided.",
            "- For stuck cases, use last-window velocity/movement evidence if available.",
            "- If vehicle_cmd is all zero but vehicle_status shows movement/braking, mark controller behavior as uncertain. Do not assign fault_layer=actuation from this mismatch alone.",
            "- Preservation constraints must be semantic conditions, not exact timestamps, raw actor IDs, or message-specific identifiers.",
            "- Root-cause patterns should describe a mechanism. Avoid label-like patterns unless independently supported by evidence.",
            "- Do not write that a module `fails to` detect, predict, plan, stop, or avoid unless the provided evidence directly supports that internal failure.",
            "- If the evidence only shows a symptom plus available topics, use cautious language such as `possible`, `candidate`, or `unknown`.",
            "- Prefer fault_layer=unknown when module-level attribution is not directly supported by critical-window evidence.",
            "- A root-cause pattern may be a conservative preservation pattern, not a confirmed module bug.",
            "- Do not set ready_for_phase2_generation=no solely because fault_layer is unknown. Use yes when there is a checkable conservative preservation pattern; use uncertain when labels conflict or a key condition is missing.",
            "- Be concise: one-sentence explanation, one-sentence root_cause_pattern, max 3 constraints.",
            "- Keep all strings short. Do not write paragraphs.",
            "- Output only valid JSON. Do not use markdown fences or backticks.",
            "- Do not include trailing commas, comments, or extra keys.",
            "",
            "Return JSON schema:",
            phase1_schema_text(),
            "",
            "Output style reference only; do not copy facts from this example into the current case:",
            one_shot_style_reference(),
            "",
            "Input evidence JSON:",
            json.dumps(evidence, ensure_ascii=False, separators=(",", ":")),
        ]
    )


def extract_json(text: str) -> Any:
    stripped = text.strip()
    if not stripped:
        return None
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


def validate_phase1_response(parsed: Any, expected_case_id: str) -> tuple[bool, list[str]]:
    errors = []
    if not isinstance(parsed, dict):
        return False, ["parsed response is not a JSON object"]
    for field in REQUIRED_RESPONSE_FIELDS:
        if field not in parsed:
            errors.append(f"missing field: {field}")
    if parsed.get("case_id") != expected_case_id:
        errors.append(f"case_id mismatch: expected {expected_case_id}, got {parsed.get('case_id')}")
    if parsed.get("fault_layer") not in {"sensing", "perception", "planning", "actuation", "simulator", "map", "unknown"}:
        errors.append("fault_layer is outside allowed enum")
    if parsed.get("confidence") not in {"high", "medium", "low"}:
        errors.append("confidence is outside allowed enum")
    for list_field in ["preservation_constraints", "uncertainty"]:
        if list_field in parsed and not isinstance(parsed[list_field], list):
            errors.append(f"{list_field} must be a list")
    return not errors, errors


def quality_flags(parsed: Any) -> list[str]:
    if not isinstance(parsed, dict):
        return []
    flags = []
    text_blob = json.dumps(parsed, ensure_ascii=False).lower()
    uncertainty_text = " ".join(str(item).lower() for item in parsed.get("uncertainty", []) if isinstance(item, str))
    if parsed.get("fault_layer") == "actuation" and "vehicle_cmd" in text_blob and "vehicle_status" in text_blob:
        if "uncertain" in uncertainty_text or "uncertain" in text_blob:
            flags.append("possible_overattribution_from_vehicle_cmd_status_mismatch")
    constraints = parsed.get("preservation_constraints") or []
    non_modifiable = parsed.get("non_modifiable_conditions") or []
    combined_rules = " ".join(str(item).lower() for item in constraints + non_modifiable)
    if re.search(r"\b\d{2}\.\d{3,}\b", combined_rules):
        flags.append("preservation_rules_include_exact_timestamp")
    if re.search(r"\b(actor id|object_id|id \d{3,}|actor \d{3,})\b", combined_rules):
        flags.append("preservation_rules_include_raw_identifier")
    attribution_terms = [
        "fails to detect",
        "failed to detect",
        "fails to predict",
        "failed to predict",
        "fails to plan",
        "failed to plan",
        "fails to stop",
        "failed to stop",
        "fails to avoid",
        "failed to avoid",
        "does not generate",
        "did not generate",
    ]
    if any(term in text_blob for term in attribution_terms) and parsed.get("fault_layer") != "unknown":
        if "unknown" not in uncertainty_text and "insufficient" not in uncertainty_text and "not directly" not in uncertainty_text:
            flags.append("possible_overattribution_to_module_failure")
    return flags


def output_path(case_id: str, model_name: str) -> Path:
    safe_model = model_name.replace("/", "_").replace(":", "_")
    return PHASE1_OUTPUT_DIR / f"{case_id}__{safe_model}.json"


def prompt_path(case_id: str, model_name: str) -> Path:
    safe_model = model_name.replace("/", "_").replace(":", "_")
    return PHASE1_PROMPT_DIR / f"{case_id}__{safe_model}.md"


def estimate_tokens(text: str) -> int:
    return math.ceil(len(text) / 4)


def estimate_cost_usd(model: dict[str, Any], prompt_tokens: int | None, completion_tokens: int | None) -> float | None:
    pricing = model.get("pricing_usd_per_1k_tokens")
    if not pricing or prompt_tokens is None or completion_tokens is None:
        return None
    return round(
        prompt_tokens / 1000 * float(pricing.get("input", 0))
        + completion_tokens / 1000 * float(pricing.get("output", 0)),
        6,
    )


def build_request_params(model: dict[str, Any], prompt: str, max_tokens_override: int | None) -> dict[str, Any]:
    max_tokens = max_tokens_override or int(model.get("max_tokens", 0) or 0)
    if not max_tokens:
        max_tokens = 2048
    params: dict[str, Any] = {
        "model": model["model_id"],
        "messages": [
            {"role": "system", "content": "You are a strict JSON generator for a software testing paper experiment."},
            {"role": "user", "content": prompt},
        ],
    }
    params[model.get("token_parameter") or "max_tokens"] = max_tokens
    if not model.get("omit_temperature"):
        params["temperature"] = 0.2
    return params


def call_model(client: OpenAI, model: dict[str, Any], prompt: str, max_tokens_override: int | None) -> tuple[str, dict[str, Any], dict[str, int | None]]:
    params = build_request_params(model, prompt, max_tokens_override)
    response = client.chat.completions.create(**params)
    content = response.choices[0].message.content or ""
    usage = response.usage
    usage_dict = {
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "completion_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
    }
    raw = response.model_dump() if hasattr(response, "model_dump") else json.loads(response.model_dump_json())
    return content, raw, usage_dict


def make_result(
    case_id: str,
    model: dict[str, Any],
    prompt: str,
    status: str,
    parsed_response: Any,
    raw_response: str,
    raw_api_payload: Any,
    usage: dict[str, int | None],
    error_message: str,
    dry_run: bool,
) -> dict[str, Any]:
    if dry_run or status.startswith("skipped_"):
        schema_valid, schema_errors = None, []
    else:
        schema_valid, schema_errors = validate_phase1_response(parsed_response, case_id) if parsed_response is not None else (False, ["no parsed response"])
    prompt_tokens_est = estimate_tokens(prompt)
    estimated_cost = estimate_cost_usd(model, usage.get("prompt_tokens"), usage.get("completion_tokens"))
    return {
        "case_id": case_id,
        "workflow": "phase1_causal_explanation",
        "model_name": model["name"],
        "model_id": model["model_id"],
        "status": status,
        "dry_run": dry_run,
        "schema_valid": schema_valid,
        "schema_errors": schema_errors,
        "quality_flags": quality_flags(parsed_response),
        "prompt_path": str(prompt_path(case_id, model["name"])),
        "output_path": str(output_path(case_id, model["name"])),
        "prompt_estimated_tokens": prompt_tokens_est,
        "usage": usage,
        "estimated_cost_usd": estimated_cost,
        "raw_response": raw_response,
        "parsed_response": parsed_response,
        "raw_api_payload": raw_api_payload,
        "error_message": error_message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def collect_results() -> list[dict[str, Any]]:
    if not PHASE1_OUTPUT_DIR.exists():
        return []
    rows = []
    for path in sorted(PHASE1_OUTPUT_DIR.glob("*.json")):
        try:
            rows.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return rows


def write_results_csv() -> None:
    rows = collect_results()
    fields = [
        "case_id",
        "model_name",
        "model_id",
        "status",
        "dry_run",
        "schema_valid",
        "prompt_estimated_tokens",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "estimated_cost_usd",
        "confidence",
        "ready_for_phase2_generation",
        "fault_layer",
        "num_preservation_constraints",
        "num_uncertainty",
        "quality_flags",
        "error_message",
        "output_path",
        "timestamp",
    ]
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for item in rows:
            parsed = item.get("parsed_response") or {}
            usage = item.get("usage") or {}
            flags = item.get("quality_flags")
            if flags is None:
                flags = quality_flags(parsed)
            writer.writerow(
                {
                    "case_id": item.get("case_id"),
                    "model_name": item.get("model_name"),
                    "model_id": item.get("model_id"),
                    "status": item.get("status"),
                    "dry_run": item.get("dry_run"),
                    "schema_valid": item.get("schema_valid"),
                    "prompt_estimated_tokens": item.get("prompt_estimated_tokens"),
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                    "estimated_cost_usd": item.get("estimated_cost_usd"),
                    "confidence": parsed.get("confidence"),
                    "ready_for_phase2_generation": parsed.get("ready_for_phase2_generation"),
                    "fault_layer": parsed.get("fault_layer"),
                    "num_preservation_constraints": len(parsed.get("preservation_constraints") or []),
                    "num_uncertainty": len(parsed.get("uncertainty") or []),
                    "quality_flags": "; ".join(flags),
                    "error_message": item.get("error_message"),
                    "output_path": item.get("output_path"),
                    "timestamp": item.get("timestamp"),
                }
            )


def write_cost_summary() -> None:
    rows = collect_results()
    completed = [r for r in rows if r.get("status") == "completed"]
    dry_runs = [r for r in rows if r.get("status") == "dry_run"]
    total_tokens = sum((r.get("usage") or {}).get("total_tokens") or 0 for r in completed)
    known_costs = [r.get("estimated_cost_usd") for r in completed if r.get("estimated_cost_usd") is not None]
    lines = [
        "# Phase 1 API Cost Summary",
        "",
        f"- Output rows: `{len(rows)}`",
        f"- Completed API calls: `{len(completed)}`",
        f"- Dry-run rows: `{len(dry_runs)}`",
        f"- Total API tokens recorded: `{total_tokens}`",
        f"- Known estimated cost: `{round(sum(known_costs), 6) if known_costs else 'unknown_no_price_table'}`",
        "",
        "Cost is only estimated when `pricing_usd_per_1k_tokens` is configured for a model. The current OPAPI config does not store provider prices, so token usage is the reliable budget proxy.",
        "",
        "## Cost Controls in Script",
        "",
        "- Default mode is dry-run; use `--execute` to spend API calls.",
        "- `--max-calls` limits the number of new API calls.",
        "- Existing completed outputs are skipped unless `--rerun` is set.",
        "- Prompts use compressed evidence summaries and do not include raw image, point cloud, or large arrays.",
        "- One case-model pair produces all Phase 1 fields in one API call.",
        "",
    ]
    COST_SUMMARY_MD.write_text("\n".join(lines), encoding="utf-8")


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


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="+", help="Cases such as 001 024 or case_001 case_024")
    parser.add_argument("--selected30", action="store_true", help="Use processed/experiments/selected_30_drivefuzz_seeds.csv")
    parser.add_argument("--models", nargs="+", help="Model names from llm_backbone_config.yaml")
    parser.add_argument("--all-models", action="store_true", help="Use all active models in llm_backbone_config.yaml")
    parser.add_argument("--execute", action="store_true", help="Actually call the API. Default is dry-run.")
    parser.add_argument("--max-calls", type=int, default=12, help="Maximum new API calls. Use 0 for unlimited.")
    parser.add_argument("--rerun", action="store_true", help="Do not skip existing outputs.")
    parser.add_argument("--include-manual-draft", action="store_true", help="Include existing Codex-assisted draft pattern in the prompt.")
    parser.add_argument("--max-output-tokens", type=int, default=None, help="Override output token budget.")
    parser.add_argument("--no-dotenv", action="store_true", help="Do not load OPAPI_KEY from the COMPSAC .env file.")
    args = parser.parse_args()

    config = load_config()
    models_by_name = {model["name"]: model for model in config.get("models", [])}
    if args.all_models:
        selected_models = list(models_by_name)
    elif args.models:
        selected_models = args.models
    else:
        selected_models = config.get("pilot_recommendation", {}).get("models_first_try", [])
    for model_name in selected_models:
        if model_name not in models_by_name:
            raise SystemExit(f"Unknown model: {model_name}")

    if args.selected30:
        selected_cases = load_selected30_cases()
    elif args.cases:
        selected_cases = [normalize_case(case) for case in args.cases]
    else:
        selected_cases = config.get("pilot_recommendation", {}).get("seed_cases", [])

    PHASE1_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PHASE1_PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    root_patterns = load_root_pattern_index()
    api_key, api_key_source = load_api_key(config, use_dotenv=not args.no_dotenv)
    client = None
    if args.execute:
        if not api_key:
            raise SystemExit("Missing API key. Export OPAPI_KEY or keep the COMPSAC .env file available.")
        client = OpenAI(api_key=api_key, base_url=config["base_url"], timeout=config.get("default_generation", {}).get("timeout", 120))

    calls_made = 0
    results = []
    case_prompts: dict[str, str] = {}
    for case_id in selected_cases:
        if not (PROCESSED / "llm_inputs" / f"{case_id}.json").exists():
            print(f"skip missing llm_input: {case_id}")
            continue
        if not (PROCESSED / "critical_windows" / f"{case_id}_critical_window.json").exists():
            print(f"skip missing critical_window: {case_id}")
            continue
        evidence = build_case_evidence(case_id, root_patterns, args.include_manual_draft)
        case_prompts[case_id] = build_prompt(case_id, evidence)

    # Model-major order is intentional for the paper experiment: finish one LLM
    # backbone on all selected seeds, inspect quality/cost, then continue to the
    # next backbone. This prevents mixed partial runs and supports cost control.
    for model_name in selected_models:
        model = models_by_name[model_name]
        print(f"=== model {model_name} ===")
        for case_id in selected_cases:
            if case_id not in case_prompts:
                continue
            prompt = case_prompts[case_id]
            out = output_path(case_id, model_name)
            pp = prompt_path(case_id, model_name)
            pp.write_text(prompt, encoding="utf-8")
            if out.exists() and not args.rerun:
                existing = load_json(out)
                if args.execute:
                    should_skip = existing.get("status") == "completed" and existing.get("schema_valid") is True
                else:
                    should_skip = existing.get("status") in {"completed", "dry_run"}
                if should_skip:
                    print(f"skip existing {case_id} {model_name}: {existing.get('status')}")
                    results.append(existing)
                    continue
            if args.execute and args.max_calls and calls_made >= args.max_calls:
                result = make_result(case_id, model, prompt, "skipped_max_calls", None, "", None, {}, "max-calls reached", dry_run=False)
                write_json(out, result)
                results.append(result)
                continue

            if not args.execute:
                result = make_result(case_id, model, prompt, "dry_run", None, "", None, {}, "", dry_run=True)
                write_json(out, result)
                results.append(result)
                print(f"dry-run {case_id} {model_name} prompt_tokens~{result['prompt_estimated_tokens']}")
                continue

            started = time.time()
            try:
                assert client is not None
                content, raw_payload, usage = call_model(client, model, prompt, args.max_output_tokens)
                parsed = extract_json(content)
                if parsed is None:
                    status = "parse_failed"
                    error = "response is not valid JSON"
                else:
                    schema_valid, schema_errors = validate_phase1_response(parsed, case_id)
                    status = "completed" if schema_valid else "schema_invalid"
                    error = "; ".join(schema_errors)
                result = make_result(case_id, model, prompt, status, parsed, content, raw_payload, usage, error, dry_run=False)
                result["elapsed_sec"] = round(time.time() - started, 3)
                calls_made += 1
                print(f"{status} {case_id} {model_name} tokens={usage.get('total_tokens')}")
            except Exception as exc:  # noqa: BLE001 - provider-specific failures are part of experiment records.
                result = make_result(case_id, model, prompt, "error", None, "", None, {}, str(exc), dry_run=False)
                result["elapsed_sec"] = round(time.time() - started, 3)
                calls_made += 1
                print(f"error {case_id} {model_name}: {str(exc)[:120]}")
            write_json(out, result)
            results.append(result)

    write_results_csv()
    write_cost_summary()
    print(f"Wrote {RESULTS_CSV}")
    print(f"Wrote {COST_SUMMARY_MD}")
    print(f"New API calls made: {calls_made}")
    print(f"API key source: {api_key_source if args.execute else 'not_used_dry_run'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
