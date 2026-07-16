#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any


csv.field_size_limit(sys.maxsize)

BASE_DIR = Path("<WORKSPACE_ROOT>")
PROCESSED_DIR = BASE_DIR / "processed"
EXTRACTED_DIR = PROCESSED_DIR / "extracted"
LLM_INPUT_DIR = PROCESSED_DIR / "llm_inputs"
PROMPT_V2_DIR = PROCESSED_DIR / "prompts" / "proposal_v2"
MANUAL_DIR = PROCESSED_DIR / "manual_llm_run_package"
CRITICAL_DIR = PROCESSED_DIR / "critical_windows"
REPORT_PATH = PROCESSED_DIR / "stage5_prompt_v2_report.md"

CASE_ORDER = ["001", "024", "027", "013"]


def safe_float(value: Any) -> float | None:
    if value in (None, "", "unknown"):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(result) or math.isinf(result):
        return None
    return result


def timestamp_from_row(row: dict[str, str]) -> float | None:
    sec = safe_float(row.get("timestamp_sec"))
    nsec = safe_float(row.get("timestamp_nsec"))
    if sec is None:
        return None
    return sec + ((nsec or 0.0) / 1_000_000_000.0)


def ts_str(ts: float | None) -> str:
    if ts is None:
        return "unknown"
    return f"{ts:.9f}".rstrip("0").rstrip(".")


def parse_json_cell(value: str | None, default: Any) -> Any:
    if value in (None, ""):
        return default
    try:
        return json.loads(value)
    except Exception:
        return default


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def find_topic(case_dir: Path, keyword: str) -> Path | None:
    topics_dir = case_dir / "topics"
    matches = sorted(topics_dir.glob(f"*{keyword}*.csv"))
    return matches[0] if matches else None


def summarize_numeric(values: list[float]) -> dict[str, float | None]:
    clean = [v for v in values if v is not None]
    if not clean:
        return {"min": None, "max": None, "mean": None, "last": None}
    return {
        "min": round(min(clean), 6),
        "max": round(max(clean), 6),
        "mean": round(statistics.fmean(clean), 6),
        "last": round(clean[-1], 6),
    }


def nearest_before(rows: list[dict[str, Any]], target: float) -> dict[str, Any] | None:
    candidates = [row for row in rows if row["timestamp"] is not None and row["timestamp"] <= target]
    if not candidates:
        return None
    return max(candidates, key=lambda row: row["timestamp"])


def rows_in_window(rows: list[dict[str, Any]], start: float, end: float) -> list[dict[str, Any]]:
    return [row for row in rows if row["timestamp"] is not None and start <= row["timestamp"] <= end]


def load_vehicle_status(path: Path | None) -> list[dict[str, Any]]:
    if not path:
        return []
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            control = parse_json_cell(row.get("control"), {})
            rows.append(
                {
                    "timestamp": timestamp_from_row(row),
                    "velocity": safe_float(row.get("velocity")),
                    "throttle": safe_float(control.get("throttle")),
                    "brake": safe_float(control.get("brake")),
                    "steer": safe_float(control.get("steer")),
                }
            )
    return rows


def load_vehicle_cmd(path: Path | None) -> list[dict[str, Any]]:
    if not path:
        return []
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            steer_cmd = parse_json_cell(row.get("steer_cmd"), {})
            accel_cmd = parse_json_cell(row.get("accel_cmd"), {})
            brake_cmd = parse_json_cell(row.get("brake_cmd"), {})
            ctrl_cmd = parse_json_cell(row.get("ctrl_cmd"), {})
            rows.append(
                {
                    "timestamp": timestamp_from_row(row),
                    "steer_cmd": safe_float(steer_cmd.get("steer")),
                    "accel_cmd": safe_float(accel_cmd.get("accel")),
                    "brake_cmd": safe_float(brake_cmd.get("brake")),
                    "linear_velocity_cmd": safe_float(ctrl_cmd.get("linear_velocity")),
                }
            )
    return rows


