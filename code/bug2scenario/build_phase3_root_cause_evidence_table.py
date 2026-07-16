#!/usr/bin/env python3
"""Build code-based root-cause evidence checks for Phase 3 candidates.

This script is intentionally separate from the earlier manual review table. It
does not try to replace human video inspection. Instead, it reads the original
DriveFuzz bug JSON stored in the selected seed zip files and compares it with
each generated candidate's DriveFuzz execution JSON under PSSD.

The output is a 360-row table with automatic evidence columns that can be used
to decide which videos actually need human attention.
"""

from __future__ import annotations

import csv
import json
import math
import re
import statistics
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path("<WORKSPACE_ROOT>")
PSSD_ROOT = Path("<PSSD_ROOT>")
PREBATCH_DIR = PROJECT_ROOT / "processed" / "experiments" / "main_evaluation_prebatch"
INPUT_CSV = PREBATCH_DIR / "phase3_360_manual_review_table.csv"
OUTPUT_CSV = PREBATCH_DIR / "phase3_360_root_cause_evidence_table.csv"
SUMMARY_MD = PREBATCH_DIR / "phase3_360_root_cause_evidence_summary.md"

EVENT_TO_CODE = {
    "crash": "C",
    "stuck": "S",
    "lane_invasion": "L",
    "red": "R",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def safe_load_json(path: Path) -> dict[str, Any] | None:
    try:
        with path.open(encoding="utf-8") as f:
            obj = json.load(f)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def one_line(text: str, limit: int = 420) -> str:
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def parse_codes(text: str) -> set[str]:
    if not text:
        return set()
    return {part.strip() for part in text.split("+") if part.strip()}


def event_codes(obj: dict[str, Any] | None) -> set[str]:
    events = obj.get("events", {}) if isinstance(obj, dict) else {}
    if not isinstance(events, dict):
        return set()
    return {code for key, code in EVENT_TO_CODE.items() if events.get(key) is True}


def load_original_error(case_id: str) -> dict[str, Any] | None:
    case_num = int(case_id.replace("case_", ""))
    zip_path = PROJECT_ROOT / f"{case_num}.zip"
    member = f"{case_num}/{case_num}_error.json"
    if not zip_path.exists():
        return None
    try:
        with zipfile.ZipFile(zip_path) as zf:
            return json.loads(zf.read(member))
    except Exception:
        return None


def first_execution_json(run_dir: Path) -> tuple[dict[str, Any] | None, str]:
    for subdir in ("errors", "cov", "queue"):
        files = sorted((run_dir / subdir).glob("*.json"))
        if files:
            obj = safe_load_json(files[0])
            if obj is not None:
                return obj, str(files[0])
    return None, ""


def point_from_seed(seed: dict[str, Any], prefix: str) -> tuple[float, float] | None:
    try:
        return float(seed[f"{prefix}_x"]), float(seed[f"{prefix}_y"])
    except Exception:
        return None


def point_from_actor(actor: dict[str, Any]) -> tuple[float, float] | None:
    try:
        return float(actor["sp_x"]), float(actor["sp_y"])
    except Exception:
        return None


def dist(a: tuple[float, float] | None, b: tuple[float, float] | None) -> float | None:
    if a is None or b is None:
        return None
    return math.hypot(a[0] - b[0], a[1] - b[1])


def point_to_segment_distance(
    p: tuple[float, float] | None,
    a: tuple[float, float] | None,
    b: tuple[float, float] | None,
) -> float | None:
    if p is None or a is None or b is None:
        return None
    ax, ay = a
    bx, by = b
    px, py = p
    dx = bx - ax
    dy = by - ay
    denom = dx * dx + dy * dy
    if denom == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / denom))
    proj = (ax + t * dx, ay + t * dy)
    return math.hypot(px - proj[0], py - proj[1])


