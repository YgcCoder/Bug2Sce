#!/usr/bin/env python3
"""Round-independent feedback memory for iterative Bug2Scenario generation.

This module does not alter completed experiment artifacts.  It provides the
stable record format that the anonymized implementation and future rounds can
use to retain failed, boundary, and successful same-seed outcomes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "bug2scenario.feedback.v1"


def normalize_preservation_result(value: Any, execution_status: str = "") -> str:
    label = str(value or "").strip().lower()
    if label in {"yes", "strictly preserved", "strictly_preserved"}:
        return "strictly_preserved"
    if label in {"?", "？", "uncertain", "partial or boundary", "partial_or_boundary"}:
        return "partial_or_boundary"
    if label in {"no", "not preserved", "not_preserved"}:
        return "not_preserved"
    if execution_status == "crash_or_minimal_artifacts":
        return "not_preserved_due_to_crash_or_missing_evidence"
    return "not_reviewed"


def _first(record: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in record and record[key] is not None:
            return record[key]
    return default


def normalize_record(
    *,
    case_id: str,
    round_number: int,
    record: dict[str, Any],
) -> dict[str, Any]:
    """Convert a legacy round-specific record to the stable memory schema."""
    execution = dict(record.get("execution") or {})
    manual = dict(record.get("manual_review") or {})
    execution_status = str(execution.get("status", ""))
    manual_result = normalize_preservation_result(
        _first(manual, "preservation_result", "manual_preservation_result", default=""),
        execution_status,
    )
    candidate_spec = _first(
        record,
        "candidate_spec",
        "round1_candidate_spec",
        "round2_candidate_spec",
        "round3_candidate_spec",
        default={},
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "round": int(round_number),
        "generator": _first(record, "generator", "model", default=""),
        "candidate_id": (candidate_spec or {}).get("candidate_id", ""),
        "candidate_spec": candidate_spec or {},
        "execution": execution,
        "automatic_analysis": record.get("automatic_analysis") or {},
        "manual_review": {
            "preservation_result": manual_result,
            "observed_failure_type": _first(
                manual, "observed_failure_type", "manual_failure_type", default=""
            ),
            "notes": manual.get("notes", ""),
        },
        "memory_role": "historical_outcome_not_authoritative_target",
    }


def build_case_memory(
    case_id: str,
    round_batches: Iterable[tuple[int, Iterable[dict[str, Any]]]],
) -> dict[str, Any]:
    records = [
        normalize_record(case_id=case_id, round_number=round_number, record=record)
        for round_number, batch in round_batches
        for record in batch
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "case_id": case_id,
        "record_policy": "retain_failed_boundary_and_successful_same_seed_attempts",
        "records": records,
    }


def save_memory(path: Path, memory: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(memory, ensure_ascii=False, indent=2), encoding="utf-8")


def load_memory(path: Path) -> dict[str, Any]:
    memory = json.loads(path.read_text(encoding="utf-8"))
    if memory.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"Unsupported feedback schema: {memory.get('schema_version')}")
    return memory


def seed_is_recovered(memory: dict[str, Any]) -> bool:
    return any(
        (record.get("manual_review") or {}).get("preservation_result")
        == "strictly_preserved"
        for record in memory.get("records", [])
    )