def load_count_series(path: Path | None, field: str = "objects") -> list[dict[str, Any]]:
    if not path:
        return []
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            objects = parse_json_cell(row.get(field), []) or []
            labels = []
            if isinstance(objects, list):
                for obj in objects[:5]:
                    if isinstance(obj, dict):
                        label = obj.get("label")
                        if label not in (None, ""):
                            labels.append(str(label))
            rows.append(
                {
                    "timestamp": timestamp_from_row(row),
                    "count": len(objects) if isinstance(objects, list) else None,
                    "labels_sample": labels,
                }
            )
    return rows


def load_current_pose(path: Path | None) -> list[dict[str, Any]]:
    if not path:
        return []
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            pose = parse_json_cell(row.get("pose"), {})
            position = pose.get("position", {}) if isinstance(pose, dict) else {}
            rows.append(
                {
                    "timestamp": timestamp_from_row(row),
                    "x": safe_float(position.get("x")),
                    "y": safe_float(position.get("y")),
                    "z": safe_float(position.get("z")),
                }
            )
    return rows


def load_collision(path: Path | None) -> list[dict[str, Any]]:
    if not path:
        return []
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            impulse = parse_json_cell(row.get("normal_impulse"), {})
            coords = [safe_float(impulse.get(axis)) for axis in ("x", "y", "z")] if isinstance(impulse, dict) else []
            magnitude = None
            if len(coords) == 3 and all(value is not None for value in coords):
                magnitude = math.sqrt(sum(value * value for value in coords if value is not None))
            rows.append(
                {
                    "timestamp": timestamp_from_row(row),
                    "other_actor_id": row.get("other_actor_id") or "unknown",
                    "impulse_magnitude": magnitude,
                }
            )
    return rows


def load_final_waypoints(path: Path | None) -> list[dict[str, Any]]:
    if not path:
        return []
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            waypoints = parse_json_cell(row.get("waypoints"), []) or []
            stop_line_ids: list[int] = []
            blocked_waypoints = 0
            if isinstance(waypoints, list):
                for wp in waypoints:
                    if not isinstance(wp, dict):
                        continue
                    stop_line = wp.get("stop_line_id")
                    if isinstance(stop_line, int) and stop_line != 0:
                        stop_line_ids.append(stop_line)
                    wpstate = wp.get("wpstate")
                    if isinstance(wpstate, dict) and safe_float(wpstate.get("event_state")) not in (None, 0.0):
                        blocked_waypoints += 1
            rows.append(
                {
                    "timestamp": timestamp_from_row(row),
                    "waypoint_count": len(waypoints) if isinstance(waypoints, list) else None,
                    "is_blocked": str(row.get("is_blocked", "")).lower() == "true",
                    "blocked_waypoint_events": blocked_waypoints,
                    "closest_object_distance": safe_float(row.get("closest_object_distance")),
                    "closest_object_velocity": safe_float(row.get("closest_object_velocity")),
                    "stop_line_ids": sorted(set(stop_line_ids))[:10],
                }
            )
    return rows


def load_objects(path: Path | None) -> list[dict[str, Any]]:
    if not path:
        return []
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            objects = parse_json_cell(row.get("objects"), []) or []
            simplified = []
            if isinstance(objects, list):
                for obj in objects:
                    if not isinstance(obj, dict):
                        continue
                    pose = obj.get("pose", {})
                    position = pose.get("position", {}) if isinstance(pose, dict) else {}
                    simplified.append(
                        {
                            "id": obj.get("id"),
                            "classification": obj.get("classification"),
                            "x": safe_float(position.get("x")),
                            "y": safe_float(position.get("y")),
                            "z": safe_float(position.get("z")),
                        }
                    )
            rows.append({"timestamp": timestamp_from_row(row), "objects": simplified})
    return rows


def load_traffic_lights(path: Path | None) -> list[dict[str, Any]]:
    if not path:
        return []
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            lights = parse_json_cell(row.get("traffic_lights"), []) or []
            states = {}
            sample = []
            if isinstance(lights, list):
                for light in lights:
                    if not isinstance(light, dict):
                        continue
                    state = light.get("state")
                    states[str(state)] = states.get(str(state), 0) + 1
                    if len(sample) < 5:
                        sample.append({"id": light.get("id"), "state": state})
            rows.append(
                {
                    "timestamp": timestamp_from_row(row),
                    "count": len(lights) if isinstance(lights, list) else None,
                    "state_histogram": states,
                    "sample": sample,
                }
            )
    return rows


