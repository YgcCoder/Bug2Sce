# B2S cand_001 Manual Review Summary

Source: `<WORKSPACE_ROOT>/b2s_review_videos/review_checklist.csv`

## Overall

- Total candidates: 180
- Manually checked: 180
- Manual same-root-cause YES: 65
- Manual same-root-cause NO: 81
- Manual uncertain: 34
- Confirmed same-root-cause rate over all 180: 36.11%
- Confirmed same-root-cause rate among decided YES/NO: 44.52%

## Manual Failure Type Counts

- R: 62
- L+R: 23
- L: 21
- S: 17
- R+S: 13
- C+L+R: 10
- C: 7
- C+R: 5
- (blank): 5
- R+L: 5
- C+R+L: 3
- L+R+S: 2
- C+L: 2
- L+S+C: 1
- C+R+S: 1
- R+C: 1
- S+L+R: 1
- L+S: 1

## By Model

| Model | Total | YES | NO | Uncertain | YES/all | YES/decided |
|---|---:|---:|---:|---:|---:|---:|
| ark-deepseek-r1-250528 | 30 | 10 | 17 | 3 | 33.33% | 37.04% |
| ark-doubao-seed-2.0-lite-260215 | 30 | 11 | 17 | 2 | 36.67% | 39.29% |
| claude-sonnet-4-5 | 30 | 13 | 11 | 6 | 43.33% | 54.17% |
| gemini-2.5-pro | 30 | 8 | 16 | 6 | 26.67% | 33.33% |
| gpt-4o-2024-11-20 | 30 | 13 | 10 | 7 | 43.33% | 56.52% |
| gpt-5.1 | 30 | 10 | 10 | 10 | 33.33% | 50.00% |

## By Expected Oracle

| Expected oracle | Total | YES | NO | Uncertain | YES/all |
|---|---:|---:|---:|---:|---:|
| C | 18 | 7 | 9 | 2 | 38.89% |
| C+L | 18 | 0 | 15 | 3 | 0.00% |
| C+L+R | 24 | 1 | 22 | 1 | 4.17% |
| C+L+S | 6 | 0 | 5 | 1 | 0.00% |
| C+R | 6 | 0 | 3 | 3 | 0.00% |
| L | 6 | 2 | 3 | 1 | 33.33% |
| L+R | 36 | 17 | 12 | 7 | 47.22% |
| L+R+S | 6 | 1 | 1 | 4 | 16.67% |
| L+S | 12 | 1 | 9 | 2 | 8.33% |
| R | 36 | 24 | 2 | 10 | 66.67% |
| S | 12 | 12 | 0 | 0 | 100.00% |

## Manual vs Code-assisted Triage

| Code-assisted decision | Total | YES | NO | Uncertain | YES/all |
|---|---:|---:|---:|---:|---:|
| invalid_scenario | 3 | 0 | 0 | 3 | 0.00% |
| likely_different_or_weak_evidence | 13 | 0 | 8 | 5 | 0.00% |
| likely_different_root_cause | 10 | 0 | 6 | 4 | 0.00% |
| likely_no_failure_or_no_oracle | 78 | 21 | 48 | 9 | 26.92% |
| likely_same_root_cause_by_code | 27 | 23 | 0 | 4 | 85.19% |
| possible_same_root_cause_needs_video | 44 | 17 | 18 | 9 | 38.64% |
| unknown_hang | 5 | 4 | 1 | 0 | 80.00% |

## Next Immediate Step

Pure-LLM manual review is still needed before RQ3 can report confirmed same-root-cause counts for both methods. Until then, B2S cand_001 has confirmed manual results, but the matched B2S-vs-Pure-LLM RQ3 table still lacks Pure-LLM manual ground truth.