def actor_type_counter(actors: list[Any]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for actor in actors:
        if isinstance(actor, dict):
            counts[str(actor.get("type", "unknown"))] += 1
    return counts


def actor_nav_counter(actors: list[Any]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for actor in actors:
        if isinstance(actor, dict):
            counts[str(actor.get("nav_type", "unknown"))] += 1
    return counts


def counter_overlap(a: Counter[str], b: Counter[str]) -> float:
    total = sum(a.values())
    if total == 0:
        return 1.0 if sum(b.values()) == 0 else 0.0
    return sum(min(a[k], b[k]) for k in a) / total


def numeric_stats(values: Any) -> dict[str, str]:
    if not isinstance(values, list) or not values:
        return {"count": "0", "min": "", "max": "", "mean": "", "last": ""}
    nums: list[float] = []
    for value in values:
        try:
            nums.append(float(value))
        except Exception:
            pass
    if not nums:
        return {"count": "0", "min": "", "max": "", "mean": "", "last": ""}
    return {
        "count": str(len(nums)),
        "min": f"{min(nums):.3f}",
        "max": f"{max(nums):.3f}",
        "mean": f"{statistics.fmean(nums):.3f}",
        "last": f"{nums[-1]:.3f}",
    }


def min_actor_route_distance(obj: dict[str, Any] | None) -> float | None:
    if not isinstance(obj, dict):
        return None
    seed = obj.get("seed", {})
    actors = obj.get("actors", [])
    if not isinstance(seed, dict) or not isinstance(actors, list):
        return None
    start = point_from_seed(seed, "sp")
    goal = point_from_seed(seed, "wp")
    vals = [
        point_to_segment_distance(point_from_actor(actor), start, goal)
        for actor in actors
        if isinstance(actor, dict)
    ]
    vals = [v for v in vals if v is not None]
    return min(vals) if vals else None


def min_actor_spawn_distance(obj: dict[str, Any] | None) -> float | None:
    if not isinstance(obj, dict):
        return None
    seed = obj.get("seed", {})
    actors = obj.get("actors", [])
    if not isinstance(seed, dict) or not isinstance(actors, list):
        return None
    start = point_from_seed(seed, "sp")
    vals = [dist(point_from_actor(actor), start) for actor in actors if isinstance(actor, dict)]
    vals = [v for v in vals if v is not None]
    return min(vals) if vals else None


def scenario_features(obj: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(obj, dict):
        return {}
    seed = obj.get("seed", {}) if isinstance(obj.get("seed"), dict) else {}
    actors = obj.get("actors", []) if isinstance(obj.get("actors"), list) else []
    puddles = obj.get("puddles", []) if isinstance(obj.get("puddles"), list) else []
    vehicle_states = obj.get("vehicle_states", {}) if isinstance(obj.get("vehicle_states"), dict) else {}
    control_cmds = obj.get("control_cmds", {}) if isinstance(obj.get("control_cmds"), dict) else {}
    return {
        "map": str(seed.get("map", "")),
        "start": point_from_seed(seed, "sp"),
        "goal": point_from_seed(seed, "wp"),
        "actor_count": len(actors),
        "actor_types": actor_type_counter(actors),
        "actor_navs": actor_nav_counter(actors),
        "puddle_count": len(puddles),
        "min_actor_route_dist": min_actor_route_distance(obj),
        "min_actor_spawn_dist": min_actor_spawn_distance(obj),
        "min_dist": vehicle_states.get("min_dist", ""),
        "speed": numeric_stats(vehicle_states.get("speed")),
        "throttle": numeric_stats(control_cmds.get("throttle")),
        "brake": numeric_stats(control_cmds.get("brake")),
        "steer": numeric_stats(control_cmds.get("steer")),
        "num_frames": str(obj.get("num_frames", "")),
        "elapsed_time": str(obj.get("elapsed_time", "")),
    }


def fmt_float(value: Any) -> str:
    try:
        return f"{float(value):.3f}"
    except Exception:
        return ""


def get_float(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def evaluate_root_cause(row: dict[str, str], original: dict[str, Any] | None, candidate: dict[str, Any] | None) -> dict[str, str]:
    expected = parse_codes(row.get("expected_oracle_codes", ""))
    observed = parse_codes(row.get("observed_oracle_codes", ""))
    execution_status = row.get("auto_execution_status", "")
    oracle_match = row.get("oracle_match_status", "")
    orig = scenario_features(original)
    cand = scenario_features(candidate)

    reasons: list[str] = []
    score = 0
    max_score = 0

    def add(condition: bool, points: int, msg_ok: str, msg_bad: str) -> None:
        nonlocal score, max_score
        max_score += points
        if condition:
            score += points
            reasons.append(msg_ok)
        else:
            reasons.append(msg_bad)

    if not candidate:
        return {
            "auto_root_cause_decision": "no_trace_json_for_code_check",
            "auto_root_cause_confidence": "low",
            "auto_root_cause_score": "0.00",
            "auto_root_cause_reasons": "No candidate execution JSON found in errors/cov/queue.",
        }

    if execution_status == "invalid_scenario_spawn_failure":
        return {
            "auto_root_cause_decision": "invalid_scenario",
            "auto_root_cause_confidence": "high",
            "auto_root_cause_score": "0.00",
            "auto_root_cause_reasons": one_line("Spawn failure in DriveFuzz/CARLA execution; cannot be same-root-cause execution evidence."),
        }
    if execution_status == "execution_hang":
        return {
            "auto_root_cause_decision": "unknown_hang",
            "auto_root_cause_confidence": "medium",
            "auto_root_cause_score": "0.00",
            "auto_root_cause_reasons": one_line("Execution hang; needs rerun or video/log inspection before root-cause classification."),
        }

    if not observed:
        decision = "likely_no_failure_or_no_oracle"
        confidence = "medium" if execution_status in {"no_failure_reached_goal", "trace_ready_no_oracle"} else "low"
        return {
            "auto_root_cause_decision": decision,
            "auto_root_cause_confidence": confidence,
            "auto_root_cause_score": "0.00",
            "auto_root_cause_reasons": one_line(f"No observed DriveFuzz oracle; status={execution_status}."),
        }

    add(oracle_match in {"exact_oracle_match", "observed_superset_contains_expected"}, 4, "oracle symptom preserves expected label(s)", "oracle symptom differs or only partially overlaps")
    add(bool(orig.get("map")) and orig.get("map") == cand.get("map"), 2, "map preserved", "map differs or unavailable")

    start_delta = dist(orig.get("start"), cand.get("start"))
    goal_delta = dist(orig.get("goal"), cand.get("goal"))
    add(start_delta is not None and start_delta <= 30.0, 1, "mission start remains close", "mission start changed substantially or unavailable")
    add(goal_delta is not None and goal_delta <= 60.0, 1, "mission goal remains close", "mission goal changed substantially or unavailable")

    add(counter_overlap(orig.get("actor_types", Counter()), cand.get("actor_types", Counter())) >= 0.5, 1, "actor type family overlaps", "actor type family differs")
    add(abs(int(orig.get("actor_count", 0)) - int(cand.get("actor_count", 0))) <= 2, 1, "actor count remains comparable", "actor count changes substantially")

    orig_route_dist = get_float(orig.get("min_actor_route_dist"))
    cand_route_dist = get_float(cand.get("min_actor_route_dist"))
    route_threshold = max(15.0, (orig_route_dist or 0.0) + 10.0)
    if expected & {"C", "S"}:
        add(cand_route_dist is not None and cand_route_dist <= route_threshold, 2, "actor remains near ego mission route", "no comparable actor-route proximity")

    orig_min_dist = get_float(orig.get("min_dist"))
    cand_min_dist = get_float(cand.get("min_dist"))
    min_dist_threshold = max(10.0, (orig_min_dist or 0.0) * 3.0)
    if expected & {"C", "S"}:
        add(cand_min_dist is not None and cand_min_dist <= min_dist_threshold, 2, "runtime min_dist remains close", "runtime min_dist not close or unavailable")

    if "R" in expected:
        add("R" in observed, 3, "red-light oracle is reproduced", "red-light oracle is not reproduced")
    if "L" in expected:
        add("L" in observed, 3, "lane-invasion oracle is reproduced", "lane-invasion oracle is not reproduced")
    if "C" in expected:
        add("C" in observed, 3, "collision oracle is reproduced", "collision oracle is not reproduced")
    if "S" in expected:
        add("S" in observed, 3, "stuck oracle is reproduced", "stuck oracle is not reproduced")

    extra = observed - expected
    if extra:
        max_score += 2
        reasons.append(f"extra oracle symptom(s) present: {'+'.join(sorted(extra))}")
    else:
        score += 2
        max_score += 2
        reasons.append("no extra oracle symptom")

    score_ratio = score / max_score if max_score else 0.0
    if oracle_match in {"different_oracle_symptom"}:
        decision = "likely_different_root_cause"
        confidence = "high"
    elif score_ratio >= 0.78 and oracle_match in {"exact_oracle_match", "observed_superset_contains_expected"}:
        decision = "likely_same_root_cause_by_code"
        confidence = "medium"
    elif score_ratio >= 0.58 and observed & expected:
        decision = "possible_same_root_cause_needs_video"
        confidence = "low"
    else:
        decision = "likely_different_or_weak_evidence"
        confidence = "medium" if observed and not (observed & expected) else "low"

    prefix = [
        f"score={score}/{max_score}",
        f"orig_min_actor_route_dist={fmt_float(orig_route_dist)}",
        f"cand_min_actor_route_dist={fmt_float(cand_route_dist)}",
        f"orig_min_dist={fmt_float(orig_min_dist)}",
        f"cand_min_dist={fmt_float(cand_min_dist)}",
        f"start_delta={fmt_float(start_delta)}",
        f"goal_delta={fmt_float(goal_delta)}",
    ]
    return {
        "auto_root_cause_decision": decision,
        "auto_root_cause_confidence": confidence,
        "auto_root_cause_score": f"{score_ratio:.2f}",
        "auto_root_cause_reasons": one_line("; ".join(prefix + reasons)),
    }


def main() -> int:
    rows = read_csv(INPUT_CSV)
    originals: dict[str, dict[str, Any] | None] = {}
    out_rows: list[dict[str, Any]] = []
    summary_counter: Counter[str] = Counter()
    confidence_counter: Counter[str] = Counter()

    for row in rows:
        case_id = row.get("case_id", "")
        if case_id not in originals:
            originals[case_id] = load_original_error(case_id)

        run_dir = Path(row.get("run_dir", ""))
        candidate, source_json = first_execution_json(run_dir)
        evidence = evaluate_root_cause(row, originals[case_id], candidate)
        summary_counter[evidence["auto_root_cause_decision"]] += 1
        confidence_counter[evidence["auto_root_cause_confidence"]] += 1
        row_out = dict(row)
        insert = {
            "code_check_source_json": source_json,
            **evidence,
        }
        row_out.update(insert)
        out_rows.append(row_out)

    base_fields = list(rows[0].keys()) if rows else []
    manual_start = base_fields.index("manual_final_category") if "manual_final_category" in base_fields else len(base_fields)
    evidence_fields = [
        "code_check_source_json",
        "auto_root_cause_decision",
        "auto_root_cause_confidence",
        "auto_root_cause_score",
        "auto_root_cause_reasons",
    ]
    fieldnames = base_fields[:manual_start] + evidence_fields + base_fields[manual_start:]
    write_csv(OUTPUT_CSV, out_rows, fieldnames)

    with SUMMARY_MD.open("w", encoding="utf-8") as f:
        f.write("# Phase 3 Code-based Root-Cause Evidence Summary\n\n")
        f.write("This file summarizes automatic checks based on original DriveFuzz bug JSON files and generated candidate execution JSON files. It is triage evidence, not final human ground truth.\n\n")
        f.write("## Decision Counts\n\n")
        for key, count in summary_counter.most_common():
            f.write(f"- `{key}`: {count}\n")
        f.write("\n## Confidence Counts\n\n")
        for key, count in confidence_counter.most_common():
            f.write(f"- `{key}`: {count}\n")
        f.write("\n## Output\n\n")
        f.write(f"- CSV: `{OUTPUT_CSV}`\n")

    print(OUTPUT_CSV)
    print(SUMMARY_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