def summarize_series_window(rows: list[dict[str, Any]], key: str, start: float, end: float) -> dict[str, Any]:
    window = rows_in_window(rows, start, end)
    values = [safe_float(row.get(key)) for row in window]
    return {
        "window_start": ts_str(start),
        "window_end": ts_str(end),
        "rows": len(window),
        "stats": summarize_numeric([value for value in values if value is not None]),
    }


def summarize_count_window(rows: list[dict[str, Any]], start: float, end: float) -> dict[str, Any]:
    window = rows_in_window(rows, start, end)
    counts = [safe_float(row.get("count")) for row in window]
    labels = sorted({label for row in window for label in row.get("labels_sample", [])})[:10]
    return {
        "rows": len(window),
        "count_stats": summarize_numeric([value for value in counts if value is not None]),
        "labels_sample": labels,
    }


def compute_closest_object(
    pose_rows: list[dict[str, Any]],
    object_rows: list[dict[str, Any]],
    target_ts: float,
) -> dict[str, Any] | str:
    pose = nearest_before(pose_rows, target_ts)
    objects_row = nearest_before(object_rows, target_ts)
    if not pose or not objects_row:
        return "unknown"
    px = pose.get("x")
    py = pose.get("y")
    if px is None or py is None:
        return "unknown"
    best = None
    for obj in objects_row.get("objects", []):
        ox = obj.get("x")
        oy = obj.get("y")
        if ox is None or oy is None:
            continue
        distance = math.dist((px, py), (ox, oy))
        if distance < 1.5:
            continue
        if best is None or distance < best["distance_to_ego"]:
            best = {
                "object_id": obj.get("id"),
                "classification": obj.get("classification"),
                "distance_to_ego": round(distance, 3),
                "position": {"x": round(ox, 3), "y": round(oy, 3), "z": round(obj.get("z") or 0.0, 3)},
            }
    return best or "unknown"


def compute_path_distance(rows: list[dict[str, Any]]) -> float | None:
    total = 0.0
    prev = None
    for row in rows:
        point = (row.get("x"), row.get("y"), row.get("z"))
        if any(value is None for value in point):
            continue
        if prev is not None:
            total += math.dist(prev, point)  # type: ignore[arg-type]
        prev = point  # type: ignore[assignment]
    return round(total, 3) if prev is not None else None


