#!/usr/bin/env python3
"""Stage 2 extension: add case_013, oracle consistency, prompts, and review sheet."""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "processed"
PROMPTS = PROCESSED / "prompts"
CASE_CARDS = PROCESSED / "case_cards"
LLM_INPUTS = PROCESSED / "llm_inputs"
EXTRACTED = PROCESSED / "extracted"
CONVERTED = PROCESSED / "converted"

TARGET_CASES = [1, 3, 7, 13]
INSPECT_ONLY_CASES = [24, 27, 37]
REQUIRED_PRECHECK = [
    "processed/dataset_summary.csv",
    "processed/dataset_summary.md",
    "processed/file_inventory.md",
    "processed/topic_availability.csv",
    "processed/convert_script_report.md",
    "processed/case_cards/case_001.md",
    "processed/case_cards/case_003.md",
    "processed/case_cards/case_007.md",
    "processed/llm_inputs/case_001.json",
    "processed/llm_inputs/case_003.json",
    "processed/llm_inputs/case_007.json",
]


def load_build_module():
    build_path = ROOT / "scripts" / "build_drivefuzz_pipeline.py"
    spec = importlib.util.spec_from_file_location("drivefuzz_build", build_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {build_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def verify_precheck_files() -> list[dict[str, str]]:
    results = []
    for relative in REQUIRED_PRECHECK:
        path = ROOT / relative
        results.append(
            {
                "path": relative,
                "status": "present" if path.exists() else "missing",
            }
        )
    return results


def run_conversion_for_case(case_id: int) -> dict[str, Any]:
    case_dir = EXTRACTED / f"case_{case_id:03d}"
    output_root = CONVERTED / f"case_{case_id:03d}"
    output_root.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        [sys.executable, "scripts/run_conversion_case.py", str(case_dir), str(output_root)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return {
        "case_id": case_id,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        "report_path": str(output_root / "conversion_report.json"),
    }


def write_conversion_errors(reports: list[dict[str, Any]]) -> None:
    lines = ["# Conversion Errors", ""]
    for report in reports:
        case_label = f"case_{report['case_id']:03d}"
        if report["returncode"] == 0:
            lines.extend(
                [
                    f"- `{case_label}` conversion completed successfully.",
                    "",
                    "```text",
                    report["stdout"],
                    "```",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    f"- `{case_label}` conversion failed with code {report['returncode']}.",
                    "",
                    "```text",
                    report["stdout"],
                    report["stderr"],
                    "```",
                    "",
                ]
            )
    (PROCESSED / "convert_errors.md").write_text("\n".join(lines), encoding="utf-8")


def write_topic_availability(build, cases: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    output_path = PROCESSED / "topic_availability.csv"
    fieldnames = ["case_id", "topic_name", "found_or_not", "matched_file_path", "file_type", "notes"]
    matches_by_case: dict[int, dict[str, Any]] = {}
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for case in cases:
            case_id = case["case_id"]
            case_matches = {}
            for spec in build.TOPIC_SPECS:
                match = build.find_topic_match(case, spec)
                if not match.found:
                    notes = "topic absent from connections.json and no fuzzy filename match; likely not recorded in exported rosbag CSVs"
                else:
                    notes = match.notes
                writer.writerow(
                    {
                        "case_id": f"case_{case_id:03d}",
                        "topic_name": spec["topic_name"],
                        "found_or_not": "true" if match.found else "false",
                        "matched_file_path": match.matched_file_path,
                        "file_type": match.file_type,
                        "notes": notes,
                    }
                )
                case_matches[spec["topic_name"]] = match
            matches_by_case[case_id] = case_matches
    return matches_by_case


def load_oracle_consistency() -> dict[str, dict[str, str]]:
    csv_path = PROCESSED / "oracle_consistency.csv"
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return {row["case_id"]: row for row in reader}


def patch_llm_inputs_with_consistency(oracle_rows: dict[str, dict[str, str]]) -> None:
    for case_id in TARGET_CASES:
        path = LLM_INPUTS / f"case_{case_id:03d}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        oracle = oracle_rows.get(f"case_{case_id:03d}")
        if oracle:
            data["oracle_consistency"] = {
                "status": oracle["consistency_status"],
                "dataset_group": oracle["dataset_group"],
                "error_json_group": oracle.get("error_json_group", "unknown"),
                "conflict_details": oracle["conflict_details"],
                "suggested_action": oracle["suggested_action"],
            }
            known_limitations = data.get("known_limitations") or []
            if oracle["consistency_status"] != "consistent":
                known_limitations.append(
                    "Dataset.xlsx and error.json are inconsistent for this case; causal explanations must explicitly preserve that uncertainty."
                )
            data["known_limitations"] = known_limitations
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def make_case_prompt(case_json: dict[str, Any]) -> str:
    oracle = case_json.get("oracle_consistency") or {}
    return f"""# Prompt For {case_json['case_id']}

You are given one structured DriveFuzz / Autoware failure case.

Use only the evidence in the JSON block below.

## Rules

- Only use the provided evidence.
- Do not invent missing facts.
- If evidence is insufficient, write `unknown`.
- If `Dataset.xlsx` and `error.json` are inconsistent, you must explicitly state the uncertainty and must not resolve it by guessing.
- Keep the explanation technical and concise.

## Oracle Consistency Note

- oracle_consistency_status: `{oracle.get('status', 'unknown')}`
- dataset_group: `{oracle.get('dataset_group', 'unknown')}`
- error_json_group: `{oracle.get('error_json_group', 'unknown')}`
- conflict_details: `{oracle.get('conflict_details', 'unknown')}`

## Case JSON

```json
{json.dumps(case_json, indent=2, ensure_ascii=False)}
```

## Required Output Format

1. Fault layer: `sensing` / `perception` / `planning` / `actuation` / `simulator` / `map` / `unknown`
2. Fault component
3. Causal chain
4. Supporting evidence
5. Uncertain or missing evidence
6. Possible root-cause pattern
7. Whether this case is suitable for Bug2Scenario-style scenario amplification
8. Possible same-root-cause scenario variants
9. Pre-execution validation rules
10. Post-execution validation rules
"""


def write_case_prompts() -> None:
    PROMPTS.mkdir(parents=True, exist_ok=True)
    for case_id in TARGET_CASES:
        json_path = LLM_INPUTS / f"case_{case_id:03d}.json"
        case_json = json.loads(json_path.read_text(encoding="utf-8"))
        prompt_path = PROMPTS / f"case_{case_id:03d}_prompt.md"
        prompt_path.write_text(make_case_prompt(case_json), encoding="utf-8")


def conversion_status_from_llm(case_json: dict[str, Any]) -> str:
    sensing = ((case_json.get("trace_summary") or {}).get("sensing") or {})
    image = sensing.get("image_raw") or {}
    points = sensing.get("points_raw") or {}
    detection = ((case_json.get("trace_summary") or {}).get("perception") or {}).get("detection_fusion_objects") or {}
    prediction = ((case_json.get("trace_summary") or {}).get("perception") or {}).get("prediction_objects") or {}
    parts = [
        f"image={image.get('decode_status', 'unknown')}",
        f"points={points.get('decode_status', 'unknown')}",
        f"detection_summary={'present' if detection else 'missing'}",
        f"prediction_summary={'present' if prediction else 'missing'}",
    ]
    return "; ".join(parts)


def available_key_topics(case_json: dict[str, Any]) -> str:
    topics = case_json.get("available_topics") or []
    key_order = [
        "/image_raw",
        "/points_raw",
        "/detection/fusion_tools/objects",
        "/current_pose",
        "/prediction/motion_predictor/objects",
        "/lane_waypoints_array",
        "/final_waypoints",
        "/vehicle_cmd",
        "/carla/ego_vehicle/vehicle_status",
        "/carla/ego_vehicle/collision",
        "/carla/ego_vehicle/odometry",
    ]
    return ", ".join([topic for topic in key_order if topic in topics])


def ready_for_llm_status(case_json: dict[str, Any], oracle_row: dict[str, str]) -> tuple[str, str, str]:
    status = oracle_row["consistency_status"]
    need_manual_review = "yes" if status != "consistent" else "no"
    if status == "consistent":
        return "yes", need_manual_review, "run_first_round_llm_causal_explanation"
    return "yes_with_uncertainty", need_manual_review, "run_llm_with_uncertainty_note_and_manual_oracle_check"


def write_manual_review_sheet(oracle_rows: dict[str, dict[str, str]]) -> None:
    fieldnames = [
        "case_id",
        "zip_file",
        "dataset_group",
        "oracle_consistency_status",
        "available_key_topics",
        "conversion_status",
        "ready_for_llm",
        "need_manual_review",
        "recommended_next_action",
    ]
    rows = []
    for case_id in TARGET_CASES:
        case_label = f"case_{case_id:03d}"
        case_json = json.loads((LLM_INPUTS / f"{case_label}.json").read_text(encoding="utf-8"))
        oracle = oracle_rows[case_label]
        ready, need_review, recommendation = ready_for_llm_status(case_json, oracle)
        rows.append(
            {
                "case_id": case_label,
                "zip_file": f"{case_id}.zip",
                "dataset_group": oracle["dataset_group"],
                "oracle_consistency_status": oracle["consistency_status"],
                "available_key_topics": available_key_topics(case_json),
                "conversion_status": conversion_status_from_llm(case_json),
                "ready_for_llm": ready,
                "need_manual_review": need_review,
                "recommended_next_action": recommendation,
            }
        )
    with (PROCESSED / "manual_review_sheet.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_workflows_and_metrics() -> None:
    content = """# Workflows And Metrics

## A. Proposal workflow: Bug2Scenario / root-cause-preserving scenario amplification

- Input: case card, fault label, selected topic summaries, oracle consistency notes, root-cause evidence
- Process: infer causal explanation, identify reusable root-cause pattern, generate scenario variants that preserve the suspected root cause, attach validation rules, and only then decide which cases need simulator execution
- Output: causal explanation, layer/component hypothesis, scenario templates, validation rules, prioritized candidate scenarios
- Evaluation metrics:
- causal explanation quality
- layer classification accuracy
- evidence support score
- hallucination rate
- semantic consistency rate
- same-root-cause reproduction rate
- query number
- simulator execution saved

## B. Pure-LLM workflow

- Input: scenario data, fault label, trace summary, oracle consistency note
- Process: prompt the LLM directly on the structured evidence without explicit root-cause-preserving scenario design
- Output: causal explanation and generated scenario hypotheses
- Evaluation metrics:
- layer accuracy
- causal chain quality
- evidence support score
- hallucination rate
- scenario validity

## C. Previous work / human annotation workflow

- Input: raw ROS topics or case card, dataset labels, oracle traces
- Process: manual inspection, human causal explanation writing, optional root-cause labeling and scenario note taking
- Output: human causal explanation, root-cause label, reviewer notes, adjudicated oracle interpretation
- Evaluation metrics:
- annotation time
- agreement with known fault label
- evidence completeness
- inter-annotator agreement
"""
    (PROCESSED / "workflows_and_metrics.md").write_text(content, encoding="utf-8")


def append_readme_sections(precheck: list[dict[str, str]], oracle_rows: dict[str, dict[str, str]]) -> None:
    readme_path = PROCESSED / "README_pipeline_report.md"
    existing = readme_path.read_text(encoding="utf-8") if readme_path.exists() else "# Pipeline Report\n"

    stage2_precheck = [
        "## Stage 2 Precheck",
        "",
        "Current processed/ completeness check:",
        "",
        "| Path | Status |",
        "| --- | --- |",
    ]
    for item in precheck:
        stage2_precheck.append(f"| {item['path']} | {item['status']} |")

    conflict_cases = [case_id for case_id, row in oracle_rows.items() if row["consistency_status"] != "consistent"]

    stage2_summary = [
        "## Stage 2 Summary",
        "",
        f"- `13.zip` processed successfully: `{'yes' if (CASE_CARDS / 'case_013.md').exists() and (LLM_INPUTS / 'case_013.json').exists() else 'no'}`",
        f"- case cards and llm inputs present for `001/003/007/013`: `{'yes' if all((CASE_CARDS / f'case_{case_id:03d}.md').exists() and (LLM_INPUTS / f'case_{case_id:03d}.json').exists() for case_id in TARGET_CASES) else 'no'}`",
        f"- Cases with Dataset.xlsx / error.json inconsistency: {', '.join(conflict_cases) if conflict_cases else 'none'}",
        "- Topics successfully parsed across the four working cases include image_raw, points_raw, IMU, current_pose, detection objects, prediction objects, lane_waypoints_array, final_waypoints, vehicle_cmd, vehicle_status, odometry, objects, and traffic_lights; collision exists for case_001 and case_013.",
        "- image_raw / points_raw / perception object conversion status: case_001 and case_013 were converted; case_003 and case_007 currently retain summary-only decoding status.",
        "- Best cases for first-round LLM causal explanation: case_001 first, then case_013; case_003 and case_007 are usable with uncertainty notes because oracle labels are inconsistent.",
        "- Next recommended dataset after this stage: prefer `24.zip` if the next experiment should keep an explicit collision topic and add red-light evidence; prefer `27.zip` if the next experiment should cover the stuck / immobility fault type.",
        "",
    ]

    new_text = existing.rstrip() + "\n\n" + "\n".join(stage2_precheck) + "\n\n" + "\n".join(stage2_summary)
    readme_path.write_text(new_text, encoding="utf-8")


def main() -> int:
    precheck = verify_precheck_files()

    build = load_build_module()
    build.TARGET_CASES = TARGET_CASES
    build.INSPECT_ONLY_CASES = INSPECT_ONLY_CASES
    build.ZIP_CASES = TARGET_CASES + INSPECT_ONLY_CASES

    build.ensure_dirs()
    dataset_rows, dataset_by_index, dataset_markdown = build.load_dataset()
    build.write_dataset_summary(dataset_rows, dataset_markdown)
    build.extract_selected_cases()

    cases = [build.load_case_static(case_id) for case_id in TARGET_CASES]
    build.write_file_inventory(cases)
    matches_by_case = write_topic_availability(build, cases)
    build.inspect_convert_script()

    conversion_reports = [run_conversion_for_case(case_id) for case_id in [1, 13]]
    write_conversion_errors(conversion_reports)

    summaries = build.build_case_summaries(cases, dataset_by_index, matches_by_case)
    build.write_case_outputs(cases, summaries)

    subprocess.run([sys.executable, "scripts/check_oracle_consistency.py"], cwd=ROOT, check=True)
    oracle_rows = load_oracle_consistency()
    patch_llm_inputs_with_consistency(oracle_rows)

    write_case_prompts()
    write_manual_review_sheet(oracle_rows)
    write_workflows_and_metrics()
    append_readme_sections(precheck, oracle_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
