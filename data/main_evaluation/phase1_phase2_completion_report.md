# Phase 1/2 Completion Report

Scope: selected 30 DriveFuzz seed cases; no CARLA/Autoware/DriveFuzz simulation was executed in this stage.

## Models

| Model | Phase1 completed | Phase1 ready yes | Phase1 uncertain | Phase1 tokens | Phase2 completed | Candidate JSON | Pre-valid | Phase2 tokens |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `ark-doubao-seed-2.0-lite-260215` | 30/30 | 17 | 13 | 183997 | 30/30 | 60/60 | 60/60 | 115463 |
| `ark-deepseek-r1-250528` | 30/30 | 18 | 12 | 182918 | 30/30 | 60/60 | 60/60 | 120981 |
| `gpt-4o-2024-11-20` | 30/30 | 12 | 18 | 104451 | 30/30 | 60/60 | 60/60 | 53604 |
| `gpt-5.1` | 30/30 | 15 | 15 | 129257 | 30/30 | 60/60 | 60/60 | 90143 |
| `claude-sonnet-4-5` | 30/30 | 13 | 17 | 140773 | 30/30 | 60/60 | 60/60 | 69201 |
| `gemini-2.5-pro` | 30/30 | 18 | 12 | 207710 | 30/30 | 60/60 | 60/60 | 117150 |

Overall status: complete.

## Output Locations

- Phase 1 outputs: `processed/experiments/phase1_api_outputs/`
- Phase 2 API outputs: `processed/experiments/phase2_api_outputs/`
- Phase 2 candidate JSON roots: `processed/experiments/phase2_candidates/<model>/json/`
- Per-case seed-artifact zips: `processed/experiments/phase2_candidates/<model>/seed-artifact/`
- Phase 1 summary CSV: `processed/experiments/phase1_api_results.csv`
- Phase 2 summary CSV: `processed/experiments/phase2_generation_results.csv`

## Notes

- Gemini Phase 1 required a more compact JSON prompt and higher output limit after early truncation.
- Gemini Phase 2 case_004 required a higher output limit, then completed normally.
- Gemini Phase 2 case_151 produced actors too close to ego; the rule-based concretizer repaired actor minimum distance to 2.5m and recorded the repairs in metadata.
- The generated candidate JSON files are pre-execution validated only. Execution-based validation must be run on the school machine with CARLA/Autoware/DriveFuzz.
