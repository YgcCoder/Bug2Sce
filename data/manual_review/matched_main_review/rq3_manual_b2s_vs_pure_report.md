# RQ3 Manual Comparison: Bug2Scenario vs Pure-LLM

Sources:
- B2S: `<WORKSPACE_ROOT>/processed/experiments/b2s_main_review/b2s_cand001_manual_review_normalized.csv`
- Pure-LLM: `<WORKSPACE_ROOT>/pure_llm_all180_videos/review_checklist.xlsx`

## Overall

| Method | Total | Checked | Strict YES | Partial/uncertain | Inclusive YES+partial | NO | Strict rate | Inclusive rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Bug2Scenario cand_001 | 180 | 180 | 65 | 34 | 99 | 81 | 36.11% | 55.00% |
| Pure-LLM all180 | 180 | 180 | 53 | 27 | 80 | 100 | 29.44% | 44.44% |

## By Model

| Model | B2S YES | B2S partial | B2S incl. | Pure YES | Pure partial | Pure incl. | Delta YES | Delta incl. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ark-deepseek-r1-250528 | 10 | 3 | 13 | 10 | 3 | 13 | 0 | 0 |
| ark-doubao-seed-2.0-lite-260215 | 11 | 2 | 13 | 10 | 2 | 12 | 1 | 1 |
| claude-sonnet-4-5 | 13 | 6 | 19 | 10 | 5 | 15 | 3 | 4 |
| gemini-2.5-pro | 8 | 6 | 14 | 9 | 3 | 12 | -1 | 2 |
| gpt-4o-2024-11-20 | 13 | 7 | 20 | 9 | 6 | 15 | 4 | 5 |
| gpt-5.1 | 10 | 10 | 20 | 5 | 8 | 13 | 5 | 7 |

## Interpretation

Use strict YES as conservative same-root-cause success. Use YES+partial/uncertain as preservation-relevant / boundary-preserving rate. Do not collapse partial into strict success.

## Paired Exact Check

The paired comparison uses the same 180 case-model pairs for both methods.

| Metric | B2S-only success | Pure-only success | Discordant pairs | Two-sided exact p |
|---|---:|---:|---:|---:|
| Strict YES | 29 | 17 | 46 | 0.104 |
| Inclusive YES+partial | 35 | 16 | 51 | 0.011 |

Interpretation: the strict confirmed same-root-cause gain is positive but not significant at p<0.05, while the inclusive preservation-relevant gain is significant under the paired exact check. This supports reporting both a conservative strict rate and an inclusive boundary-preservation rate.