def compact_trace_summary(trace_summary: dict[str, Any]) -> dict[str, Any]:
    sensing = trace_summary.get("sensing", {})
    perception = trace_summary.get("perception", {})
    planning = trace_summary.get("planning", {})
    actuation = trace_summary.get("actuation", {})
    oracle = trace_summary.get("oracle", {})
    image_raw = sensing.get("image_raw") or {}
    points_raw = sensing.get("points_raw") or {}
    imu = sensing.get("imu") or {}
    detection = perception.get("detection_fusion_objects") or {}
    prediction = perception.get("prediction_objects") or {}
    current_pose = perception.get("current_pose") or {}
    lane_waypoints = planning.get("lane_waypoints_array") or {}
    final_waypoints = planning.get("final_waypoints") or {}
    vehicle_cmd = actuation.get("vehicle_cmd") or {}
    vehicle_status = actuation.get("vehicle_status") or {}
    collision = oracle.get("collision") or {}
    traffic_lights = oracle.get("traffic_lights") or {}
    objects = oracle.get("objects") or {}
    odometry = oracle.get("odometry") or {}
    error_json_events = oracle.get("error_json_events") or {}
    return {
        "sensing": {
            "image_raw": {
                "exists": image_raw.get("exists"),
                "encoding": image_raw.get("encoding"),
                "height": image_raw.get("height"),
                "width": image_raw.get("width"),
                "decode_status": image_raw.get("decode_status"),
            },
            "points_raw": {
                "exists": points_raw.get("exists"),
                "width": points_raw.get("width"),
                "fields": points_raw.get("fields"),
                "decode_status": points_raw.get("decode_status"),
            },
            "imu": {
                "exists": imu.get("exists"),
                "first_timestamp": imu.get("first_timestamp"),
                "last_timestamp": imu.get("last_timestamp"),
            },
        },
        "perception": {
            "detection": {
                "exists": detection.get("exists"),
                "first_timestamp": detection.get("first_timestamp"),
                "last_timestamp": detection.get("last_timestamp"),
                "object_count_range": detection.get("object_count_range"),
                "labels_sample": detection.get("labels_sample"),
            },
            "prediction": {
                "exists": prediction.get("exists"),
                "first_timestamp": prediction.get("first_timestamp"),
                "last_timestamp": prediction.get("last_timestamp"),
                "object_count_range": prediction.get("object_count_range"),
                "labels_sample": prediction.get("labels_sample"),
            },
            "current_pose": {
                "exists": current_pose.get("exists"),
                "first_timestamp": current_pose.get("first_timestamp"),
                "last_timestamp": current_pose.get("last_timestamp"),
            },
        },
        "planning": {
            "lane_waypoints_array": {
                "exists": lane_waypoints.get("exists"),
                "primary_lane_waypoint_count_range": lane_waypoints.get("primary_lane_waypoint_count_range"),
            },
            "final_waypoints": {
                "exists": final_waypoints.get("exists"),
                "waypoint_count_range": final_waypoints.get("waypoint_count_range"),
                "blocked_true_count_sample": final_waypoints.get("blocked_true_count_sample"),
            },
        },
        "actuation": {
            "vehicle_cmd": {
                "exists": vehicle_cmd.get("exists"),
                "steer_cmd_range": vehicle_cmd.get("steer_cmd_range"),
                "accel_cmd_range": vehicle_cmd.get("accel_cmd_range"),
                "brake_cmd_range": vehicle_cmd.get("brake_cmd_range"),
            },
            "vehicle_status": {
                "exists": vehicle_status.get("exists"),
                "velocity_range": vehicle_status.get("velocity_range"),
                "throttle_range": vehicle_status.get("throttle_range"),
                "brake_range": vehicle_status.get("brake_range"),
            },
        },
        "oracle": {
            "collision": {
                "exists": collision.get("exists"),
                "first_timestamp": collision.get("first_timestamp"),
                "last_timestamp": collision.get("last_timestamp"),
                "other_actor_ids_sample": collision.get("other_actor_ids_sample"),
            },
            "traffic_lights": {
                "exists": traffic_lights.get("exists"),
                "state_sample": traffic_lights.get("state_sample"),
            },
            "objects": {
                "exists": objects.get("exists"),
                "object_count_range": objects.get("object_count_range"),
                "labels_sample": objects.get("labels_sample"),
            },
            "odometry": {
                "exists": odometry.get("exists"),
                "first_timestamp": odometry.get("first_timestamp"),
                "last_timestamp": odometry.get("last_timestamp"),
            },
            "error_json_events": error_json_events,
        },
    }


