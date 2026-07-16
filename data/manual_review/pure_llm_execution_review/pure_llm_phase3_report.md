# Pure-LLM Phase 3 Execution Audit

Generated: <REDACTED_TIMESTAMP>

- JSON dir: `<PSSD_ROOT>/PURE_LLM_JSON`
- Runs dir: `<PSSD_ROOT>/PURE_LLM_RUNS`
- Total Pure-LLM candidates: 180
- JSON-valid candidates: 180 / 180

## Artifact Availability

| Artifact | Candidate count | Ratio |
|---|---:|---:|
| output directories | 180 | 100.0% |
| camera videos | 173 | 96.1% |
| rosbags | 94 | 52.2% |
| score files | 62 | 34.4% |
| error JSON files | 94 | 52.2% |

## Execution Status Counts

| Status | Count | Ratio |
|---|---:|---:|
| oracle_triggered | 87 | 48.3% |
| partial_artifacts_no_oracle | 80 | 44.4% |
| crash_or_minimal_artifacts | 6 | 3.3% |
| no_failure_reached_goal | 6 | 3.3% |
| trace_ready_no_oracle | 1 | 0.6% |

## Oracle Match Counts

| Match status | Count | Ratio |
|---|---:|---:|
| no_observed_oracle | 93 | 51.7% |
| partial_oracle_overlap | 47 | 26.1% |
| exact_oracle_match | 24 | 13.3% |
| different_oracle_symptom | 15 | 8.3% |
| observed_superset_contains_expected | 1 | 0.6% |

## Preliminary Categories

| Category | Count | Ratio |
|---|---:|---:|
| no observed oracle / incomplete | 87 | 48.3% |
| needs same-root-cause review | 72 | 40.0% |
| different failure | 15 | 8.3% |
| invalid / crash | 6 | 3.3% |

## Model Summary

| model | total | has_rosbag | has_camera | oracle_triggered | exact_oracle_match | observed_superset_contains_expected | partial_oracle_overlap | different_oracle_symptom | invalid_crash | no_observed_oracle_or_incomplete | needs_same_root_cause_review |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ark-deepseek-r1-250528 | 30 | 15 | 30 | 13 | 4 | 0 | 8 | 1 | 0 | 17 | 12 |
| ark-doubao-seed-2.0-lite-260215 | 30 | 17 | 30 | 14 | 5 | 0 | 8 | 1 | 0 | 16 | 13 |
| claude-sonnet-4-5 | 30 | 15 | 28 | 15 | 2 | 1 | 9 | 3 | 2 | 13 | 12 |
| gemini-2.5-pro | 30 | 16 | 29 | 16 | 4 | 0 | 9 | 3 | 1 | 13 | 13 |
| gpt-4o-2024-11-20 | 30 | 17 | 28 | 15 | 6 | 0 | 7 | 2 | 1 | 14 | 13 |
| gpt-5.1 | 30 | 14 | 28 | 14 | 3 | 0 | 6 | 5 | 2 | 14 | 9 |

## Files

- `<WORKSPACE_ROOT>/processed/experiments/pure_llm_execution_review/pure_llm_phase3_execution_results.csv`
- `<WORKSPACE_ROOT>/processed/experiments/pure_llm_execution_review/pure_llm_phase3_summary_by_model.csv`
- `<WORKSPACE_ROOT>/processed/experiments/pure_llm_execution_review/pure_llm_phase3_summary_by_case.csv`
