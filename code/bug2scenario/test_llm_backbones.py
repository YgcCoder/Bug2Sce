#!/usr/bin/env python3
"""Smoke-test OpenAI-compatible LLM backbones for Bug2Scenario.

The script reads model IDs from processed/experiments/llm_backbone_config.yaml
and tests a minimal chat completion request. It never prints or writes API keys.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from openai import OpenAI


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "processed/experiments/llm_backbone_config.yaml"
OUT_JSON = ROOT / "processed/experiments/api_model_smoke_test_results.json"
OUT_MD = ROOT / "processed/experiments/api_model_smoke_test_results.md"
COMPSAC_ENV = Path("<PRIVATE_CONFIG_ROOT>/compsac26-1原始代码/.env")


def load_dotenv_value(path: Path, key: str) -> str | None:
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        if name.strip() == key:
            return value.strip().strip('"').strip("'")
    return None


def load_config() -> dict[str, Any]:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def model_map(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {m["name"]: m for m in config.get("models", [])}


def build_params(model_id: str, token_parameter: str | None, omit_temperature: bool) -> dict[str, Any]:
    params: dict[str, Any] = {
        "model": model_id,
        "messages": [
            {
                "role": "system",
                "content": "You are a strict JSON generator. Return exactly one JSON object.",
            },
            {
                "role": "user",
                "content": (
                    "Return exactly one JSON object and echo the requested model id. "
                    f'The requested model id is "{model_id}". '
                    '{"ok": true, "requested_model_id": "<requested_model_id>", '
                    '"purpose": "bug2scenario_smoke_test"}'
                ),
            },
        ],
    }
    params[token_parameter or "max_tokens"] = 120
    if not omit_temperature:
        params["temperature"] = 0.2
    return params


def try_call(client: OpenAI, model: dict[str, Any]) -> dict[str, Any]:
    model_id = model["model_id"]
    token_parameter = model.get("token_parameter")
    omit_temperature = bool(model.get("omit_temperature", False))
    params = build_params(model_id, token_parameter, omit_temperature)
    started = time.time()
    retries: list[str] = []

    for attempt in range(3):
        try:
            response = client.chat.completions.create(**params)
            elapsed = round(time.time() - started, 3)
            content = response.choices[0].message.content or ""
            usage = response.usage
            return {
                "name": model["name"],
                "model_id": model_id,
                "status": "ok",
                "elapsed_sec": elapsed,
                "usage": {
                    "prompt_tokens": getattr(usage, "prompt_tokens", None),
                    "completion_tokens": getattr(usage, "completion_tokens", None),
                    "total_tokens": getattr(usage, "total_tokens", None),
                },
                "response_preview": content[:500],
                "error_message": "",
                "retries": retries,
            }
        except Exception as exc:  # noqa: BLE001 - smoke test records provider-specific errors.
            error = str(exc)
            retries.append(error[:300])
            if "max_tokens" in error and "max_completion_tokens" in error and "max_tokens" in params:
                params["max_completion_tokens"] = params.pop("max_tokens")
                continue
            if "temperature" in error and "temperature" in params:
                params.pop("temperature", None)
                continue
            if attempt < 2:
                time.sleep(1 + attempt)
                continue
            return {
                "name": model["name"],
                "model_id": model_id,
                "status": "failed",
                "elapsed_sec": round(time.time() - started, 3),
                "usage": {},
                "response_preview": "",
                "error_message": error[:1000],
                "retries": retries,
            }

    return {
        "name": model["name"],
        "model_id": model_id,
        "status": "failed",
        "elapsed_sec": round(time.time() - started, 3),
        "usage": {},
        "response_preview": "",
        "error_message": "unknown error",
        "retries": retries,
    }


def write_markdown(report: dict[str, Any]) -> None:
    lines = [
        "# API Model Smoke Test Results",
        "",
        f"- Timestamp: `{report['timestamp']}`",
        f"- Base URL: `{report['base_url']}`",
        f"- API key source: `{report['api_key_source']}`",
        "",
        "| Model | Status | Total Tokens | Notes |",
        "|---|---:|---:|---|",
    ]
    for result in report["results"]:
        tokens = result.get("usage", {}).get("total_tokens", "")
        note = result["response_preview"].replace("\n", " ")[:120] if result["status"] == "ok" else result["error_message"].replace("\n", " ")[:120]
        lines.append(f"| `{result['name']}` | `{result['status']}` | `{tokens}` | {note} |")
    lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", help="Model names to test. Defaults to config pilot models.")
    args = parser.parse_args()

    config = load_config()
    api_key_env = config.get("api_key_env", "OPAPI_KEY")
    api_key = os.environ.get(api_key_env)
    api_key_source = f"env:{api_key_env}"
    if not api_key:
        api_key = load_dotenv_value(COMPSAC_ENV, api_key_env)
        api_key_source = str(COMPSAC_ENV)
    if not api_key:
        raise SystemExit(f"Missing API key. Set {api_key_env} or provide it in {COMPSAC_ENV}.")

    models_by_name = model_map(config)
    selected_names = args.models or config.get("pilot_recommendation", {}).get("models_first_try", [])
    selected = []
    for name in selected_names:
        if name not in models_by_name:
            raise SystemExit(f"Unknown model in config: {name}")
        selected.append(models_by_name[name])

    client = OpenAI(api_key=api_key, base_url=config["base_url"], timeout=config.get("default_generation", {}).get("timeout", 120))
    results = [try_call(client, model) for model in selected]
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "base_url": config["base_url"],
        "api_key_env": api_key_env,
        "api_key_source": api_key_source,
        "results": results,
    }
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    for result in results:
        print(f"{result['name']}: {result['status']}")


if __name__ == "__main__":
    main()
