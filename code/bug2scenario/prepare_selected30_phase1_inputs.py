#!/usr/bin/env python3
"""Prepare selected-30 Phase 1 inputs without API calls or simulation.

This script is intentionally local-only:
- does not run CARLA, Autoware, or DriveFuzz;
- does not modify source zip files;
- processes selected cases from processed/experiments/selected_30_drivefuzz_seeds.csv;
- writes compact case cards, LLM inputs, oracle consistency, critical windows,
  and a readiness table for cost-controlled Phase 1 API calls.

For disk safety, newly extracted case directories are removed by default after
their summaries are written. Use --keep-extracted if you need to inspect CSVs.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "processed"
EXPERIMENTS = PROCESSED / "experiments"
EXTRACTED = PROCESSED / "extracted"
LLM_INPUTS = PROCESSED / "llm_inputs"
CASE_CARDS = PROCESSED / "case_cards"
CRITICAL_WINDOWS = PROCESSED / "critical_windows"
SELECTED_CSV = EXPERIMENTS / "selected_30_drivefuzz_seeds.csv"


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


build = load_module(ROOT / "scripts" / "build_drivefuzz_pipeline.py", "build_drivefuzz_pipeline_selected30")
v2 = load_module(ROOT / "scripts" / "generate_stage5_prompt_v2.py", "generate_stage5_prompt_v2_selected30")
oracle_mod = load_module(ROOT / "scripts" / "check_oracle_consistency.py", "check_oracle_consistency_selected30")


def normalize_case(value: str) -> int:
    text = value.strip().lower().replace("case_", "")
    return int(text)


def load_selected_cases() -> list[int]:
    with SELECTED_CSV.open(newline="", encoding="utf-8-sig") as handle:
        return [int(row["Index"]) for row in csv.DictReader(handle) if row.get("Index")]


def selected_row_index() -> dict[int, dict[str, str]]:
    with SELECTED_CSV.open(newline="", encoding="utf-8-sig") as handle:
        return {int(row["Index"]): row for row in csv.DictReader(handle) if row.get("Index")}


def read_oracle_rows() -> dict[str, dict[str, str]]:
    path = PROCESSED / "oracle_consistency.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["case_id"]: row for row in csv.DictReader(handle)}


def ensure_dirs() -> None:
    for path in [PROCESSED, EXPERIMENTS, EXTRACTED, LLM_INPUTS, CASE_CARDS, CRITICAL_WINDOWS]:
        path.mkdir(parents=True, exist_ok=True)


def extract_case(case_id: int) -> bool:
    """Extract one case. Returns True when this script created the extraction."""
    dest = EXTRACTED / f"case_{case_id:03d}"
    if (dest / "manifest.json").exists():
        return False
    zip_path = ROOT / f"{case_id}.zip"
    if not zip_path.exists():
        raise FileNotFoundError(f"Missing source zip: {zip_path}")
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        for member in archive.infolist():
            if member.is_dir():
                continue
            parts = [part for part in PurePosixPath(member.filename).parts if part]
            relative_parts = parts[1:] if len(parts) > 1 else parts
            if not relative_parts:
                continue
            output_path = dest / Path(*relative_parts)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, output_path.open("wb") as target:
                shutil.copyfileobj(source, target)
    if not (dest / "manifest.json").exists():
        raise FileNotFoundError(f"Extraction did not produce manifest.json for case_{case_id:03d}")
    return True


def build_topic_matches(case: dict[str, Any]) -> dict[str, Any]:
    return {spec["topic_name"]: build.find_topic_match(case, spec) for spec in build.TOPIC_SPECS}


def patch_llm_input(case_id: int, oracle_row: dict[str, str]) -> dict[str, Any]:
    path = LLM_INPUTS / f"case_{case_id:03d}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["oracle_consistency"] = {
        "status": oracle_row.get("consistency_status", "unknown"),
        "dataset_group": oracle_row.get("dataset_group", "unknown"),
        "error_json_group": oracle_row.get("error_json_group", "unknown"),
        "conflict_details": oracle_row.get("conflict_details", "unknown"),
        "suggested_action": oracle_row.get("suggested_action", "inspect_case_metadata"),
    }
    cleaned_limits = []
    for item in data.get("known_limitations", []):
        if item == "Only case_001 was fully decoded with convert_sensor_data_field.py in this pipeline run.":
            continue
        cleaned_limits.append(item)
    cleaned_limits.extend(
        [
            "Sensor and perception topics are summarized where available; large raw arrays are not included in prompts.",
            "Dataset.xlsx and error.json oracle labels are compared separately; conflicts are preserved rather than resolved automatically.",
        ]
    )
    if oracle_row.get("consistency_status") != "consistent":
        cleaned_limits.append(
            "Dataset.xlsx and error.json are inconsistent for this case; Phase 1 must explicitly mark uncertainty."
        )
    data["known_limitations"] = sorted(set(cleaned_limits))
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return data


def relevant_label(llm_input: dict[str, Any], events: dict[str, Any], label: str, group_letter: str) -> bool:
    fault = llm_input.get("fault_label", {})
    group = str(fault.get("group", ""))
    return bool(fault.get(label)) or bool(events.get({"red_light": "red", "lane_invasion": "lane_invasion", "stuck": "stuck"}.get(label, label))) or group_letter in group.split("+")


def last_timestamp(*series: list[dict[str, Any]]) -> float | None:
    values = []
    for rows in series:
        values.extend(row.get("timestamp") for row in rows if row.get("timestamp") is not None)
    return max(values) if values else None


def add_generic_red_window(case_dir: Path, result: dict[str, Any], target_ts: float | None) -> None:
    if "red_light_window" in result:
        return
    traffic_light_rows = v2.load_traffic_lights(v2.find_topic(case_dir, "traffic_lights"))
    final_waypoint_rows = v2.load_final_waypoints(v2.find_topic(case_dir, "final_waypoints"))
    start = max(0.0, (target_ts or 0.0) - 5.0)
    tl_near = v2.rows_in_window(traffic_light_rows, start, target_ts or start) if target_ts is not None else traffic_light_rows[:5]
    state_samples = [
        {
            "timestamp": v2.ts_str(row.get("timestamp")),
            "traffic_light_count": row.get("count"),
            "state_histogram": row.get("state_histogram"),
            "sample": row.get("sample"),
        }
        for row in tl_near[:5]
    ]
    nearest_fw = v2.nearest_before(final_waypoint_rows, target_ts or 0.0) if target_ts is not None else None
    events = result.get("error_json_events", {})
    result["red_light_window"] = {
        "red_light_violation_from_error_json": bool(events.get("red")),
        "red_light_violation_timestamp": "unknown",
        "traffic_lights_topic_exists": bool(traffic_light_rows),
        "traffic_light_state_samples": state_samples or "unknown",
        "route_light_relation_confirmed": "unknown",
        "stop_line_crossing_confirmed": "unknown",
        "nearest_final_waypoints_stop_line_ids": nearest_fw.get("stop_line_ids") if nearest_fw else [],
        "notes": "Traffic light states may be available, but route-light relation and stop-line crossing are not confirmed by the current summaries.",
    }


def add_generic_stuck_window(case_dir: Path, result: dict[str, Any], error_json: dict[str, Any]) -> None:
    if "stuck_window" in result:
        return
    pose_rows = v2.load_current_pose(v2.find_topic(case_dir, "current_pose"))
    vehicle_status_rows = v2.load_vehicle_status(v2.find_topic(case_dir, "vehicle_status"))
    vehicle_cmd_rows = v2.load_vehicle_cmd(v2.find_topic(case_dir, "vehicle_cmd"))
    final_waypoint_rows = v2.load_final_waypoints(v2.find_topic(case_dir, "final_waypoints"))
    collision_rows = v2.load_collision(v2.find_topic(case_dir, "collision"))
    total_duration = v2.safe_float(error_json.get("elapsed_time"))
    last_ts = last_timestamp(pose_rows, vehicle_status_rows, vehicle_cmd_rows, final_waypoint_rows)
    last_start = max(0.0, (last_ts or 0.0) - 60.0) if last_ts is not None else None
    pose_window = v2.rows_in_window(pose_rows, last_start or 0.0, last_ts or 0.0) if last_ts is not None else []
    status_window = v2.rows_in_window(vehicle_status_rows, last_start or 0.0, last_ts or 0.0) if last_ts is not None else []
    cmd_window = v2.rows_in_window(vehicle_cmd_rows, last_start or 0.0, last_ts or 0.0) if last_ts is not None else []
    fw_window = v2.rows_in_window(final_waypoint_rows, last_start or 0.0, last_ts or 0.0) if last_ts is not None else []
    displacement = None
    if pose_window:
        start_pose = pose_window[0]
        end_pose = pose_window[-1]
        if all(start_pose.get(k) is not None for k in ("x", "y", "z")) and all(end_pose.get(k) is not None for k in ("x", "y", "z")):
            displacement = round(
                v2.math.dist(
                    (start_pose["x"], start_pose["y"], start_pose["z"]),
                    (end_pose["x"], end_pose["y"], end_pose["z"]),
                ),
                3,
            )
    events = result.get("error_json_events", {})
    result["stuck_window"] = {
        "stuck_from_error_json": bool(events.get("stuck")),
        "total_duration_sec": round(total_duration, 3) if total_duration is not None else None,
        "last_60_seconds_window": {
            "start_timestamp": v2.ts_str(last_start),
            "end_timestamp": v2.ts_str(last_ts),
            "ego_movement_distance": v2.compute_path_distance(pose_window),
            "ego_start_to_end_displacement": displacement,
            "velocity_stats": v2.summarize_numeric([row.get("velocity") for row in status_window if row.get("velocity") is not None]),
            "vehicle_status_control_stats": {
                "throttle": v2.summarize_numeric([row.get("throttle") for row in status_window if row.get("throttle") is not None]),
                "brake": v2.summarize_numeric([row.get("brake") for row in status_window if row.get("brake") is not None]),
                "steer": v2.summarize_numeric([row.get("steer") for row in status_window if row.get("steer") is not None]),
            },
            "vehicle_cmd_stats": {
                "accel_cmd": v2.summarize_numeric([row.get("accel_cmd") for row in cmd_window if row.get("accel_cmd") is not None]),
                "brake_cmd": v2.summarize_numeric([row.get("brake_cmd") for row in cmd_window if row.get("brake_cmd") is not None]),
                "steer_cmd": v2.summarize_numeric([row.get("steer_cmd") for row in cmd_window if row.get("steer_cmd") is not None]),
            },
            "final_waypoints_present": bool(fw_window),
            "final_waypoint_count_stats": v2.summarize_numeric(
                [row.get("waypoint_count") for row in fw_window if row.get("waypoint_count") is not None]
            ),
        },
        "collision_or_red_light_interference": {
            "error_json_collision": bool(events.get("crash")),
            "error_json_red": bool(events.get("red")),
            "collision_topic_exists": bool(collision_rows),
        },
    }


def add_generic_lane_window(case_dir: Path, result: dict[str, Any], oracle_row: dict[str, str]) -> None:
    lane_path = v2.find_topic(case_dir, "lane_waypoints_array")
    final_path = v2.find_topic(case_dir, "final_waypoints")
    events = result.get("error_json_events", {})
    result["lane_invasion_window"] = {
        "lane_invasion_from_dataset": oracle_row.get("dataset_lane_invasion"),
        "lane_invasion_from_error_json": bool(events.get("lane_invasion")),
        "lane_waypoints_array_topic_exists": bool(lane_path),
        "final_waypoints_topic_exists": bool(final_path),
        "explicit_lane_boundary_crossing_evidence": "unknown",
        "notes": "No dedicated lane-boundary crossing evidence was extracted; do not infer lane invasion mechanism unless additional evidence confirms it.",
    }


def build_selected_critical_window(case_id: int, llm_input: dict[str, Any], oracle_row: dict[str, str]) -> dict[str, Any]:
    case_key = f"{case_id:03d}"
    case_dir = EXTRACTED / f"case_{case_key}"
    error_json = json.loads((case_dir / f"{case_id}_error.json").read_text(encoding="utf-8"))
    result = v2.build_critical_window(case_key, llm_input, oracle_row)
    events = result.get("error_json_events", {}) or {}
    collision_rows = v2.load_collision(v2.find_topic(case_dir, "collision"))
    pose_rows = v2.load_current_pose(v2.find_topic(case_dir, "current_pose"))
    status_rows = v2.load_vehicle_status(v2.find_topic(case_dir, "vehicle_status"))
    target_ts = collision_rows[0]["timestamp"] if collision_rows else last_timestamp(pose_rows, status_rows)

    if relevant_label(llm_input, events, "red_light", "R"):
        add_generic_red_window(case_dir, result, target_ts)
    if relevant_label(llm_input, events, "stuck", "S"):
        add_generic_stuck_window(case_dir, result, error_json)
    if relevant_label(llm_input, events, "lane_invasion", "L"):
        add_generic_lane_window(case_dir, result, oracle_row)
    if oracle_row.get("consistency_status") != "consistent":
        result["label_conflict"] = {
            "dataset_group": oracle_row.get("dataset_group", "unknown"),
            "error_json_group": oracle_row.get("error_json_group", "unknown"),
            "conflict_details": oracle_row.get("conflict_details", ""),
            "needs_manual_review": True,
            "guidance": "Use this case as uncertainty-aware Phase 1 input unless manual review resolves the conflict.",
        }
    return result


def write_selected_topic_availability(rows: list[dict[str, str]]) -> None:
    path = EXPERIMENTS / "selected30_topic_availability.csv"
    fieldnames = ["case_id", "topic_name", "found_or_not", "matched_file_path", "file_type", "notes"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_readiness(rows: list[dict[str, Any]]) -> None:
    csv_path = EXPERIMENTS / "selected30_phase1_readiness.csv"
    md_path = EXPERIMENTS / "selected30_phase1_readiness.md"
    fieldnames = [
        "case_id",
        "zip_file",
        "dataset_group",
        "oracle_consistency_status",
        "llm_input",
        "case_card",
        "critical_window",
        "ready_for_phase1_api",
        "notes",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# Selected 30 Phase 1 Readiness",
        "",
        "This file tracks whether each selected seed has compact local evidence ready for Phase 1 API calls.",
        "",
        "| Case | Group | Oracle Consistency | Ready | Notes |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['case_id']} | {row['dataset_group']} | {row['oracle_consistency_status']} | {row['ready_for_phase1_api']} | {row['notes']} |"
        )
    lines.extend(
        [
            "",
            "## API Cost Rule",
            "",
            "Run `scripts/run_phase1_api.py` in dry-run mode first. Use `--execute --max-calls` only for a small pilot batch.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")


def prepare_cases(case_ids: list[int], keep_extracted: bool, rerun: bool, dry_run: bool) -> int:
    ensure_dirs()
    missing = [case_id for case_id in case_ids if not (ROOT / f"{case_id}.zip").exists()]
    if missing:
        raise SystemExit(f"Missing selected zip files: {', '.join(str(item) + '.zip' for item in missing)}")

    if dry_run:
        print(f"dry-run selected cases: {' '.join(f'{case_id:03d}' for case_id in case_ids)}")
        return 0

    # Keep oracle consistency aligned with the currently present numeric zips.
    oracle_mod.write_outputs(oracle_mod.build_rows())
    oracle_rows = read_oracle_rows()
    selected_rows = selected_row_index()

    _dataset_rows, dataset_by_index, _dataset_md = build.load_dataset()
    readiness_rows: list[dict[str, Any]] = []
    topic_rows: list[dict[str, str]] = []

    for idx, case_id in enumerate(case_ids, start=1):
        case_label = f"case_{case_id:03d}"
        if (
            not rerun
            and (LLM_INPUTS / f"{case_label}.json").exists()
            and (CASE_CARDS / f"{case_label}.md").exists()
            and (CRITICAL_WINDOWS / f"{case_label}_critical_window.json").exists()
        ):
            oracle_row = oracle_rows.get(case_label, {})
            readiness_rows.append(
                {
                    "case_id": case_label,
                    "zip_file": f"{case_id}.zip",
                    "dataset_group": selected_rows.get(case_id, {}).get("Group", "unknown"),
                    "oracle_consistency_status": oracle_row.get("consistency_status", "unknown"),
                    "llm_input": "present",
                    "case_card": "present",
                    "critical_window": "present",
                    "ready_for_phase1_api": "yes",
                    "notes": "existing outputs reused",
                }
            )
            print(f"[{idx}/{len(case_ids)}] skip existing {case_label}")
            continue

        extracted_by_script = False
        try:
            print(f"[{idx}/{len(case_ids)}] preparing {case_label}")
            extracted_by_script = extract_case(case_id)
            case = build.load_case_static(case_id)
            matches = build_topic_matches(case)
            summaries = build.build_case_summaries([case], dataset_by_index, {case_id: matches})
            build.write_case_outputs([case], summaries)
            oracle_row = oracle_rows.get(case_label, {})
            llm_input = patch_llm_input(case_id, oracle_row)
            critical = build_selected_critical_window(case_id, llm_input, oracle_row)
            (CRITICAL_WINDOWS / f"{case_label}_critical_window.json").write_text(
                json.dumps(critical, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            for topic_name, match in matches.items():
                topic_rows.append(
                    {
                        "case_id": case_label,
                        "topic_name": topic_name,
                        "found_or_not": "true" if match.found else "false",
                        "matched_file_path": match.matched_file_path,
                        "file_type": match.file_type,
                        "notes": match.notes if match.found else "topic absent or not matched by selected fuzzy keywords",
                    }
                )
            readiness_rows.append(
                {
                    "case_id": case_label,
                    "zip_file": f"{case_id}.zip",
                    "dataset_group": selected_rows.get(case_id, {}).get("Group", "unknown"),
                    "oracle_consistency_status": oracle_row.get("consistency_status", "unknown"),
                    "llm_input": "present",
                    "case_card": "present",
                    "critical_window": "present",
                    "ready_for_phase1_api": "yes" if oracle_row.get("consistency_status") == "consistent" else "yes_with_uncertainty",
                    "notes": "prepared",
                }
            )
        except Exception as exc:  # noqa: BLE001 - preprocessing should continue across cases.
            readiness_rows.append(
                {
                    "case_id": case_label,
                    "zip_file": f"{case_id}.zip",
                    "dataset_group": selected_rows.get(case_id, {}).get("Group", "unknown"),
                    "oracle_consistency_status": oracle_rows.get(case_label, {}).get("consistency_status", "unknown"),
                    "llm_input": "missing",
                    "case_card": "missing",
                    "critical_window": "missing",
                    "ready_for_phase1_api": "no",
                    "notes": f"error: {exc}",
                }
            )
            print(f"  error {case_label}: {exc}")
        finally:
            if extracted_by_script and not keep_extracted:
                shutil.rmtree(EXTRACTED / case_label, ignore_errors=True)

    # Add existing topic availability for skipped cases when extracted data is still present.
    for case_id in case_ids:
        case_label = f"case_{case_id:03d}"
        if any(row["case_id"] == case_label for row in topic_rows):
            continue
        case_dir = EXTRACTED / case_label
        if (case_dir / "manifest.json").exists():
            try:
                case = build.load_case_static(case_id)
                matches = build_topic_matches(case)
                for topic_name, match in matches.items():
                    topic_rows.append(
                        {
                            "case_id": case_label,
                            "topic_name": topic_name,
                            "found_or_not": "true" if match.found else "false",
                            "matched_file_path": match.matched_file_path,
                            "file_type": match.file_type,
                            "notes": match.notes if match.found else "topic absent or not matched by selected fuzzy keywords",
                        }
                    )
            except Exception:
                pass

    write_selected_topic_availability(topic_rows)
    write_readiness(readiness_rows)

    ready_count = sum(1 for row in readiness_rows if str(row["ready_for_phase1_api"]).startswith("yes"))
    print(f"ready_for_phase1_api: {ready_count}/{len(readiness_rows)}")
    print(f"wrote {EXPERIMENTS / 'selected30_phase1_readiness.csv'}")
    print(f"wrote {EXPERIMENTS / 'selected30_phase1_readiness.md'}")
    return 0 if ready_count == len(case_ids) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="+", help="Optional subset, e.g. 001 024 027.")
    parser.add_argument("--keep-extracted", action="store_true", help="Keep newly extracted CSV directories under processed/extracted/.")
    parser.add_argument("--rerun", action="store_true", help="Regenerate outputs even when llm_input/case_card/critical_window already exist.")
    parser.add_argument("--dry-run", action="store_true", help="Only list selected cases; do not extract or write outputs.")
    args = parser.parse_args()

    case_ids = [normalize_case(item) for item in args.cases] if args.cases else load_selected_cases()
    return prepare_cases(case_ids, keep_extracted=args.keep_extracted, rerun=args.rerun, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
