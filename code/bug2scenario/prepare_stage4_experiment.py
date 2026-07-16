#!/usr/bin/env python3
"""Prepare and execute Stage 4 first-round LLM causal explanation experiments."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "processed"
PROMPTS = PROCESSED / "prompts"
LLM_OUTPUTS = PROCESSED / "llm_outputs"
MANUAL_PACKAGE = PROCESSED / "manual_llm_run_package"

CLEAN_CASES = ["001", "024", "027"]
UNCERTAINTY_CASES = ["013"]
ALL_CASES = CLEAN_CASES + UNCERTAINTY_CASES

REQUIRED_FILES = [
    "processed/stage3_status.md",
    "processed/stage3_report.md",
    "processed/manual_review_sheet.csv",
    "processed/oracle_consistency.csv",
    "processed/llm_inputs/case_001.json",
    "processed/llm_inputs/case_013.json",
    "processed/llm_inputs/case_024.json",
    "processed/llm_inputs/case_027.json",
    "processed/prompts/proposal/case_001_prompt.md",
    "processed/prompts/proposal/case_013_prompt.md",
    "processed/prompts/proposal/case_024_prompt.md",
    "processed/prompts/proposal/case_027_prompt.md",
    "processed/prompts/pure_llm/case_001_prompt.md",
    "processed/prompts/pure_llm/case_013_prompt.md",
    "processed/prompts/pure_llm/case_024_prompt.md",
    "processed/prompts/pure_llm/case_027_prompt.md",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def llm_env_available() -> bool:
    return bool(os.environ.get("LLM_API_KEY") and os.environ.get("LLM_BASE_URL") and os.environ.get("LLM_MODEL"))


def run_cmd(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True)


def write_stage4_status() -> None:
    manual_rows = {row["case_id"]: row for row in read_csv(PROCESSED / "manual_review_sheet.csv")}
    oracle_rows = {row["case_id"]: row for row in read_csv(PROCESSED / "oracle_consistency.csv")}
    lines = [
        "# Stage 4 Status",
        "",
        "These are the prioritized cases for the first-round LLM causal explanation experiment.",
        "",
        "| case_id | category | fault group | oracle consistency status | ready_for_llm | key available topics | uncertainty notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for case_id in ALL_CASES:
        label = f"case_{case_id}"
        manual = manual_rows[label]
        oracle = oracle_rows[label]
        category = "clean sample" if case_id in CLEAN_CASES else "uncertainty sample"
        uncertainty = "none"
        if case_id == "013":
            uncertainty = "Dataset.xlsx and error.json are inconsistent; output must explicitly preserve uncertainty."
        lines.append(
            f"| {label} | {category} | {manual['dataset_group']} | {manual['oracle_consistency_status']} | {manual['ready_for_llm']} | {manual['available_key_topics']} | {uncertainty} |"
        )
    (PROCESSED / "stage4_status.md").write_text("\n".join(lines), encoding="utf-8")


def create_manual_package() -> None:
    if MANUAL_PACKAGE.exists():
        shutil.rmtree(MANUAL_PACKAGE)
    MANUAL_PACKAGE.mkdir(parents=True, exist_ok=True)
    responses_dir = MANUAL_PACKAGE / "responses"
    responses_dir.mkdir(parents=True, exist_ok=True)

    order = [
        ("proposal", "001"),
        ("proposal", "024"),
        ("proposal", "027"),
        ("proposal", "013"),
        ("pure_llm", "001"),
        ("pure_llm", "024"),
        ("pure_llm", "027"),
        ("pure_llm", "013"),
    ]
    for workflow, case_id in order:
        source = PROMPTS / workflow / f"case_{case_id}_prompt.md"
        target = MANUAL_PACKAGE / f"{workflow}_case_{case_id}.md"
        shutil.copyfile(source, target)
        response_placeholder = responses_dir / f"{workflow}_case_{case_id}_response.txt"
        response_placeholder.write_text(
            f"Paste the raw webpage LLM response for {workflow} case_{case_id} here.\n",
            encoding="utf-8",
        )

    instructions = [
        "# Manual LLM Run Instructions",
        "",
        "No `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL` was available, so Stage 4 fell back to dry-run mode.",
        "",
        "## Recommended Paste Order",
        "",
        "1. `proposal_case_001.md`",
        "2. `proposal_case_024.md`",
        "3. `proposal_case_027.md`",
        "4. `proposal_case_013.md`",
        "5. `pure_llm_case_001.md`",
        "6. `pure_llm_case_024.md`",
        "7. `pure_llm_case_027.md`",
        "8. `pure_llm_case_013.md`",
        "",
        "## Save Locations For Web Responses",
        "",
        "- Save the raw webpage answer for each prompt under `processed/manual_llm_run_package/responses/`.",
        "- Example: `proposal_case_001_response.txt`, `pure_llm_case_024_response.txt`.",
        "- After pasting those responses locally, they can be wrapped into `processed/llm_outputs/.../*.json` later for parsing.",
        "",
        "## Notes",
        "",
        "- `case_013` is an uncertainty sample. Its prompt already explains that Dataset.xlsx and error.json disagree.",
        "- Do not edit the prompt contents before the first run unless you want to invalidate the baseline comparison.",
        "",
    ]
    (PROCESSED / "manual_llm_run_instructions.md").write_text("\n".join(instructions), encoding="utf-8")


def create_stage4_report(api_success: bool) -> None:
    comparison_path = PROCESSED / "llm_evaluation" / "llm_comparison_table.csv"
    comparison_rows = read_csv(comparison_path) if comparison_path.exists() else []
    by_case_workflow = {(row["case_id"], row["workflow"]): row for row in comparison_rows}
    lines = [
        "# Stage 4 Report",
        "",
        "## Cases Used",
        "",
        "- `case_001`, `case_024`, `case_027`, `case_013`",
        "",
        "## Sample Types",
        "",
        "- Clean samples: `case_001`, `case_024`, `case_027`",
        "- Uncertainty sample: `case_013`",
        "",
        "## Prompt Difference",
        "",
        "- Proposal prompt uses full structured evidence, selected topic summaries, oracle consistency, and uncertainty notes.",
        "- Pure-LLM prompt uses reduced summary information only and does not expose full topic-level evidence.",
        "",
        "## LLM API Status",
        "",
        f"- Successful real API invocation: `{'yes' if api_success else 'no'}`",
    ]
    if not api_success:
        lines.extend(
            [
                f"- Manual run package: `{MANUAL_PACKAGE}`",
                f"- Manual instructions: `{PROCESSED / 'manual_llm_run_instructions.md'}`",
            ]
        )
    lines.extend(["", "## Initial Case Results", ""])
    for case_id in ALL_CASES:
        label = f"case_{case_id}"
        proposal = by_case_workflow.get((label, "proposal"), {})
        pure = by_case_workflow.get((label, "pure_llm"), {})
        lines.extend(
            [
                f"### {label}",
                "",
                f"- proposal status: `{proposal.get('status', proposal.get('notes', 'unknown'))}`",
                f"- pure_llm status: `{pure.get('status', pure.get('notes', 'unknown'))}`",
                f"- proposal fault layer: `{proposal.get('fault_layer_pred', '') or 'not_run'}`",
                f"- pure_llm fault layer: `{pure.get('fault_layer_pred', '') or 'not_run'}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Preliminary Comparison",
            "",
            "- If real outputs exist, compare whether Proposal mentions more evidence items, more uncertainty notes for conflicted cases, more explicit root-cause patterns, and more validation rules.",
            "- In the current run, dry-run or missing API results should be treated as `not_run` rather than actual model performance.",
            "",
            "## Next Step Suggestions",
            "",
            "- If no real outputs were produced, use the manual package first.",
            "- After the first manual or API run, inspect `llm_comparison_table.csv` and revise prompts only after preserving the original baseline copy.",
            "- Expand to `case_003` and `case_007` only after the clean samples are stable.",
            "- Do not interpret Dataset.xlsx / error.json conflicts as resolved ground truth without manual adjudication.",
            "",
            "## Commands",
            "",
            "Dry run:",
            "```bash",
            "python3 scripts/run_llm_causal_explanations.py --workflow both --cases 001 024 027 013 --dry-run",
            "```",
            "",
            "Real run:",
            "```bash",
            "export LLM_API_KEY=\"...\"",
            "export LLM_BASE_URL=\"...\"",
            "export LLM_MODEL=\"...\"",
            "python3 scripts/run_llm_causal_explanations.py --workflow proposal --cases 001 024 027",
            "python3 scripts/run_llm_causal_explanations.py --workflow proposal --cases 013",
            "python3 scripts/run_llm_causal_explanations.py --workflow pure_llm --cases 001 024 027 013",
            "```",
            "",
            "Evaluation:",
            "```bash",
            "python3 scripts/evaluate_llm_outputs.py",
            "```",
            "",
        ]
    )
    (PROCESSED / "stage4_report.md").write_text("\n".join(lines), encoding="utf-8")


def normalize_output_statuses() -> bool:
    success = False
    for workflow in ["proposal", "pure_llm"]:
        for case_id in ALL_CASES:
            path = LLM_OUTPUTS / workflow / f"case_{case_id}_output.json"
            if not path.exists():
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            if data.get("status") == "success":
                success = True
    return success


def main() -> int:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise SystemExit("Missing Stage 4 required inputs:\n" + "\n".join(missing))

    write_stage4_status()

    env_ready = llm_env_available()
    if env_ready:
        run_cmd([sys.executable, "scripts/run_llm_causal_explanations.py", "--workflow", "proposal", "--cases", *CLEAN_CASES])
        run_cmd([sys.executable, "scripts/run_llm_causal_explanations.py", "--workflow", "proposal", "--cases", *UNCERTAINTY_CASES])
        run_cmd([sys.executable, "scripts/run_llm_causal_explanations.py", "--workflow", "pure_llm", "--cases", *ALL_CASES])
    else:
        run_cmd([sys.executable, "scripts/run_llm_causal_explanations.py", "--workflow", "both", "--cases", *ALL_CASES, "--dry-run"])
        create_manual_package()

    run_cmd([sys.executable, "scripts/evaluate_llm_outputs.py"])
    api_success = normalize_output_statuses()
    if not env_ready or not api_success:
        create_manual_package()
    create_stage4_report(api_success)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
