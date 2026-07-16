#!/usr/bin/env python3
"""Prepare Stage 5 first-round LLM run assets for clean and uncertainty samples."""

from __future__ import annotations

import csv
from pathlib import Path
import os
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "processed"
PROMPTS = PROCESSED / "prompts"
MANUAL_PACKAGE = PROCESSED / "manual_llm_run_package"
MANUAL_RESULTS = PROCESSED / "manual_llm_results"
LLM_EVAL = PROCESSED / "llm_evaluation"

ORDER = [
    ("proposal", "001"),
    ("proposal", "024"),
    ("proposal", "027"),
    ("proposal", "013"),
    ("pure_llm", "001"),
    ("pure_llm", "024"),
    ("pure_llm", "027"),
    ("pure_llm", "013"),
]

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


def check_required() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise SystemExit("Missing Stage 5 inputs:\n" + "\n".join(missing))


def api_ready() -> bool:
    return bool(os.environ.get("LLM_API_KEY") and os.environ.get("LLM_BASE_URL") and os.environ.get("LLM_MODEL"))


def write_api_status() -> bool:
    api_ok = api_ready()
    lines = [
        "# Stage 5 API Status",
        "",
        f"- `LLM_API_KEY`: {'present' if os.environ.get('LLM_API_KEY') else 'missing'}",
        f"- `LLM_BASE_URL`: {'present' if os.environ.get('LLM_BASE_URL') else 'missing'}",
        f"- `LLM_MODEL`: {'present' if os.environ.get('LLM_MODEL') else 'missing'}",
        f"- Mode: `{'api' if api_ok else 'manual'}`",
        "",
    ]
    (PROCESSED / "stage5_api_status.md").write_text("\n".join(lines), encoding="utf-8")
    return api_ok


