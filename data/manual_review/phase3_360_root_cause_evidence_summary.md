# Phase 3 Code-based Root-Cause Evidence Summary

This file summarizes automatic checks based on original DriveFuzz bug JSON files and generated candidate execution JSON files. It is triage evidence, not final human ground truth.

## Decision Counts

- `likely_no_failure_or_no_oracle`: 162
- `possible_same_root_cause_needs_video`: 81
- `likely_same_root_cause_by_code`: 57
- `likely_different_or_weak_evidence`: 23
- `likely_different_root_cause`: 17
- `invalid_scenario`: 10
- `unknown_hang`: 10

## Confidence Counts

- `low`: 247
- `medium`: 86
- `high`: 27

## Output

- CSV: `<WORKSPACE_ROOT>/processed/experiments/main_evaluation_prebatch/phase3_360_root_cause_evidence_table.csv`
