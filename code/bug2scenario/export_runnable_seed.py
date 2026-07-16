#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any


BASE_DIR = Path("<WORKSPACE_ROOT>")
PROCESSED_DIR = BASE_DIR / "processed"
EXTRACTED_DIR = PROCESSED_DIR / "extracted"
OUTPUT_DIR = PROCESSED_DIR / "runnable_seeds"


ACTOR_TYPE_MAP = {
    0: "vehicle",
    1: "walker",
}

NAV_TYPE_MAP = {
    0: "linear",
    1: "autopilot",
    2: "immobile",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def mission_from_seed(seed: dict[str, Any]) -> dict[str, Any]:
    return {
        "map": seed["map"],
        "spawn": {
            "x": seed["sp_x"],
            "y": seed["sp_y"],
            "z": seed["sp_z"],
            "pitch": seed["pitch"],
            "yaw": seed["yaw"],
            "roll": seed["roll"],
        },
        "destination": {
            "x": seed["wp_x"],
            "y": seed["wp_y"],
            "z": seed["wp_z"],
            "yaw": seed["wp_yaw"],
        },
    }


def convert_actor(actor: dict[str, Any]) -> dict[str, Any]:
    converted = {
        "type": ACTOR_TYPE_MAP.get(actor.get("type"), "unknown"),
        "nav_type": NAV_TYPE_MAP.get(actor.get("nav_type"), "unknown"),
        "speed": actor.get("speed", 0.0),
        "spawn": {
            "x": actor["sp_x"],
            "y": actor["sp_y"],
            "z": actor["sp_z"],
            "pitch": actor["sp_pitch"],
            "yaw": actor["sp_yaw"],
            "roll": actor["sp_roll"],
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
        "location": {
            "x": puddle["sp_x"],
            "y": puddle["sp_y"],
            "z": puddle["sp_z"],
        },
        "size": {
            "x": puddle["size_x"],
            "y": puddle["size_y"],
            "z": puddle["size_z"],
        },
    }


def build_scenario(case_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    case_dir = EXTRACTED_DIR / f"case_{case_id}"
    raw = load_json(case_dir / f"{int(case_id)}_error.json")
    scenario = {
        "name": f"scenario-case_{case_id}",
        "schema": "drivefuzz-json-scenario-v1",
        "mission": mission_from_seed(raw["seed"]),
        "weather": raw["weather"],
        "actors": [convert_actor(actor) for actor in raw.get("actors", [])],
        "puddles": [convert_puddle(puddle) for puddle in raw.get("puddles", [])],
    }
    return scenario, raw


def write_outputs(case_id: str, scenario: dict[str, Any], raw: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUTPUT_DIR / f"scenario-case_{case_id}.json"
    json_path.write_text(json.dumps(scenario, indent=2, ensure_ascii=False) + "\n")

    zip_path = OUTPUT_DIR / f"seed-artifact-case_{case_id}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(f"seed-artifact/scenario-case_{case_id}.json", json.dumps(scenario, indent=2, ensure_ascii=False) + "\n")

    metadata = {
        "case_id": f"case_{case_id}",
        "generated_from": str(EXTRACTED_DIR / f"case_{case_id}" / f"{int(case_id)}_error.json"),
        "scenario_json": str(json_path),
        "zip_artifact": str(zip_path),
        "events": raw.get("events", {}),
        "note": "This runnable seed is a schema-aligned export of the original DriveFuzz failure seed. It is not an LLM-generated amplified scenario.",
    }
    metadata_path = OUTPUT_DIR / f"scenario-case_{case_id}.metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")


def update_readme(case_id: str) -> None:
    readme_path = OUTPUT_DIR / "README.md"
    readme_path.write_text(
        "\n".join(
            [
                "# Runnable Seeds",
                "",
                f"- Generated seed: `scenario-case_{case_id}.json`",
                f"- Matching artifact zip: `seed-artifact-case_{case_id}.zip`",
                "",
                "## What To Give The Local Runner",
                "",
                "- If your local runner accepts a raw DriveFuzz scenario JSON, give it `processed/runnable_seeds/scenario-case_"
                f"{case_id}.json`.",
                "- If your local workflow expects a seed-artifact style zip, give it `processed/runnable_seeds/seed-artifact-case_"
                f"{case_id}.zip`.",
                "",
                "## Important Note",
                "",
                "- This file is generated from the original failure seed metadata in `processed/extracted/case_"
                f"{case_id}/{int(case_id)}_error.json`.",
                "- It is for local runnable scenario input.",
                "- It is not the same as `processed/llm_inputs/*.json` or `processed/prompts/*.md`, which are only for LLM analysis.",
                "",
            ]
        )
        + "\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a schema-aligned runnable DriveFuzz seed from an extracted case.")
    parser.add_argument("--case", default="001", help="Case id like 001, 024, 027, 013.")
    args = parser.parse_args()

    case_id = args.case.zfill(3)
    scenario, raw = build_scenario(case_id)
    write_outputs(case_id, scenario, raw)
    update_readme(case_id)


if __name__ == "__main__":
    main()