def format_prompt(case_payload: dict[str, Any]) -> str:
    schema = {
        "fault_layer": "sensing | perception | planning | actuation | simulator | map | unknown",
        "fault_component": "string or unknown",
        "causal_chain": ["step 1", "step 2", "step 3"],
        "supporting_evidence": [{"evidence_id": "string", "description": "string"}],
        "uncertain_or_missing_evidence": ["string"],
        "possible_root_cause_pattern": "string or unknown",
        "whether_suitable_for_Bug2Scenario": "yes | no | uncertain",
        "same_root_cause_scenario_variants": ["string"],
        "pre_execution_validation_rules": ["string"],
        "post_execution_validation_rules": ["string"],
        "confidence_score": 0.0,
    }
    return "\n".join(
        [
            f"# Proposal V2 Prompt For {case_payload['case_id']}",
            "",
            "Use only the structured evidence below and return exactly one JSON object.",
            "",
            "## Rules",
            "",
            "- Only use the given evidence.",
            "- Do not invent missing sensor, perception, planning, actuation, or oracle evidence.",
            "- If evidence is insufficient, write `unknown`.",
            "- If oracle consistency has a conflict, explicitly describe it in `uncertain_or_missing_evidence`.",
            "- Do not treat topic existence as proof of correct perception or planning.",
            "- Do not infer red-light violation causal mechanism unless route-light relation and stop-line crossing evidence are available.",
            "- Do not infer lane invasion unless lane invasion evidence or lane boundary crossing evidence is available.",
            "- Do not infer stuck mechanism only from the stuck label; use last-window velocity or movement evidence if available.",
            "- If `vehicle_cmd` is all zero but `vehicle_status` shows movement, mark this as uncertain instead of assuming controller behavior.",
            "- If `Dataset.xlsx` and `error.json` disagree, treat the case as an uncertainty sample.",
            "",
            "## Case JSON",
            "",
            "```json",
            json.dumps(case_payload, indent=2, ensure_ascii=False),
            "```",
            "",
            "## Return JSON Schema",
            "",
            "```json",
            json.dumps(schema, indent=2, ensure_ascii=False),
            "```",
            "",
            "Return exactly one JSON object that conforms to the schema above. Do not add markdown fences, explanations, or extra text outside the JSON object.",
            "",
        ]
    )


def build_known_limitations(case_id: str) -> list[str]:
    limits = [
        "Dataset labels and error.json oracle events are compared separately; conflicts are preserved rather than resolved automatically.",
        "Sensor and perception topics were decoded for selected cases where available; large raw arrays are not included in prompts, only summaries are used.",
        "Large CSV topics are summarized with bounded scans or critical-window extraction for reproducibility and memory safety.",
    ]
    if case_id == "013":
        limits.insert(
            1,
            "Dataset.xlsx and error.json disagree for this case; treat it as an uncertainty sample and do not assume the dataset label is confirmed ground truth.",
        )
    return limits


