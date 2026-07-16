#!/usr/bin/env python3
"""Build Codex-assisted Phase 1 root-cause pattern artifacts.

This script does not call external LLM APIs and does not run simulation.
It standardizes the current first-round seed cases into the files needed by
the Bug2Scenario candidate-generation stage.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "processed"
EXPERIMENTS = PROCESSED / "experiments"
TARGET_CASES = ["case_001", "case_024", "case_027", "case_013"]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_by_case(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return {row["case_id"]: row for row in csv.DictReader(f)}


def parse_saved_llm_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    match = re.search(r"\{.*\}\s*$", text, flags=re.S)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def scenario_summary(llm_input: dict[str, Any]) -> str:
    config = llm_input.get("scenario_config", {})
    mission = config.get("mission", {})
    return (
        f"Map={config.get('map', 'unknown')}; "
        f"mission_start={mission.get('start', 'unknown')}; "
        f"mission_goal={mission.get('goal', 'unknown')}; "
        f"actors={config.get('actors', 'unknown')}; "
        f"weather={config.get('weather', 'unknown')}; "
        f"puddles={config.get('puddles', 'unknown')}"
    )


def evidence_summary(case_id: str, critical: dict[str, Any]) -> str:
    if case_id in {"case_001", "case_024", "case_013"}:
        window = critical.get("collision_window", {})
        speed = window.get("ego_speed_before_collision", {}).get("window_velocity_stats", {})
        obj = window.get("closest_available_object_info", {})
        waypoints = window.get("final_waypoints_before_collision", {})
        return (
            f"collision_window={window.get('window_start', 'unknown')}..{window.get('window_end', 'unknown')}; "
            f"velocity_stats={speed}; "
            f"closest_object_distance={obj.get('distance_to_ego', 'unknown')}; "
            f"final_waypoints={waypoints.get('waypoint_count_stats', 'unknown')}; "
            f"blocked_true_count_nonzero={waypoints.get('blocked_true_count_nonzero', 'unknown')}"
        )
    if case_id == "case_027":
        window = critical.get("stuck_window", {}).get("last_60_seconds_window", {})
        return (
            f"last_60s_velocity={window.get('velocity_stats', 'unknown')}; "
            f"last_60s_displacement={window.get('ego_start_to_end_displacement', 'unknown')}; "
            f"movement_distance={window.get('ego_movement_distance', 'unknown')}; "
            f"final_waypoints_present={window.get('final_waypoints_present', 'unknown')}; "
            f"final_waypoints={window.get('final_waypoint_count_stats', 'unknown')}"
        )
    return "unknown"


def pattern_for_case(
    case_id: str,
    llm_input: dict[str, Any],
    critical: dict[str, Any],
    oracle: dict[str, str],
    saved_llm: dict[str, Any] | None,
) -> dict[str, Any]:
    fault = llm_input.get("fault_label", {})
    group = fault.get("group", oracle.get("dataset_group", "unknown"))
    consistency = oracle.get("consistency_status", "unknown")

    base: dict[str, Any] = {
        "case_id": case_id,
        "phase1_source": "codex_assisted_manual_phase1",
        "external_api_used": False,
        "raw_oracle_labels": {
            "collision": int(fault.get("collision", 0)),
            "stuck": int(fault.get("stuck", 0)),
            "lane_invasion": int(fault.get("lane_invasion", 0)),
            "red_light": int(fault.get("red_light", 0)),
            "group": group,
        },
        "corrected_group": group if consistency == "consistent" else "unknown_needs_manual_review",
        "oracle_consistency_status": consistency,
        "scenario_summary": scenario_summary(llm_input),
        "critical_window": evidence_summary(case_id, critical),
        "causal_explanation": "",
        "root_cause_pattern": "",
        "preservation_constraints": [],
        "modifiable_factors": [],
        "non_modifiable_conditions": [],
        "candidate_generation_status": "ready" if consistency == "consistent" else "uncertainty_sample_only",
        "confidence": "low",
        "known_limitations": [],
    }

    if case_id == "case_001":
        llm_pattern = (saved_llm or {}).get("possible_root_cause_pattern")
        base.update(
            {
                "causal_explanation": (
                    "A collision was confirmed by both Dataset.xlsx and error.json. "
                    "The collision window contains a nearby actor, available detection/prediction summaries, "
                    "final waypoints, and low ego speed near the collision. The evidence does not localize the "
                    "root cause to a specific Autoware layer."
                ),
                "root_cause_pattern": llm_pattern
                or (
                    "Collision with a nearby actor while the ego vehicle was stopped or nearly stopped; "
                    "module-level attribution remains unknown."
                ),
                "preservation_constraints": [
                    "The candidate should remain a collision-only case with no red-light, lane-invasion, or stuck oracle.",
                    "A nearby actor should be present near the ego route before the collision.",
                    "The critical window should include object perception/prediction evidence before collision.",
                    "The candidate should record final waypoints before collision.",
                    "Post-execution validation must inspect ego speed and actor relation before collision.",
                ],
                "modifiable_factors": ["actor_position", "actor_behavior", "weather", "puddles"],
                "non_modifiable_conditions": [
                    "Town01 mission remains executable",
                    "nearby actor interaction is preserved",
                    "collision oracle must be triggered",
                    "no red-light/lane-invasion/stuck confounder is introduced",
                ],
                "confidence": "medium",
                "known_limitations": [
                    "Direct planner decision logs are unavailable.",
                    "The evidence does not prove whether the collision actor was correctly associated by perception.",
                    "Vehicle_cmd is all zero while vehicle_status shows movement/braking, so controller attribution is uncertain.",
                ],
            }
        )
    elif case_id == "case_024":
        base.update(
            {
                "causal_explanation": (
                    "Dataset.xlsx and error.json consistently report a compound collision and red-light case. "
                    "The collision window shows ego movement, braking evidence, a close object, available detection/prediction, "
                    "and waypoint blockage events. Traffic-light states are available, but the current summary cannot confirm "
                    "route-light relation or stop-line crossing."
                ),
                "root_cause_pattern": (
                    "Compound collision and red-light symptom with ego approaching a traffic-light region and interacting "
                    "with a nearby object; the collision evidence is stronger than the red-light causal mechanism because "
                    "route-light relation and stop-line crossing are still unknown."
                ),
                "preservation_constraints": [
                    "The candidate should preserve both collision and red-light oracle checks when possible.",
                    "Traffic lights must exist in the scenario.",
                    "A nearby object/actor should remain close to the ego route before collision.",
                    "Post-execution validation must confirm whether the ego route is controlled by the red light.",
                    "Post-execution validation must confirm stop-line crossing before claiming a red-light causal mechanism.",
                ],
                "modifiable_factors": ["actor_position", "actor_type", "weather", "puddles", "mission_route"],
                "non_modifiable_conditions": [
                    "traffic-light topic/evidence remains available",
                    "collision oracle remains compatible with original case",
                    "red-light relation must be checked instead of assumed",
                ],
                "confidence": "medium_low",
                "known_limitations": [
                    "Red-light violation timestamp is unknown.",
                    "Route-light relation is unknown.",
                    "Stop-line crossing is unknown.",
                    "Vehicle_cmd is all zero while vehicle_status shows movement/braking, so controller attribution is uncertain.",
                ],
            }
        )
    elif case_id == "case_027":
        base.update(
            {
                "causal_explanation": (
                    "Dataset.xlsx and error.json consistently report stuck/immobility. "
                    "In the last 60 seconds, ego velocity is zero, start-to-end displacement is near zero, "
                    "final waypoints remain present, and no collision or red-light interference is reported."
                ),
                "root_cause_pattern": (
                    "Immobility while a mission and final waypoints remain available: the ego vehicle stays stationary "
                    "in the final window without collision or red-light interference. The exact module-level cause remains unknown."
                ),
                "preservation_constraints": [
                    "The candidate should trigger stuck/immobility without collision or red-light confounders.",
                    "Last-window ego velocity should remain near zero.",
                    "Last-window displacement should remain near zero.",
                    "Final waypoints should remain available during the stuck window.",
                    "Post-execution validation must distinguish planner/control immobility from invalid initialization.",
                ],
                "modifiable_factors": ["actor_position", "mission_route", "weather", "puddles"],
                "non_modifiable_conditions": [
                    "stuck oracle must be triggered",
                    "no collision/red-light confounder",
                    "final waypoints remain present",
                    "last-window velocity remains zero or near zero",
                ],
                "confidence": "medium",
                "known_limitations": [
                    "Module-level attribution between planning, control, simulator, and map remains unknown.",
                    "The movement_distance statistic and near-zero displacement should be manually checked for interpretation.",
                ],
            }
        )
    elif case_id == "case_013":
        base.update(
            {
                "causal_explanation": (
                    "Dataset.xlsx labels this case as C+L, but error.json reports speeding only and does not confirm "
                    "collision or lane invasion. This case is useful as an uncertainty/label-conflict sample, not as a clean seed."
                ),
                "root_cause_pattern": (
                    "No clean C+L root-cause pattern should be extracted until manual review resolves the conflict between "
                    "Dataset.xlsx and error.json."
                ),
                "preservation_constraints": [
                    "Do not use this case as confirmed collision or lane-invasion ground truth.",
                    "Any generated candidate from this case must be marked as uncertainty-driven.",
                    "Manual review must resolve whether the collision topic indicates a real collision event.",
                    "Manual review must find lane-boundary crossing evidence before using lane invasion as a root-cause condition.",
                ],
                "modifiable_factors": [],
                "non_modifiable_conditions": [
                    "dataset/error_json conflict must be preserved in experiment metadata",
                    "not counted as clean same-root-cause seed",
                ],
                "candidate_generation_status": "not_ready_for_clean_generation",
                "confidence": "low",
                "known_limitations": [
                    "Dataset label C+L conflicts with error_json speeding-only summary.",
                    "Explicit lane-boundary crossing evidence is unknown.",
                    "This case should only test uncertainty awareness unless manually corrected.",
                ],
            }
        )

    return base


def write_curated_pool(rows: list[dict[str, Any]], manual: dict[str, dict[str, str]], oracle: dict[str, dict[str, str]]) -> None:
    fields = [
        "case_id",
        "raw_oracle_labels",
        "raw_failure_group",
        "manual_corrected_group",
        "scenario_available",
        "log_available",
        "rosbag_available",
        "trace_available",
        "auto_identification_error",
        "error_type",
        "phase1_usable",
        "ambiguity_level",
        "selected_as_seed",
        "selection_reason",
    ]
    out = EXPERIMENTS / "curated_failure_pool.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for p in rows:
            case_id = p["case_id"]
            o = oracle.get(case_id, {})
            m = manual.get(case_id, {})
            consistent = o.get("consistency_status") == "consistent"
            writer.writerow(
                {
                    "case_id": case_id,
                    "raw_oracle_labels": json.dumps(p["raw_oracle_labels"], ensure_ascii=False),
                    "raw_failure_group": p["raw_oracle_labels"]["group"],
                    "manual_corrected_group": p["corrected_group"],
                    "scenario_available": "yes",
                    "log_available": "partial" if case_id == "case_001" else "not_checked",
                    "rosbag_available": "yes" if case_id == "case_001" else "not_checked",
                    "trace_available": "summary_available",
                    "auto_identification_error": "no" if consistent else "yes_or_unresolved",
                    "error_type": "none" if consistent else "oracle_label_conflict",
                    "phase1_usable": "yes" if p["candidate_generation_status"] == "ready" else "uncertainty_only",
                    "ambiguity_level": "low" if consistent else "high",
                    "selected_as_seed": "yes",
                    "selection_reason": m.get("recommended_next_action", "first_round_seed_subset"),
                }
            )


def write_summary(patterns: list[dict[str, Any]]) -> None:
    lines = [
        "# Phase 1 Root-Cause Pattern Summary",
        "",
        "This file summarizes the current Codex-assisted Phase 1 output.",
        "No external API was called in this step. The results are based on existing case cards, oracle consistency checks, critical-window summaries, and the saved webpage LLM output for `case_001`.",
        "",
        "## Scope",
        "",
        "- Seed subset: `case_001`, `case_024`, `case_027`, `case_013`",
        "- Purpose: prepare the first API-based candidate generation round",
        "- Output files: `curated_failure_pool.csv` and `root_cause_patterns.json`",
        "",
        "## Case Status",
        "",
    ]
    for p in patterns:
        lines.extend(
            [
                f"### {p['case_id']}",
                "",
                f"- Group: `{p['raw_oracle_labels']['group']}`",
                f"- Oracle consistency: `{p['oracle_consistency_status']}`",
                f"- Candidate generation status: `{p['candidate_generation_status']}`",
                f"- Confidence: `{p['confidence']}`",
                f"- Pattern: {p['root_cause_pattern']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Next Step",
            "",
            "Use `root_cause_patterns.json` as the input to the next script: `root-cause pattern -> API candidate scenario generation -> generated_candidates.csv`.",
            "For paper claims, mark this artifact as Phase 1 preparation rather than completed API experiment results.",
            "",
        ]
    )
    (EXPERIMENTS / "phase1_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    EXPERIMENTS.mkdir(parents=True, exist_ok=True)
    manual = read_csv_by_case(PROCESSED / "manual_review_sheet.csv")
    oracle = read_csv_by_case(PROCESSED / "oracle_consistency.csv")
    saved_llm = parse_saved_llm_json(PROCESSED / "manual_llm_results/proposal/case_001_raw_response.md")

    patterns = []
    for case_id in TARGET_CASES:
        llm_input = read_json(PROCESSED / "llm_inputs" / f"{case_id}.json")
        critical = read_json(PROCESSED / "critical_windows" / f"{case_id}_critical_window.json")
        patterns.append(pattern_for_case(case_id, llm_input, critical, oracle[case_id], saved_llm if case_id == "case_001" else None))

    (EXPERIMENTS / "root_cause_patterns.json").write_text(
        json.dumps(patterns, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_curated_pool(patterns, manual, oracle)
    write_summary(patterns)

    print(f"Wrote {EXPERIMENTS / 'root_cause_patterns.json'}")
    print(f"Wrote {EXPERIMENTS / 'curated_failure_pool.csv'}")
    print(f"Wrote {EXPERIMENTS / 'phase1_summary.md'}")


if __name__ == "__main__":
    main()