def write_stage4_status() -> None:
    manual_rows = {row["case_id"]: row for row in read_csv(PROCESSED / "manual_review_sheet.csv")}
    lines = [
        "# Stage 4 Status",
        "",
        "These are the prioritized cases for the first-round LLM causal explanation experiment.",
        "",
        "| case_id | category | fault group | oracle consistency status | ready_for_llm | key available topics | uncertainty notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for case_id, category in [("001", "clean sample"), ("024", "clean sample"), ("027", "clean sample"), ("013", "uncertainty sample")]:
        label = f"case_{case_id}"
        row = manual_rows[label]
        uncertainty = "none"
        if case_id == "013":
            uncertainty = "Dataset.xlsx and error.json are inconsistent; output must explicitly preserve uncertainty."
        lines.append(
            f"| {label} | {category} | {row['dataset_group']} | {row['oracle_consistency_status']} | {row['ready_for_llm']} | {row['available_key_topics']} | {uncertainty} |"
        )
    (PROCESSED / "stage4_status.md").write_text("\n".join(lines), encoding="utf-8")


def build_all_prompts() -> None:
    MANUAL_PACKAGE.mkdir(parents=True, exist_ok=True)
    combined = ["# All Prompts To Run", ""]
    save_lines = [
        "# Where To Save Outputs",
        "",
        "Save each webpage LLM answer into the matching file below.",
        "",
    ]
    for index, (workflow, case_id) in enumerate(ORDER, 1):
        prompt_path = PROMPTS / workflow / f"case_{case_id}_prompt.md"
        combined.append(f"===== {index}. {workflow}_case_{case_id} =====")
        combined.append("")
        combined.append(prompt_path.read_text(encoding="utf-8").rstrip())
        combined.append("")
        target_dir = MANUAL_RESULTS / workflow
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / f"case_{case_id}_raw_response.md"
        if not target_file.exists():
            target_file.write_text(
                f"# Paste raw webpage response for {workflow} case_{case_id} below this line\n\n",
                encoding="utf-8",
            )
        save_lines.append(f"{workflow}_case_{case_id} 的回答保存为：")
        save_lines.append(str(target_file))
        save_lines.append("")
    (MANUAL_PACKAGE / "ALL_PROMPTS_TO_RUN.md").write_text("\n".join(combined), encoding="utf-8")
    (MANUAL_PACKAGE / "WHERE_TO_SAVE_OUTPUTS.md").write_text("\n".join(save_lines), encoding="utf-8")


def run_stage5_llm(api_ok: bool) -> None:
    if api_ok:
        subprocess.run([sys.executable, "scripts/run_llm_causal_explanations.py", "--workflow", "proposal", "--cases", "001", "024", "027"], cwd=ROOT, check=False)
        subprocess.run([sys.executable, "scripts/run_llm_causal_explanations.py", "--workflow", "proposal", "--cases", "013"], cwd=ROOT, check=False)
        subprocess.run([sys.executable, "scripts/run_llm_causal_explanations.py", "--workflow", "pure_llm", "--cases", "001", "024", "027", "013"], cwd=ROOT, check=False)
    else:
        subprocess.run([sys.executable, "scripts/run_llm_causal_explanations.py", "--workflow", "both", "--cases", "001", "024", "027", "013", "--dry-run"], cwd=ROOT, check=False)


def run_eval() -> None:
    subprocess.run([sys.executable, "scripts/evaluate_llm_outputs.py", "--cases", "001", "024", "027", "013"], cwd=ROOT, check=False)


def write_stage5_report(api_ok: bool) -> None:
    comp_rows = read_csv(LLM_EVAL / "llm_comparison_table.csv") if (LLM_EVAL / "llm_comparison_table.csv").exists() else []
    by_key = {(row["case_id"], row["workflow"]): row for row in comp_rows}
    lines = [
        "# Stage 5 First-Round Experiment Report",
        "",
        "## Cases used in first-round LLM experiment",
        "",
        "- `case_001` clean Collision",
        "- `case_024` clean Collision + Red",
        "- `case_027` clean Stuck",
        "- `case_013` uncertainty C+L",
        "",
        "## Workflows",
        "",
        "- Proposal workflow: structured evidence + oracle consistency + selected topic summaries + uncertainty",
        "- Pure-LLM baseline: reduced high-level input",
        "",
        "## Expected comparison",
        "",
        "- Proposal 是否更能引用 evidence",
        "- Proposal 是否更少 hallucination",
        "- Proposal 是否更明确 uncertainty",
        "- Proposal 是否更能生成 root-cause pattern 和 validation rules",
        "",
        "## Metrics",
        "",
        "- causal chain quality",
        "- evidence support",
        "- hallucination",
        "- uncertainty awareness",
        "- root-cause pattern quality",
        "- scenario amplification usefulness",
        "",
        "## Current status",
        "",
        f"- Mode: `{'api' if api_ok else 'manual'}`",
        f"- API available: `{'yes' if api_ok else 'no'}`",
        "",
    ]
    for case_id in ["001", "024", "027", "013"]:
        lines.append(f"### case_{case_id}")
        lines.append("")
        for workflow in ["proposal", "pure_llm"]:
            row = by_key.get((f"case_{case_id}", workflow), {})
            lines.append(f"- {workflow}: `{row.get('status', 'not_run')}`")
        lines.append("")
    lines.extend(
        [
            "## Next action",
            "",
            "- If API is available: run the real API commands below.",
            "- If API is not available: use `processed/manual_llm_run_package/ALL_PROMPTS_TO_RUN.md`, paste each answer into `processed/manual_llm_results/...`, then run `python3 scripts/import_manual_llm_results.py` and `python3 scripts/evaluate_llm_outputs.py --cases 001 024 027 013`.",
            "",
        ]
    )
    (PROCESSED / "stage5_first_round_experiment_report.md").write_text("\n".join(lines), encoding="utf-8")


def write_next_action(api_ok: bool) -> None:
    if api_ok:
        text = "\n".join(
            [
                "1. export LLM_API_KEY",
                "2. export LLM_BASE_URL",
                "3. export LLM_MODEL",
                "4. python3 scripts/run_llm_causal_explanations.py --workflow both --cases 001 024 027 013",
                "5. python3 scripts/evaluate_llm_outputs.py --cases 001 024 027 013",
            ]
        )
    else:
        text = "\n".join(
            [
                "1. 打开 processed/manual_llm_run_package/ALL_PROMPTS_TO_RUN.md",
                "2. 按顺序复制第 1 个 prompt 到网页端大模型",
                "3. 把回答粘贴到 processed/manual_llm_results/proposal/case_001_raw_response.md",
                "4. 重复 8 个 prompt",
                "5. 运行 python3 scripts/import_manual_llm_results.py",
                "6. 运行 python3 scripts/evaluate_llm_outputs.py --cases 001 024 027 013",
                "7. 查看 processed/stage5_first_round_experiment_report.md",
            ]
        )
    (PROCESSED / "NEXT_ACTION_FOR_USER.md").write_text(text, encoding="utf-8")


def main() -> int:
    check_required()
    api_ok = write_api_status()
    write_stage4_status()
    build_all_prompts()
    run_stage5_llm(api_ok)
    run_eval()
    write_stage5_report(api_ok)
    write_next_action(api_ok)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