def build_critical_window(case_id: str, llm_input: dict[str, Any], oracle_row: dict[str, str]) -> dict[str, Any]:
    case_dir = EXTRACTED_DIR / f"case_{case_id}"
    error_json = load_json(case_dir / f"{int(case_id)}_error.json")
    vehicle_status_rows = load_vehicle_status(find_topic(case_dir, "vehicle_status"))
    vehicle_cmd_rows = load_vehicle_cmd(find_topic(case_dir, "vehicle_cmd"))
    detection_rows = load_count_series(find_topic(case_dir, "detection__fusion_tools__objects"))
    prediction_rows = load_count_series(find_topic(case_dir, "prediction__motion_predictor__objects"))
    pose_rows = load_current_pose(find_topic(case_dir, "current_pose"))
    collision_rows = load_collision(find_topic(case_dir, "collision"))
    final_waypoint_rows = load_final_waypoints(find_topic(case_dir, "final_waypoints"))
    object_rows = load_objects(find_topic(case_dir, "carla__objects"))
    traffic_light_rows = load_traffic_lights(find_topic(case_dir, "traffic_lights"))

    events = error_json.get("events", {})
    result: dict[str, Any] = {
        "case_id": f"case_{case_id}",
        "dataset_group": llm_input["fault_label"]["group"],
        "oracle_consistency_status": oracle_row["consistency_status"],
        "error_json_events": events,
    }

    if collision_rows:
        collision_ts = collision_rows[0]["timestamp"]
        start = max(0.0, (collision_ts or 0.0) - 5.0)
        status_window = rows_in_window(vehicle_status_rows, start, collision_ts or start)
        cmd_window = rows_in_window(vehicle_cmd_rows, start, collision_ts or start)
        detect_window = summarize_count_window(detection_rows, start, collision_ts or start)
        predict_window = summarize_count_window(prediction_rows, start, collision_ts or start)
        fw_window = rows_in_window(final_waypoint_rows, start, collision_ts or start)
        fw_counts = [safe_float(row.get("waypoint_count")) for row in fw_window]
        blocked_rows = sum(1 for row in fw_window if row.get("is_blocked"))
        blocked_events = sum(int(row.get("blocked_waypoint_events") or 0) for row in fw_window)
        pre_status = nearest_before(vehicle_status_rows, collision_ts or 0.0)
        pre_cmd = nearest_before(vehicle_cmd_rows, collision_ts or 0.0)
        pre_fw = nearest_before(final_waypoint_rows, collision_ts or 0.0)
        result["collision_window"] = {
            "collision_timestamp": ts_str(collision_ts),
            "window_start": ts_str(start),
            "window_end": ts_str(collision_ts),
            "collision_topic_exists": True,
            "error_json_crash": bool(events.get("crash")),
            "ego_speed_before_collision": {
                "nearest_pre_collision_velocity": pre_status.get("velocity") if pre_status else None,
                "window_velocity_stats": summarize_numeric([row.get("velocity") for row in status_window if row.get("velocity") is not None]),
            },
            "ego_control_before_collision": {
                "vehicle_status_control_stats": {
                    "throttle": summarize_numeric([row.get("throttle") for row in status_window if row.get("throttle") is not None]),
                    "brake": summarize_numeric([row.get("brake") for row in status_window if row.get("brake") is not None]),
                    "steer": summarize_numeric([row.get("steer") for row in status_window if row.get("steer") is not None]),
                },
                "vehicle_cmd_stats": {
                    "accel_cmd": summarize_numeric([row.get("accel_cmd") for row in cmd_window if row.get("accel_cmd") is not None]),
                    "brake_cmd": summarize_numeric([row.get("brake_cmd") for row in cmd_window if row.get("brake_cmd") is not None]),
                    "steer_cmd": summarize_numeric([row.get("steer_cmd") for row in cmd_window if row.get("steer_cmd") is not None]),
                    "linear_velocity_cmd": summarize_numeric(
                        [row.get("linear_velocity_cmd") for row in cmd_window if row.get("linear_velocity_cmd") is not None]
                    ),
                },
                "nearest_pre_collision_vehicle_cmd": pre_cmd,
            },
            "detected_object_count_before_collision": detect_window,
            "predicted_object_count_before_collision": predict_window,
            "final_waypoints_before_collision": {
                "rows": len(fw_window),
                "waypoint_count_stats": summarize_numeric([value for value in fw_counts if value is not None]),
                "blocked_true_count_rows": blocked_rows,
                "blocked_true_count_nonzero": blocked_rows > 0 or blocked_events > 0,
                "blocked_waypoint_event_total": blocked_events,
                "nearest_pre_collision_row": pre_fw,
            },
            "closest_available_object_info": compute_closest_object(pose_rows, object_rows, collision_ts or 0.0),
            "evidence_of_braking_or_stopping": {
                "vehicle_status_brake_nonzero": any((row.get("brake") or 0.0) > 0.01 for row in status_window),
                "vehicle_cmd_brake_nonzero": any((row.get("brake_cmd") or 0.0) > 0.01 for row in cmd_window),
                "speed_decreases_within_window": (
                    bool(status_window)
                    and status_window[0].get("velocity") is not None
                    and status_window[-1].get("velocity") is not None
                    and (status_window[-1]["velocity"] < status_window[0]["velocity"])
                ),
            },
        }

    if case_id == "024":
        collision_ts = collision_rows[0]["timestamp"] if collision_rows else None
        tl_near = []
        if collision_ts is not None:
            tl_near = rows_in_window(traffic_light_rows, max(0.0, collision_ts - 5.0), collision_ts)
        state_samples = []
        for row in tl_near[:5]:
            state_samples.append(
                {
                    "timestamp": ts_str(row["timestamp"]),
                    "traffic_light_count": row.get("count"),
                    "state_histogram": row.get("state_histogram"),
                    "sample": row.get("sample"),
                }
            )
        nearest_fw = nearest_before(final_waypoint_rows, collision_ts or 0.0) if collision_ts is not None else None
        result["red_light_window"] = {
            "red_light_violation_from_error_json": bool(events.get("red")),
            "red_light_violation_timestamp": "unknown",
            "traffic_lights_topic_exists": bool(traffic_light_rows),
            "traffic_light_state_samples": state_samples or "unknown",
            "route_light_relation_confirmed": "unknown",
            "stop_line_crossing_confirmed": "unknown",
            "nearest_final_waypoints_stop_line_ids": nearest_fw.get("stop_line_ids") if nearest_fw else [],
            "notes": "Traffic light states are available, but route-light relation and stop-line crossing are not directly confirmed by the current summaries.",
        }

    if case_id == "027":
        total_duration = safe_float(error_json.get("elapsed_time"))
        last_ts = pose_rows[-1]["timestamp"] if pose_rows else None
        last_start = max(0.0, (last_ts or 0.0) - 60.0) if last_ts is not None else None
        pose_window = rows_in_window(pose_rows, last_start or 0.0, last_ts or 0.0) if last_ts is not None else []
        status_window = rows_in_window(vehicle_status_rows, last_start or 0.0, last_ts or 0.0) if last_ts is not None else []
        cmd_window = rows_in_window(vehicle_cmd_rows, last_start or 0.0, last_ts or 0.0) if last_ts is not None else []
        fw_window = rows_in_window(final_waypoint_rows, last_start or 0.0, last_ts or 0.0) if last_ts is not None else []
        start_pose = pose_window[0] if pose_window else None
        end_pose = pose_window[-1] if pose_window else None
        displacement = None
        if start_pose and end_pose and all(start_pose.get(k) is not None for k in ("x", "y", "z")) and all(
            end_pose.get(k) is not None for k in ("x", "y", "z")
        ):
            displacement = round(
                math.dist(
                    (start_pose["x"], start_pose["y"], start_pose["z"]),
                    (end_pose["x"], end_pose["y"], end_pose["z"]),
                ),
                3,
            )
        result["stuck_window"] = {
            "stuck_from_error_json": bool(events.get("stuck")),
            "total_duration_sec": round(total_duration, 3) if total_duration is not None else None,
            "last_60_seconds_window": {
                "start_timestamp": ts_str(last_start),
                "end_timestamp": ts_str(last_ts),
                "ego_movement_distance": compute_path_distance(pose_window),
                "ego_start_to_end_displacement": displacement,
                "velocity_stats": summarize_numeric([row.get("velocity") for row in status_window if row.get("velocity") is not None]),
                "vehicle_status_control_stats": {
                    "throttle": summarize_numeric([row.get("throttle") for row in status_window if row.get("throttle") is not None]),
                    "brake": summarize_numeric([row.get("brake") for row in status_window if row.get("brake") is not None]),
                    "steer": summarize_numeric([row.get("steer") for row in status_window if row.get("steer") is not None]),
                },
                "vehicle_cmd_stats": {
                    "accel_cmd": summarize_numeric([row.get("accel_cmd") for row in cmd_window if row.get("accel_cmd") is not None]),
                    "brake_cmd": summarize_numeric([row.get("brake_cmd") for row in cmd_window if row.get("brake_cmd") is not None]),
                    "steer_cmd": summarize_numeric([row.get("steer_cmd") for row in cmd_window if row.get("steer_cmd") is not None]),
                },
                "final_waypoints_present": bool(fw_window),
                "final_waypoint_count_stats": summarize_numeric(
                    [row.get("waypoint_count") for row in fw_window if row.get("waypoint_count") is not None]
                ),
            },
            "collision_or_red_light_interference": {
                "error_json_collision": bool(events.get("crash")),
                "error_json_red": bool(events.get("red")),
                "collision_topic_exists": bool(collision_rows),
            },
        }

    if case_id == "013":
        result["label_conflict"] = {
            "dataset_label": "C+L",
            "error_json_summary": "speeding only / no crash / no lane invasion",
            "explicit_lane_boundary_crossing_evidence": "unknown",
            "collision_topic_exists": bool(collision_rows),
            "needs_manual_review": True,
            "guidance": "Use this case only as an uncertainty sample. Do not treat the dataset label as confirmed ground truth.",
        }

    return result


