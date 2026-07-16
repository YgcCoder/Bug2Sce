#!/usr/bin/env python3
"""Import manually pasted webpage LLM results into llm_outputs JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "processed"
MANUAL_RESULTS = PROCESSED / "manual_llm_results"
PROMPTS = PROCESSED / "prompts"
LLM_OUTPUTS = PROCESSED / "llm_outputs"
CASES = ["001", "024", "027", "013"]
WORKFLOWS = ["proposal", "pure_llm"]


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


def output_json(case_id: str, workflow: str, raw_text: str, prompt_path: Path, source_path: Path) -> dict[str, Any]:
    if not raw_text.strip():
        return {
            "case_id": f"case_{case_id}",
            "workflow": workflow,
            "model": "manual_web_llm_unknown",
            "prompt_path": str(prompt_path),
            "raw_response": "",
            "parsed_response": None,
            "status": "manual_missing",
            "error_message": f"manual response file is empty: {source_path}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    parsed = extract_json_from_text(raw_text)
    if parsed is None:
        return {
            "case_id": f"case_{case_id}",
            "workflow": workflow,
            "model": "manual_web_llm_unknown",
            "prompt_path": str(prompt_path),
            "raw_response": raw_text,
            "parsed_response": None,
            "status": "parse_failed",
            "error_message": "manual response was not valid JSON",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    return {
        "case_id": f"case_{case_id}",
        "workflow": workflow,
        "model": "manual_web_llm_unknown",
        "prompt_path": str(prompt_path),
        "raw_response": raw_text,
        "parsed_response": parsed,
        "status": "completed",
        "error_message": "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    for workflow in WORKFLOWS:
        (LLM_OUTPUTS / workflow).mkdir(parents=True, exist_ok=True)
        for case_id in CASES:
            source = MANUAL_RESULTS / workflow / f"case_{case_id}_raw_response.md"
            prompt_path = PROMPTS / workflow / f"case_{case_id}_prompt.md"
            raw_text = source.read_text(encoding="utf-8") if source.exists() else ""
            data = output_json(case_id, workflow, raw_text, prompt_path, source)
            target = LLM_OUTPUTS / workflow / f"case_{case_id}_output.json"
            target.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
