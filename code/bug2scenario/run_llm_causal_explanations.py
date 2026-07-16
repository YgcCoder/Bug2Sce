#!/usr/bin/env python3
"""Run or dry-run LLM causal explanation prompts for proposal and pure-LLM workflows."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from datetime import datetime, timezone
import urllib.error
import urllib.request
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_DIR = ROOT / "processed" / "prompts"
OUTPUTS_DIR = ROOT / "processed" / "llm_outputs"


def normalize_case(case_text: str) -> str:
    text = case_text.strip().lower().replace("case_", "")
    return f"case_{int(text):03d}"


def workflows_from_arg(value: str) -> list[str]:
    if value == "both":
        return ["proposal", "pure_llm"]
    return [value]


def prompt_path(workflow: str, case_id: str) -> Path:
    return PROMPTS_DIR / workflow / f"{case_id}_prompt.md"


def output_path(workflow: str, case_id: str) -> Path:
    return OUTPUTS_DIR / workflow / f"{case_id}_output.json"


def discover_cases(workflow: str) -> list[str]:
    folder = PROMPTS_DIR / workflow
    cases = []
    for path in sorted(folder.glob("case_*_prompt.md")):
        cases.append(path.stem.replace("_prompt", ""))
    return cases


def ensure_output_dirs() -> None:
    for workflow in ["proposal", "pure_llm"]:
        (OUTPUTS_DIR / workflow).mkdir(parents=True, exist_ok=True)


def extract_json_from_text(text: str) -> Any:
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = stripped[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return None
    return None


def call_openai_compatible(prompt_text: str, api_key: str, base_url: str, model: str) -> tuple[str, Any]:
    url = base_url.rstrip("/")
    if not url.endswith("/chat/completions"):
        url = url + "/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.2,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        raw = response.read().decode("utf-8")
    parsed = json.loads(raw)
    content = ""
    choices = parsed.get("choices") or []
    if choices:
        message = (choices[0] or {}).get("message") or {}
        content = message.get("content", "")
        if isinstance(content, list):
            content = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in content)
    return content, parsed


def build_result(case_id: str, workflow: str, model: str, prompt_path_value: Path, status: str, error_message: str, raw_response: str, parsed_response: Any, prompt_text: str) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "workflow": workflow,
        "model": model,
        "prompt_path": str(prompt_path_value),
        "raw_response": raw_response,
        "parsed_response": parsed_response,
        "status": status,
        "error_message": error_message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_text": prompt_text,
    }


def run_one(case_id: str, workflow: str, dry_run: bool) -> dict[str, Any]:
    path = prompt_path(workflow, case_id)
    prompt_text = path.read_text(encoding="utf-8")
    api_key = os.environ.get("LLM_API_KEY", "")
    base_url = os.environ.get("LLM_BASE_URL", "")
    model = os.environ.get("LLM_MODEL", "unknown_model")

    if dry_run:
        return build_result(case_id, workflow, model, path, "dry_run", "", "", None, prompt_text)
    if not api_key or not base_url or not model:
        return build_result(case_id, workflow, model, path, "skipped_no_api_key", "LLM_API_KEY or LLM_BASE_URL or LLM_MODEL is missing", "", None, prompt_text)
    try:
        content, raw_payload = call_openai_compatible(prompt_text, api_key, base_url, model)
        parsed = extract_json_from_text(content)
        if parsed is None:
            return build_result(case_id, workflow, model, path, "parse_failed", "response was not valid JSON", content, None, prompt_text)
        return build_result(case_id, workflow, model, path, "completed", "", content, parsed, prompt_text)
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        return build_result(case_id, workflow, model, path, "http_error", f"{exc.code}: {details}", "", None, prompt_text)
    except Exception as exc:  # pragma: no cover - defensive path
        return build_result(case_id, workflow, model, path, "error", str(exc), "", None, prompt_text)


def write_output(result: dict[str, Any]) -> None:
    path = output_path(result["workflow"], result["case_id"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")


def write_dry_run_report(results: list[dict[str, Any]]) -> None:
    lines = [
        "# Dry Run Report",
        "",
        "| Case | Workflow | Status | Prompt Path | Output Path |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in results:
        lines.append(
            f"| {result['case_id']} | {result['workflow']} | {result['status']} | {result['prompt_path']} | {output_path(result['workflow'], result['case_id'])} |"
        )
    (OUTPUTS_DIR / "dry_run_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="*", help="Cases such as 001 013 or case_001 case_013")
    parser.add_argument("--workflow", choices=["proposal", "pure_llm", "both"], default="both")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    ensure_output_dirs()
    workflows = workflows_from_arg(args.workflow)
    if args.cases:
        cases = [normalize_case(case_text) for case_text in args.cases]
    else:
        case_set = set()
        for workflow in workflows:
            case_set.update(discover_cases(workflow))
        cases = sorted(case_set)

    results = []
    for workflow in workflows:
        for case_id in cases:
            path = prompt_path(workflow, case_id)
            if not path.exists():
                results.append(
                    build_result(case_id, workflow, os.environ.get("LLM_MODEL", "unknown_model"), path, "missing_prompt", "prompt file not found", "", None, "")
                )
                continue
            result = run_one(case_id, workflow, args.dry_run)
            write_output(result)
            results.append(result)

    if args.dry_run:
        write_dry_run_report(results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