def collect_unknowns(payload: dict[str, Any]) -> list[str]:
    unknowns: list[str] = []

    def visit(prefix: str, value: Any) -> None:
        if value == "unknown":
            unknowns.append(prefix)
            return
        if value is None:
            unknowns.append(prefix)
            return
        if isinstance(value, dict):
            for key, child in value.items():
                visit(f"{prefix}.{key}" if prefix else key, child)

    visit("", payload)
    return sorted(set(item for item in unknowns if item))


def main() -> None:
    oracle_rows = {}
    with (PROCESSED_DIR / "oracle_consistency.csv").open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            oracle_rows[row["case_id"]] = row

    PROMPT_V2_DIR.mkdir(parents=True, exist_ok=True)
    CRITICAL_DIR.mkdir(parents=True, exist_ok=True)
    MANUAL_DIR.mkdir(parents=True, exist_ok=True)

    report_lines = [
        "# Stage 5 Prompt V2 Report",
        "",
        "## Changes From The Original Proposal Prompts",
        "",
        "- Added `critical_window_summary` so the model sees failure-adjacent evidence instead of only full-trace ranges.",
        "- Replaced the stale `Only case_001 was fully decoded...` limitation with a case-accurate statement covering the selected decoded cases.",
        "- Tightened the output contract to an explicit JSON schema instead of a loose field list.",
        "- Added anti-hallucination rules for topic existence, red-light inference, lane invasion inference, stuck inference, and label conflicts.",
        "",
        "## Case Notes",
        "",
    ]
    manual_lines = []

    for index, case_id in enumerate(CASE_ORDER, start=1):
        llm_input_path = LLM_INPUT_DIR / f"case_{case_id}.json"
        llm_input = load_json(llm_input_path)
        oracle_row = oracle_rows[f"case_{case_id}"]

        llm_input["known_limitations"] = build_known_limitations(case_id)
        write_json(llm_input_path, llm_input)

        critical_window = build_critical_window(case_id, llm_input, oracle_row)
        critical_path = CRITICAL_DIR / f"case_{case_id}_critical_window.json"
        write_json(critical_path, critical_window)

        case_payload = {
            "case_id": llm_input["case_id"],
            "fault_label": llm_input["fault_label"],
            "scenario_config": llm_input["scenario_config"],
            "oracle_consistency": {
                "status": oracle_row["consistency_status"],
                "conflict_details": oracle_row["conflict_details"],
                "suggested_action": oracle_row["suggested_action"],
            },
            "available_topics": llm_input["available_topics"],
            "trace_summary": compact_trace_summary(llm_input["trace_summary"]),
            "critical_window_summary": critical_window,
            "known_limitations": llm_input["known_limitations"],
        }
        prompt_text = format_prompt(case_payload)
        prompt_path = PROMPT_V2_DIR / f"case_{case_id}_prompt.md"
        prompt_path.write_text(prompt_text)

        title = f"===== {index}. proposal_v2_case_{case_id} ====="
        manual_lines.extend([title, "", prompt_text.strip(), "", ""])

        unknowns = collect_unknowns(critical_window)
        critical_sections = ", ".join(key for key in critical_window.keys() if key.endswith("_window")) or "none"
        report_lines.extend(
            [
                f"### case_{case_id}",
                "",
                f"- critical window sections: `{critical_sections}`",
                f"- remaining unknown evidence: `{', '.join(unknowns[:12]) if unknowns else 'none'}`",
            ]
        )
        if case_id == "013":
            report_lines.append("- reason to keep as uncertainty sample: `Dataset.xlsx = C+L, but error.json reports speeding only and oracle consistency is dataset_only.`")
        report_lines.append("")

    (MANUAL_DIR / "ALL_PROMPTS_TO_RUN_V2.md").write_text("\n".join(manual_lines).rstrip() + "\n")
    report_lines.extend(
        [
            "## Recommendation",
            "",
            "- Run only `proposal_v2_case_001` first.",
            "- If the response stays evidence-grounded and uncertainty-aware, continue with `case_024` and `case_027`.",
            "- Keep `case_013` only for label-conflict testing, not as a main conclusion sample.",
            "",
        ]
    )
    REPORT_PATH.write_text("\n".join(report_lines))


if __name__ == "__main__":
    main()
