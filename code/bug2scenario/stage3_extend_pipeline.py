#!/usr/bin/env python3
"""Stage 3 extension: add cases 024/027 and prepare first-round LLM experiments."""

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
PROMPT_TEMPLATES = PROMPTS / "templates"
PROPOSAL_PROMPTS = PROMPTS / "proposal"
PURE_PROMPTS = PROMPTS / "pure_llm"
CASE_CARDS = PROCESSED / "case_cards"
LLM_INPUTS = PROCESSED / "llm_inputs"
EXTRACTED = PROCESSED / "extracted"
CONVERTED = PROCESSED / "converted"
LLM_OUTPUTS = PROCESSED / "llm_outputs"

TARGET_CASES = [1, 3, 7, 13, 24, 27]
INSPECT_ONLY_CASES = [37]
STAGE2_REQUIRED = [
    "processed/case_cards/case_001.md",
    "processed/case_cards/case_003.md",
    "processed/case_cards/case_007.md",
    "processed/case_cards/case_013.md",
    "processed/llm_inputs/case_001.json",
    "processed/llm_inputs/case_003.json",
    "processed/llm_inputs/case_007.json",
    "processed/llm_inputs/case_013.json",
    "processed/oracle_consistency.csv",
    "processed/manual_review_sheet.csv",
    "processed/prompts/case_001_prompt.md",
    "processed/prompts/case_003_prompt.md",
    "processed/prompts/case_007_prompt.md",
    "processed/prompts/case_013_prompt.md",
]


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def verify_stage2_files() -> list[dict[str, str]]:
    rows = []
    for relative in STAGE2_REQUIRED:
        path = ROOT / relative
        rows.append({"path": relative, "status": "present" if path.exists() else "missing"})
    return rows


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
        "status": "completed" if completed.returncode == 0 else "failed",
    }


