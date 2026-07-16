# Loop2 Recommended Minimal Set

Purpose: run a small feedback-loop experiment after first-round B2S manual review.

- Zero-success seed cases in B2S cand_001: 9
- Models selected per case: gpt-4o-2024-11-20, claude-sonnet-4-5
- Total loop2 candidates: 18

This is not the main RQ3 comparison. It is an optional iterative repair / feedback-loop experiment.

## Zero-success cases
- case_024: expected=C+R
- case_037: expected=C+L+R
- case_039: expected=L+S
- case_061: expected=C+L+R
- case_069: expected=C+L
- case_094: expected=C+L+S
- case_112: expected=C+L
- case_118: expected=C+L+R
- case_147: expected=C+L

## Output
CSV: `<WORKSPACE_ROOT>/processed/experiments/b2s_main_review/loop2_recommended_zero_success_cases_gpt4o_claude.csv`