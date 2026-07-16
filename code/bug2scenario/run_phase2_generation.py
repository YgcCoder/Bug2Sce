#!/usr/bin/env python3
"""Run Phase 2 grounded candidate generation and local concretization.

Phase 2 uses the same LLM backbone as Phase 1:
- input: Phase 1 root-cause pattern + preservation constraints + original seed scenario;
- output: high-level candidate specs from the LLM;
- local code: deterministic concretizer + lightweight pre-validation;
- no CARLA, Autoware, or DriveFuzz execution.
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
from pathlib import Path, PurePosixPath
from typing import Any
import zipfile

import yaml
from openai import OpenAI


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "processed"
EXPERIMENTS = PROCESSED / "experiments"
CONFIG_PATH = EXPERIMENTS / "llm_backbone_config.yaml"
SELECTED_CSV = EXPERIMENTS / "selected_30_drivefuzz_seeds.csv"
PHASE1_OUTPUT_DIR = EXPERIMENTS / "phase1_api_outputs"
PHASE2_OUTPUT_DIR = EXPERIMENTS / "phase2_api_outputs"
PHASE2_PROMPT_DIR = EXPERIMENTS / "phase2_api_prompts"
PHASE2_CANDIDATE_DIR = EXPERIMENTS / "phase2_candidates"
RESULTS_CSV = EXPERIMENTS / "phase2_generation_results.csv"
COMPSAC_ENV = Path("<PRIVATE_CONFIG_ROOT>/compsac26-1原始代码/.env")


WEATHER_BOUNDS = {
    "cloud": (0, 100),
    "rain": (0, 100),
    "puddle": (0, 100),
    "wind": (0, 100),
    "fog": (0, 100),
    "wetness": (0, 100),
    "angle": (0, 360),
    "altitude": (-90, 90),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
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


def normalize_case(value: str) -> str:
    text = value.strip().lower().replace("case_", "")
    return f"case_{int(text):03d}"


def safe_name(value: str) -> str:
    return value.replace("/", "_").replace(":", "_")


def load_selected_cases() -> list[str]:
    with SELECTED_CSV.open(newline="", encoding="utf-8-sig") as handle:
        return [f"case_{int(row['Index']):03d}" for row in csv.DictReader(handle) if row.get("Index")]


def read_error_json_from_zip(case_id: str) -> dict[str, Any]:
    idx = int(case_id.replace("case_", ""))
    zip_path = ROOT / f"{idx}.zip"
    inner = f"{idx}/{idx}_error.json"
    with zipfile.ZipFile(zip_path) as archive:
        if inner not in set(archive.namelist()):
            raise FileNotFoundError(f"{inner} not found in {zip_path}")
        return json.loads(archive.read(inner))


def mission_from_seed(seed: dict[str, Any]) -> dict[str, Any]:
    return {
        "map": seed["map"],
        "spawn": {
            "x": seed["sp_x"],
            "y": seed["sp_y"],
            "z": seed["sp_z"],
            "pitch": seed.get("pitch", 0.0),
            "yaw": seed.get("yaw", 0.0),
            "roll": seed.get("roll", 0.0),
        },
        "destination": {
            "x": seed["wp_x"],
            "y": seed["wp_y"],
            "z": seed["wp_z"],
            "yaw": seed.get("wp_yaw", 0.0),
        },
    }


def convert_actor(actor: dict[str, Any]) -> dict[str, Any]:
    actor_type = {0: "vehicle", 1: "walker"}.get(actor.get("type"), "unknown")
    nav_type = {0: "linear", 1: "autopilot", 2: "immobile"}.get(actor.get("nav_type"), "unknown")
    converted = {
        "type": actor_type,
        "nav_type": nav_type,
        "speed": actor.get("speed", 0.0),
        "spawn": {
            "x": actor["sp_x"],
            "y": actor["sp_y"],
            "z": actor["sp_z"],
            "pitch": actor.get("sp_pitch", 0.0),
            "yaw": actor.get("sp_yaw", 0.0),
            "roll": actor.get("sp_roll", 0.0),
        },
    }
    if all(key in actor for key in ("dp_x", "dp_y", "dp_z", "dp_pitch", "dp_yaw", "dp_roll")):
        converted["destination"] = {
            "x": actor["dp_x"],
            "y": actor["dp_y"],
            "z": actor["dp_z"],
            "pitch": actor["dp_pitch"],
            "yaw": actor["dp_yaw"],
            "roll": actor["dp_roll"],
        }
    return converted


def convert_puddle(puddle: dict[str, Any]) -> dict[str, Any]:
    return {
        "level": puddle["level"],
        "location": {"x": puddle["sp_x"], "y": puddle["sp_y"], "z": puddle["sp_z"]},
        "size": {"x": puddle["size_x"], "y": puddle["size_y"], "z": puddle["size_z"]},
    }


def seed_scenario_from_error(case_id: str, error_json: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": f"seed-{case_id}",
        "schema": "drivefuzz-json-scenario-v1",
        "mission": mission_from_seed(error_json["seed"]),
        "weather": error_json.get("weather", {}),
        "actors": [convert_actor(actor) for actor in error_json.get("actors", [])],
        "puddles": [convert_puddle(puddle) for puddle in error_json.get("puddles", [])],
    }


def clamp(value: Any, low: float, high: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0.0
    if math.isnan(number) or math.isinf(number):
        number = 0.0
    return max(low, min(high, number))


def bounded_delta(value: Any, low: float, high: float) -> float:
    return clamp(value, low, high)


def compact_seed(scenario: dict[str, Any]) -> dict[str, Any]:
    return {
        "mission": scenario.get("mission"),
        "weather": scenario.get("weather"),
        "actors": [
            {
                "index": idx,
                "type": actor.get("type"),
                "nav_type": actor.get("nav_type"),
                "speed": actor.get("speed"),
                "spawn": actor.get("spawn"),
            }
            for idx, actor in enumerate(scenario.get("actors", []))
        ],
        "puddles": [
            {
                "index": idx,
                "level": puddle.get("level"),
                "location": puddle.get("location"),
                "size": puddle.get("size"),
            }
            for idx, puddle in enumerate(scenario.get("puddles", []))
        ],
    }


def truncate_text(value: Any, max_chars: int) -> str:
    text = str(value)
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def compact_list(value: Any, max_items: int = 5, max_chars: int = 260) -> list[str]:
    if not isinstance(value, list):
        return [truncate_text(value, max_chars)] if value not in (None, "") else []
    return [truncate_text(item, max_chars) for item in value[:max_items]]


def phase2_schema_text() -> str:
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


def build_prompt(case_id: str, model_name: str, phase1: dict[str, Any], seed: dict[str, Any], candidates_per_case: int) -> str:
    parsed = phase1.get("parsed_response") or {}
    compact_phase1 = {
        "case_id": parsed.get("case_id"),
        "fault_layer": parsed.get("fault_layer"),
        "causal_explanation": compact_list(parsed.get("causal_explanation"), max_items=4, max_chars=220),
        "root_cause_pattern": truncate_text(parsed.get("root_cause_pattern", ""), 520),
        "preservation_constraints": compact_list(parsed.get("preservation_constraints"), max_items=6, max_chars=180),
        "uncertainty": compact_list(parsed.get("uncertainty"), max_items=5, max_chars=180),
        "ready_for_phase2_generation": parsed.get("ready_for_phase2_generation"),
        "notes_for_validator": compact_list(parsed.get("notes_for_validator"), max_items=4, max_chars=160),
    }
    return "\n".join(
        [
            "You are the Phase 2 scenario amplifier for Bug2Scenario.",
            "Task: generate high-level, root-cause-preserving candidate scenario specs.",
            "",
            "Rules:",
            "- Return exactly one JSON object. Do not use markdown fences.",
            "- Use the Phase 1 root-cause pattern and preservation constraints from the same LLM backbone.",
            "- Do not invent new oracle labels. Preserve the intended oracle/failure pattern when evidence supports it.",
            "- Generate candidate specs only; local rule-based code will concretize them into DriveFuzz-style JSON.",
            "- Keep actor position offsets within [-8, 8] meters on x/y.",
            "- Keep actor speed_delta within [-3, 3].",
            "- Keep mission spawn/destination offsets within [-5, 5] meters, or set keep_original=true.",
            "- Keep weather deltas conservative: each weather_delta should be within [-20, 20].",
            "- Keep puddle level_delta within [-0.2, 0.2] and size_scale within [0.8, 1.2].",
            "- If Phase 1 is uncertainty-heavy, create conservative variants and preserve uncertainty in the output.",
            f"- Generate exactly {candidates_per_case} candidate_specs.",
            "- Keep every string short. Do not write explanatory paragraphs.",
            "- Each validation/uncertainty array must contain at most 3 short strings.",
            "- Use plain ASCII quotes and valid JSON syntax only.",
            "- Do not include trailing commas, comments, markdown, or extra keys.",
            "",
            "Return JSON schema:",
            phase2_schema_text(),
            "",
            "Input JSON:",
            json.dumps(
                {
                    "case_id": case_id,
                    "model_name": model_name,
                    "phase1_output": compact_phase1,
                    "seed_scenario": compact_seed(seed),
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


def validate_phase2_response(parsed: Any, case_id: str, candidates_per_case: int) -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not isinstance(parsed, dict):
        return False, ["parsed response is not a JSON object"]
    if parsed.get("case_id") != case_id:
        errors.append(f"case_id mismatch: expected {case_id}, got {parsed.get('case_id')}")
    specs = parsed.get("candidate_specs")
    if not isinstance(specs, list):
        errors.append("candidate_specs must be a list")
    elif len(specs) != candidates_per_case:
        errors.append(f"candidate_specs length must be {candidates_per_case}, got {len(specs)}")
    return not errors, errors


def apply_candidate_spec(seed: dict[str, Any], case_id: str, model_name: str, spec: dict[str, Any], index: int) -> tuple[dict[str, Any], dict[str, Any]]:
    scenario = json.loads(json.dumps(seed))
    safe_model = safe_name(model_name)
    scenario["name"] = f"bug2scenario-{case_id}-{safe_model}-cand_{index:03d}"
    modifications = spec.get("modifications") or {}
    applied: dict[str, Any] = {
        "weather_delta": {},
        "actor_mutations": [],
        "puddle_mutations": [],
        "mission_mutation": {},
        "safety_repairs": [],
    }

    for key, delta in (modifications.get("weather_delta") or {}).items():
        if key not in scenario.get("weather", {}) or key not in WEATHER_BOUNDS:
            continue
        low, high = WEATHER_BOUNDS[key]
        bounded = bounded_delta(delta, -20, 20)
        scenario["weather"][key] = clamp(float(scenario["weather"].get(key, 0)) + bounded, low, high)
        applied["weather_delta"][key] = bounded

    for mutation in modifications.get("actor_mutations") or []:
        if not isinstance(mutation, dict):
            continue
        actor_index = int(clamp(mutation.get("actor_index", 0), 0, max(0, len(scenario.get("actors", [])) - 1)))
        if actor_index >= len(scenario.get("actors", [])):
            continue
        actor = scenario["actors"][actor_index]
        offset = mutation.get("position_offset") or {}
        dx = bounded_delta(offset.get("x", 0.0), -8, 8)
        dy = bounded_delta(offset.get("y", 0.0), -8, 8)
        speed_delta = bounded_delta(mutation.get("speed_delta", 0.0), -3, 3)
        actor["spawn"]["x"] = float(actor["spawn"]["x"]) + dx
        actor["spawn"]["y"] = float(actor["spawn"]["y"]) + dy
        actor["speed"] = clamp(float(actor.get("speed", 0.0)) + speed_delta, 0, 30)
        applied["actor_mutations"].append({"actor_index": actor_index, "position_offset": {"x": dx, "y": dy}, "speed_delta": speed_delta})

    for mutation in modifications.get("puddle_mutations") or []:
        if not isinstance(mutation, dict) or not scenario.get("puddles"):
            continue
        puddle_index = int(clamp(mutation.get("puddle_index", 0), 0, len(scenario["puddles"]) - 1))
        puddle = scenario["puddles"][puddle_index]
        offset = mutation.get("location_offset") or {}
        dx = bounded_delta(offset.get("x", 0.0), -8, 8)
        dy = bounded_delta(offset.get("y", 0.0), -8, 8)
        level_delta = bounded_delta(mutation.get("level_delta", 0.0), -0.2, 0.2)
        size_scale = clamp(mutation.get("size_scale", 1.0), 0.8, 1.2)
        puddle["location"]["x"] = float(puddle["location"]["x"]) + dx
        puddle["location"]["y"] = float(puddle["location"]["y"]) + dy
        puddle["level"] = clamp(float(puddle.get("level", 0.0)) + level_delta, 0, 1)
        puddle["size"]["x"] = clamp(float(puddle["size"]["x"]) * size_scale, 0.1, 2000)
        puddle["size"]["y"] = clamp(float(puddle["size"]["y"]) * size_scale, 0.1, 2000)
        applied["puddle_mutations"].append(
            {"puddle_index": puddle_index, "location_offset": {"x": dx, "y": dy}, "level_delta": level_delta, "size_scale": size_scale}
        )

    mission_mutation = modifications.get("mission_mutation") or {}
    if mission_mutation and not mission_mutation.get("keep_original", True):
        for section_name, offset_name in [("spawn", "spawn_offset"), ("destination", "destination_offset")]:
            offset = mission_mutation.get(offset_name) or {}
            dx = bounded_delta(offset.get("x", 0.0), -5, 5)
            dy = bounded_delta(offset.get("y", 0.0), -5, 5)
            scenario["mission"][section_name]["x"] = float(scenario["mission"][section_name]["x"]) + dx
            scenario["mission"][section_name]["y"] = float(scenario["mission"][section_name]["y"]) + dy
            applied["mission_mutation"][offset_name] = {"x": dx, "y": dy}
    else:
        applied["mission_mutation"] = {"keep_original": True}

    # Deterministic pre-execution repair: avoid sending obviously invalid
    # ego-actor overlaps to the simulator. The repair is recorded in metadata.
    ego = (scenario.get("mission") or {}).get("spawn") or {}
    ego_x, ego_y = ego.get("x"), ego.get("y")
    if isinstance(ego_x, (int, float)) and isinstance(ego_y, (int, float)):
        min_distance = 2.5
        for actor_index, actor in enumerate(scenario.get("actors") or []):
            spawn = actor.get("spawn") or {}
            if not isinstance(spawn.get("x"), (int, float)) or not isinstance(spawn.get("y"), (int, float)):
                continue
            dx = float(spawn["x"]) - float(ego_x)
            dy = float(spawn["y"]) - float(ego_y)
            distance = math.hypot(dx, dy)
            if 0 < distance < min_distance:
                scale = min_distance / distance
                old = {"x": float(spawn["x"]), "y": float(spawn["y"])}
                spawn["x"] = float(ego_x) + dx * scale
                spawn["y"] = float(ego_y) + dy * scale
                applied["safety_repairs"].append(
                    {
                        "type": "actor_min_distance",
                        "actor_index": actor_index,
                        "old_spawn": old,
                        "new_spawn": {"x": spawn["x"], "y": spawn["y"]},
                        "old_distance": round(distance, 3),
                        "min_distance": min_distance,
                    }
                )
            elif distance == 0:
                old = {"x": float(spawn["x"]), "y": float(spawn["y"])}
                spawn["x"] = float(ego_x) + min_distance
                spawn["y"] = float(ego_y)
                applied["safety_repairs"].append(
                    {
                        "type": "actor_min_distance",
                        "actor_index": actor_index,
                        "old_spawn": old,
                        "new_spawn": {"x": spawn["x"], "y": spawn["y"]},
                        "old_distance": 0.0,
                        "min_distance": min_distance,
                    }
                )

    return scenario, applied


def pre_validate_scenario(seed: dict[str, Any], scenario: dict[str, Any]) -> tuple[bool, list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for field in ["name", "schema", "mission", "weather", "actors", "puddles"]:
        if field not in scenario:
            errors.append(f"missing field: {field}")
    if scenario.get("schema") != "drivefuzz-json-scenario-v1":
        errors.append("unsupported schema")
    mission = scenario.get("mission") or {}
    if not mission.get("map"):
        errors.append("mission map missing")
    for section in ["spawn", "destination"]:
        coords = (mission.get(section) or {})
        for key in ["x", "y", "z"]:
            if not isinstance(coords.get(key), (int, float)):
                errors.append(f"mission.{section}.{key} is not numeric")
    ego = (mission.get("spawn") or {})
    for idx, actor in enumerate(scenario.get("actors") or []):
        spawn = actor.get("spawn") or {}
        if not isinstance(spawn.get("x"), (int, float)) or not isinstance(spawn.get("y"), (int, float)):
            errors.append(f"actor {idx} spawn is not numeric")
            continue
        if ego.get("x") is not None and ego.get("y") is not None:
            distance = math.dist((float(ego["x"]), float(ego["y"])), (float(spawn["x"]), float(spawn["y"])))
            if distance < 2.0:
                errors.append(f"actor {idx} starts too close to ego: {distance:.2f}m")
        if float(actor.get("speed", 0.0)) < 0:
            errors.append(f"actor {idx} speed negative")
    if not scenario.get("actors"):
        warnings.append("no actors in candidate scenario")
    return not errors, errors, warnings


def output_path(case_id: str, model_name: str) -> Path:
    return PHASE2_OUTPUT_DIR / f"{case_id}__{safe_name(model_name)}.json"


def prompt_path(case_id: str, model_name: str) -> Path:
    return PHASE2_PROMPT_DIR / f"{case_id}__{safe_name(model_name)}.md"


def candidate_json_path(model_name: str, case_id: str, index: int) -> Path:
    return PHASE2_CANDIDATE_DIR / safe_name(model_name) / "json" / case_id / f"{case_id}__cand_{index:03d}.json"


def candidate_metadata_path(model_name: str, case_id: str, index: int) -> Path:
    return PHASE2_CANDIDATE_DIR / safe_name(model_name) / "metadata" / case_id / f"{case_id}__cand_{index:03d}.metadata.json"


def candidate_zip_path(model_name: str, case_id: str) -> Path:
    return PHASE2_CANDIDATE_DIR / safe_name(model_name) / "seed-artifact" / f"seed-artifact-{case_id}.zip"


def estimate_tokens(text: str) -> int:
    return math.ceil(len(text) / 4)


def build_request_params(model: dict[str, Any], prompt: str, max_tokens_override: int | None) -> dict[str, Any]:
    max_tokens = max_tokens_override or int(model.get("max_tokens", 0) or 0) or 2048
    params: dict[str, Any] = {
        "model": model["model_id"],
        "messages": [
            {"role": "system", "content": "You are a strict JSON generator for a scenario amplification experiment."},
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


def write_seed_artifact_zip(model_name: str, case_id: str, candidate_paths: list[Path]) -> Path:
    zip_path = candidate_zip_path(model_name, case_id)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in candidate_paths:
            archive.write(path, arcname=f"seed-artifact/{path.name}")
    return zip_path


def collect_results() -> list[dict[str, Any]]:
    rows = []
    if not PHASE2_OUTPUT_DIR.exists():
        return rows
    for path in sorted(PHASE2_OUTPUT_DIR.glob("*.json")):
        try:
            rows.append(json.loads(path.read_text(encoding="utf-8")))
        except json.JSONDecodeError:
            continue
    return rows


def write_results_csv() -> None:
    fields = [
        "case_id",
        "model_name",
        "status",
        "schema_valid",
        "phase1_ready",
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
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in collect_results():
            usage = item.get("usage") or {}
            writer.writerow(
                {
                    "case_id": item.get("case_id"),
                    "model_name": item.get("model_name"),
                    "status": item.get("status"),
                    "schema_valid": item.get("schema_valid"),
                    "phase1_ready": item.get("phase1_ready"),
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


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", required=True)
    parser.add_argument("--selected30", action="store_true")
    parser.add_argument("--cases", nargs="+")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--max-calls", type=int, default=12)
    parser.add_argument("--rerun", action="store_true")
    parser.add_argument("--candidates-per-case", type=int, default=2)
    parser.add_argument("--include-uncertain", action="store_true", help="Run Phase 2 for Phase 1 outputs marked uncertain as well as yes.")
    parser.add_argument("--include-not-ready", action="store_true", help="Also run cases marked no.")
    parser.add_argument("--max-output-tokens", type=int, default=None)
    parser.add_argument("--no-dotenv", action="store_true")
    args = parser.parse_args()

    config = load_config()
    models_by_name = {model["name"]: model for model in config.get("models", [])}
    for model_name in args.models:
        if model_name not in models_by_name:
            raise SystemExit(f"Unknown model: {model_name}")
    cases = load_selected_cases() if args.selected30 else [normalize_case(item) for item in (args.cases or [])]
    if not cases:
        raise SystemExit("No cases selected. Use --selected30 or --cases.")

    api_key, api_key_source = load_api_key(config, use_dotenv=not args.no_dotenv)
    client = None
    if args.execute:
        if not api_key:
            raise SystemExit("Missing API key. Export OPAPI_KEY or keep the COMPSAC .env file available.")
        client = OpenAI(api_key=api_key, base_url=config["base_url"], timeout=config.get("default_generation", {}).get("timeout", 120))

    calls_made = 0
    for model_name in args.models:
        model = models_by_name[model_name]
        print(f"=== phase2 model {model_name} ===")
        for case_id in cases:
            phase1_path = PHASE1_OUTPUT_DIR / f"{case_id}__{safe_name(model_name)}.json"
            if not phase1_path.exists():
                print(f"skip missing phase1: {case_id} {model_name}")
                continue
            phase1 = load_json(phase1_path)
            parsed_phase1 = phase1.get("parsed_response") or {}
            phase1_ready = parsed_phase1.get("ready_for_phase2_generation")
            if not args.include_not_ready:
                if phase1_ready == "no":
                    print(f"skip phase1 not ready: {case_id} {model_name}")
                    continue
                if phase1_ready == "uncertain" and not args.include_uncertain:
                    print(f"skip phase1 uncertain: {case_id} {model_name}")
                    continue
            error_json = read_error_json_from_zip(case_id)
            seed = seed_scenario_from_error(case_id, error_json)
            prompt = build_prompt(case_id, model_name, phase1, seed, args.candidates_per_case)
            pp = prompt_path(case_id, model_name)
            pp.parent.mkdir(parents=True, exist_ok=True)
            pp.write_text(prompt, encoding="utf-8")
            out = output_path(case_id, model_name)
            if out.exists() and not args.rerun:
                existing = load_json(out)
                if args.execute:
                    should_skip = existing.get("status") == "completed" and existing.get("schema_valid") is True
                else:
                    should_skip = existing.get("status") in {"completed", "dry_run"}
                if should_skip:
                    print(f"skip existing phase2 {case_id} {model_name}: {existing.get('status')}")
                    continue
            if args.execute and args.max_calls and calls_made >= args.max_calls:
                result = {
                    "case_id": case_id,
                    "model_name": model_name,
                    "status": "skipped_max_calls",
                    "schema_valid": None,
                    "phase1_ready": phase1_ready,
                    "num_candidates_requested": args.candidates_per_case,
                    "num_candidates_written": 0,
                    "num_pre_valid": 0,
                    "prompt_path": str(pp),
                    "output_path": str(out),
                    "prompt_estimated_tokens": estimate_tokens(prompt),
                    "usage": {},
                    "error_message": "max-calls reached",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                write_json(out, result)
                continue
            if not args.execute:
                result = {
                    "case_id": case_id,
                    "model_name": model_name,
                    "status": "dry_run",
                    "schema_valid": None,
                    "phase1_ready": phase1_ready,
                    "num_candidates_requested": args.candidates_per_case,
                    "num_candidates_written": 0,
                    "num_pre_valid": 0,
                    "prompt_path": str(pp),
                    "output_path": str(out),
                    "prompt_estimated_tokens": estimate_tokens(prompt),
                    "usage": {},
                    "error_message": "",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                write_json(out, result)
                print(f"dry-run phase2 {case_id} {model_name} prompt_tokens~{result['prompt_estimated_tokens']}")
                continue

            started = time.time()
            try:
                assert client is not None
                content, raw_payload, usage = call_model(client, model, prompt, args.max_output_tokens)
                parsed = extract_json(content)
                schema_valid, schema_errors = validate_phase2_response(parsed, case_id, args.candidates_per_case)
                status = "completed" if schema_valid else "schema_invalid"
                candidate_records: list[dict[str, Any]] = []
                candidate_paths: list[Path] = []
                pre_valid_count = 0
                if schema_valid and isinstance(parsed, dict):
                    for idx, spec in enumerate(parsed.get("candidate_specs") or [], start=1):
                        scenario, applied = apply_candidate_spec(seed, case_id, model_name, spec, idx)
                        pre_valid, errors, warnings = pre_validate_scenario(seed, scenario)
                        if pre_valid:
                            pre_valid_count += 1
                        json_path = candidate_json_path(model_name, case_id, idx)
                        metadata_path = candidate_metadata_path(model_name, case_id, idx)
                        write_json(json_path, scenario)
                        metadata = {
                            "case_id": case_id,
                            "model_name": model_name,
                            "candidate_index": idx,
                            "candidate_spec": spec,
                            "applied_modifications": applied,
                            "pre_validation": {"pre_valid": pre_valid, "errors": errors, "warnings": warnings},
                            "phase1_output_path": str(phase1_path),
                            "phase2_output_path": str(out),
                            "note": "Generated candidate scenario JSON for local DriveFuzz execution. It has not been executed in CARLA/Autoware.",
                        }
                        write_json(metadata_path, metadata)
                        candidate_records.append({"json_path": str(json_path), "metadata_path": str(metadata_path), **metadata})
                        candidate_paths.append(json_path)
                    zip_path = write_seed_artifact_zip(model_name, case_id, candidate_paths)
                else:
                    zip_path = None
                result = {
                    "case_id": case_id,
                    "model_name": model_name,
                    "workflow": "phase2_grounded_generation",
                    "status": status,
                    "schema_valid": schema_valid,
                    "schema_errors": schema_errors,
                    "phase1_ready": phase1_ready,
                    "num_candidates_requested": args.candidates_per_case,
                    "num_candidates_written": len(candidate_records),
                    "num_pre_valid": pre_valid_count,
                    "candidate_records": candidate_records,
                    "seed_artifact_zip": str(zip_path) if zip_path else "",
                    "prompt_path": str(pp),
                    "output_path": str(out),
                    "prompt_estimated_tokens": estimate_tokens(prompt),
                    "usage": usage,
                    "raw_response": content,
                    "parsed_response": parsed,
                    "raw_api_payload": raw_payload,
                    "error_message": "; ".join(schema_errors),
                    "elapsed_sec": round(time.time() - started, 3),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                calls_made += 1
                print(f"{status} phase2 {case_id} {model_name} tokens={usage.get('total_tokens')} candidates={len(candidate_records)} pre_valid={pre_valid_count}")
            except Exception as exc:  # noqa: BLE001
                result = {
                    "case_id": case_id,
                    "model_name": model_name,
                    "workflow": "phase2_grounded_generation",
                    "status": "error",
                    "schema_valid": False,
                    "phase1_ready": phase1_ready,
                    "num_candidates_requested": args.candidates_per_case,
                    "num_candidates_written": 0,
                    "num_pre_valid": 0,
                    "prompt_path": str(pp),
                    "output_path": str(out),
                    "prompt_estimated_tokens": estimate_tokens(prompt),
                    "usage": {},
                    "raw_response": "",
                    "parsed_response": None,
                    "raw_api_payload": None,
                    "error_message": str(exc),
                    "elapsed_sec": round(time.time() - started, 3),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                calls_made += 1
                print(f"error phase2 {case_id} {model_name}: {str(exc)[:120]}")
            write_json(out, result)
    write_results_csv()
    print(f"Wrote {RESULTS_CSV}")
    print(f"New Phase 2 API calls made: {calls_made}")
    print(f"API key source: {api_key_source if args.execute else 'not_used_dry_run'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