def load_existing_conversion_report(case_id: int) -> dict[str, Any] | None:
    report_path = CONVERTED / f"case_{case_id:03d}" / "conversion_report.json"
    if not report_path.exists():
        return None
    return {
        "case_id": case_id,
        "returncode": 0,
        "stdout": f"existing_report {report_path}",
        "stderr": "",
        "report_path": str(report_path),
        "status": "existing_report",
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
                notes = match.notes if match.found else "topic absent from connections.json and no fuzzy filename match; likely not recorded in exported rosbag CSVs"
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
    path = PROCESSED / "oracle_consistency.csv"
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return {row["case_id"]: row for row in reader}


def patch_llm_inputs_with_consistency(oracle_rows: dict[str, dict[str, str]]) -> None:
    for case_id in TARGET_CASES:
        path = LLM_INPUTS / f"case_{case_id:03d}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        oracle = oracle_rows.get(f"case_{case_id:03d}")
        if not oracle:
            continue
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
        data["known_limitations"] = sorted(set(known_limitations))
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def make_single_case_prompt(case_json: dict[str, Any]) -> str:
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


def write_single_case_prompts() -> None:
    PROMPTS.mkdir(parents=True, exist_ok=True)
    for case_id in TARGET_CASES:
        case_json = json.loads((LLM_INPUTS / f"case_{case_id:03d}.json").read_text(encoding="utf-8"))
        (PROMPTS / f"case_{case_id:03d}_prompt.md").write_text(make_single_case_prompt(case_json), encoding="utf-8")


def high_level_scenario_summary(case_json: dict[str, Any]) -> str:
    config = case_json.get("scenario_config") or {}
    fault = case_json.get("fault_label") or {}
    topics = case_json.get("available_topics") or []
    return (
        f"Case {case_json.get('case_id')} is labeled `{fault.get('group', 'unknown')}`. "
        f"Map is `{config.get('map', 'unknown')}`. "
        f"Actors summary: `{config.get('actors', 'unknown')}`. "
        f"Weather summary: `{json.dumps(config.get('weather', 'unknown'), ensure_ascii=False)[:180]}`. "
        f"Available key topics count is `{len(topics)}`."
    )


def oracle_result_summary(case_json: dict[str, Any]) -> str:
    oracle = case_json.get("oracle_consistency") or {}
    oracle_trace = ((case_json.get("trace_summary") or {}).get("oracle") or {}).get("error_json_events")
    return (
        f"oracle_consistency_status=`{oracle.get('status', 'unknown')}`, "
        f"dataset_group=`{oracle.get('dataset_group', 'unknown')}`, "
        f"error_json_group=`{oracle.get('error_json_group', 'unknown')}`, "
        f"error_json_events=`{json.dumps(oracle_trace, ensure_ascii=False)[:220]}`."
    )


def write_prompt_templates() -> None:
    PROMPT_TEMPLATES.mkdir(parents=True, exist_ok=True)
    proposal_template = """# Proposal Causal Explanation Template

You are given one DriveFuzz / Autoware case in structured form.

You must use only the provided evidence.

## Input

- scenario_config
- fault_label
- oracle_consistency status
- selected topic summaries
- sensing / perception / planning / actuation / oracle evidence
- uncertainty notes

## Required Constraints

- Only use the provided evidence.
- Do not invent sensor, perception, planning, control, simulator, or oracle evidence that is not present.
- If evidence is insufficient, write `unknown`.
- If oracle consistency has conflicts, you must explicitly mention them under uncertainty.
- Return one JSON object only.

## Required JSON Fields

- fault_layer
- fault_component
- causal_chain
- supporting_evidence
- uncertain_or_missing_evidence
- possible_root_cause_pattern
- whether_suitable_for_Bug2Scenario
- same_root_cause_scenario_variants
- pre_execution_validation_rules
- post_execution_validation_rules
- confidence_score
"""
    pure_template = """# Pure LLM Baseline Template

You are given a reduced summary of one DriveFuzz / Autoware case.

Use only the provided information.

## Input

- case_id
- fault_label
- high-level scenario summary
- oracle result summary

## Required Constraints

- Only use the provided evidence.
- Do not invent unavailable low-level sensor/perception/planning/control evidence.
- If evidence is insufficient, write `unknown`.
- If Dataset.xlsx and error.json disagree, explicitly mention the uncertainty.
- Return one JSON object only.

## Required JSON Fields

- fault_layer
- fault_component
- causal_chain
- supporting_evidence
- uncertain_or_missing_evidence
- possible_root_cause_pattern
- whether_suitable_for_Bug2Scenario
- same_root_cause_scenario_variants
- pre_execution_validation_rules
- post_execution_validation_rules
- confidence_score
"""
    (PROMPT_TEMPLATES / "proposal_causal_explanation_template.md").write_text(proposal_template, encoding="utf-8")
    (PROMPT_TEMPLATES / "pure_llm_baseline_template.md").write_text(pure_template, encoding="utf-8")


def proposal_prompt_text(case_json: dict[str, Any]) -> str:
    return f"""# Proposal Prompt For {case_json['case_id']}

Use only the structured evidence below and return exactly one JSON object.

## Rules

- Only use the given evidence.
- Do not invent missing sensor, perception, planning, actuation, or oracle evidence.
- If evidence is insufficient, write `unknown`.
- If oracle consistency has a conflict, explicitly describe it in `uncertain_or_missing_evidence`.

## Case JSON

```json
{json.dumps(case_json, indent=2, ensure_ascii=False)}
```

## Return JSON Fields

- fault_layer
- fault_component
- causal_chain
- supporting_evidence
- uncertain_or_missing_evidence
- possible_root_cause_pattern
- whether_suitable_for_Bug2Scenario
- same_root_cause_scenario_variants
- pre_execution_validation_rules
- post_execution_validation_rules
- confidence_score
"""


def pure_prompt_text(case_json: dict[str, Any]) -> str:
    compact = {
        "case_id": case_json["case_id"],
        "fault_label": case_json.get("fault_label"),
        "high_level_scenario_summary": high_level_scenario_summary(case_json),
        "oracle_result_summary": oracle_result_summary(case_json),
        "known_limitations": case_json.get("known_limitations"),
    }
    return f"""# Pure LLM Baseline Prompt For {case_json['case_id']}

Use only the reduced case summary below and return exactly one JSON object.

## Rules

- Only use the provided information.
- Do not invent unavailable low-level topic evidence.
- If evidence is insufficient, write `unknown`.
- If Dataset.xlsx and error.json disagree, explicitly mention that uncertainty.

## Reduced Case Summary

```json
{json.dumps(compact, indent=2, ensure_ascii=False)}
```

## Return JSON Fields

- fault_layer
- fault_component
- causal_chain
- supporting_evidence
- uncertain_or_missing_evidence
- possible_root_cause_pattern
- whether_suitable_for_Bug2Scenario
- same_root_cause_scenario_variants
- pre_execution_validation_rules
- post_execution_validation_rules
- confidence_score
"""


def write_baseline_prompts() -> None:
    PROPOSAL_PROMPTS.mkdir(parents=True, exist_ok=True)
    PURE_PROMPTS.mkdir(parents=True, exist_ok=True)
    for case_id in TARGET_CASES:
        case_json = json.loads((LLM_INPUTS / f"case_{case_id:03d}.json").read_text(encoding="utf-8"))
        (PROPOSAL_PROMPTS / f"case_{case_id:03d}_prompt.md").write_text(proposal_prompt_text(case_json), encoding="utf-8")
        (PURE_PROMPTS / f"case_{case_id:03d}_prompt.md").write_text(pure_prompt_text(case_json), encoding="utf-8")


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


def ready_for_llm_status(oracle_row: dict[str, str]) -> tuple[str, str, str]:
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
        ready, need_review, recommendation = ready_for_llm_status(oracle)
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


def write_stage3_status(oracle_rows: dict[str, dict[str, str]]) -> None:
    manual_rows = {}
    with (PROCESSED / "manual_review_sheet.csv").open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            manual_rows[row["case_id"]] = row
    lines = [
        "# Stage 3 Status",
        "",
        "| case_id | fault group | oracle consistency status | ready_for_llm | key available topics | uncertainty notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for case_id in TARGET_CASES:
        label = f"case_{case_id:03d}"
        oracle = oracle_rows.get(label, {})
        manual = manual_rows.get(label, {})
        uncertainty = oracle.get("conflict_details", "")
        if oracle.get("consistency_status") == "consistent":
            uncertainty = "none"
        lines.append(
            f"| {label} | {oracle.get('dataset_group', 'unknown')} | {oracle.get('consistency_status', 'unknown')} | {manual.get('ready_for_llm', 'unknown')} | {manual.get('available_key_topics', '')} | {uncertainty} |"
        )
    (PROCESSED / "stage3_status.md").write_text("\n".join(lines), encoding="utf-8")


def write_stage3_report(oracle_rows: dict[str, dict[str, str]]) -> None:
    inconsistent = [case_id for case_id, row in oracle_rows.items() if case_id in {f"case_{cid:03d}" for cid in TARGET_CASES} and row["consistency_status"] != "consistent"]
    lines = [
        "# Stage 3 Report",
        "",
        "## Cases",
        "",
        "- Processed cases: `001`, `003`, `007`, `013`, `024`, `027`",
        "",
        "## Fault Groups And Oracle Status",
        "",
        "| Case | Dataset Group | Oracle Consistency |",
        "| --- | --- | --- |",
    ]
    for case_id in TARGET_CASES:
        label = f"case_{case_id:03d}"
        oracle = oracle_rows.get(label, {})
        lines.append(f"| {label} | {oracle.get('dataset_group', 'unknown')} | {oracle.get('consistency_status', 'unknown')} |")
    lines.extend(
        [
            "",
            "## Best Cases For First-Round LLM Causal Explanation",
            "",
            "- `case_001`: most stable baseline because labels and error.json are consistent and sensing topics were converted.",
            "- `case_013`: strong second choice because collision topic exists and selected topics were converted, but oracle labels conflict with error.json and must be treated as uncertain.",
            "- `case_024`: suitable third choice because it covers `C+R` and its oracle status is consistent.",
            "",
            "## Cases With Label Uncertainty",
            "",
            f"- Cases requiring explicit uncertainty handling: {', '.join(inconsistent) if inconsistent else 'none'}",
            "",
            "## Proposal vs Pure-LLM Prompts",
            "",
            "- Proposal prompt uses the full structured trace summary, topic-level evidence, oracle consistency note, and uncertainty metadata.",
            "- Pure-LLM prompt uses only reduced case information: case id, fault label, high-level scenario summary, and oracle result summary.",
            "- The two prompts are aligned on output schema so later comparison is straightforward.",
            "",
            "## Batch LLM Script",
            "",
            "- Script: `python3 scripts/run_llm_causal_explanations.py`",
            "- Reads prompts from `processed/prompts/proposal/` and `processed/prompts/pure_llm/`.",
            "- Supports `--workflow proposal`, `--workflow pure_llm`, or `--workflow both`.",
            "- Supports `--cases 001 013` style filtering.",
            "- Supports `--dry-run` when no API key is available.",
            "",
            "## Environment Variables",
            "",
            "- `LLM_API_KEY`: API key for an OpenAI-compatible endpoint.",
            "- `LLM_BASE_URL`: base URL, for example an OpenAI endpoint or Doubao-compatible OpenAI API endpoint.",
            "- `LLM_MODEL`: model name.",
            "",
            "## Recommended First Real Run Order",
            "",
            "- First run `case_001` with proposal prompt.",
            "- Then run `case_013` with proposal prompt.",
            "- Then run `case_024` with proposal prompt.",
            "- After that, run the matching pure-LLM baselines for the same cases.",
            "",
            "## Next Steps",
            "",
            "- Manually review LLM causal explanations.",
            "- Refine prompts based on hallucination and evidence-support issues.",
            "- Expand to more cases after the first comparison table is checked.",
            "- Delay Bug2Scenario-style scenario amplification until causal explanation quality is acceptable.",
            "",
            "## Commands",
            "",
            "Dry run:",
            "```bash",
            "python3 scripts/run_llm_causal_explanations.py --workflow both --cases 001 013 --dry-run",
            "```",
            "",
            "Real run:",
            "```bash",
            "export LLM_API_KEY=\"...\"",
            "export LLM_BASE_URL=\"...\"",
            "export LLM_MODEL=\"...\"",
            "python3 scripts/run_llm_causal_explanations.py --workflow proposal --cases 001 013",
            "```",
            "",
            "Evaluation:",
            "```bash",
            "python3 scripts/evaluate_llm_outputs.py",
            "```",
            "",
        ]
    )
    (PROCESSED / "stage3_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    build = load_module(ROOT / "scripts" / "build_drivefuzz_pipeline.py", "stage3_build")

    build.TARGET_CASES = TARGET_CASES
    build.INSPECT_ONLY_CASES = INSPECT_ONLY_CASES
    build.ZIP_CASES = TARGET_CASES + INSPECT_ONLY_CASES
    build.ensure_dirs()

    precheck = verify_stage2_files()
    dataset_rows, dataset_by_index, dataset_markdown = build.load_dataset()
    build.write_dataset_summary(dataset_rows, dataset_markdown)
    build.extract_selected_cases()
    cases = [build.load_case_static(case_id) for case_id in TARGET_CASES]
    build.write_file_inventory(cases)
    matches_by_case = write_topic_availability(build, cases)
    build.inspect_convert_script()

    reports = []
    for case_id in [1, 13]:
        existing = load_existing_conversion_report(case_id)
        if existing:
            reports.append(existing)
    for case_id in [24, 27]:
        reports.append(run_conversion_for_case(case_id))
    write_conversion_errors(reports)

    summaries = build.build_case_summaries(cases, dataset_by_index, matches_by_case)
    build.write_case_outputs(cases, summaries)

    subprocess.run([sys.executable, "scripts/check_oracle_consistency.py"], cwd=ROOT, check=True)
    oracle_rows = load_oracle_consistency()
    patch_llm_inputs_with_consistency(oracle_rows)
    write_single_case_prompts()
    write_prompt_templates()
    write_baseline_prompts()
    write_manual_review_sheet(oracle_rows)
    write_stage3_status(oracle_rows)
    write_stage3_report(oracle_rows)

    lines = [
        "# Stage 2 File Check",
        "",
        "| Path | Status |",
        "| --- | --- |",
    ]
    for item in precheck:
        lines.append(f"| {item['path']} | {item['status']} |")
    existing = (PROCESSED / "stage3_status.md").read_text(encoding="utf-8")
    (PROCESSED / "stage3_status.md").write_text("\n".join(lines) + "\n\n" + existing, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
