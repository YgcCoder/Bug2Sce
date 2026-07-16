# Phase 3 360-Row Manual Review Table

This table lists every Phase 3 candidate exactly once. It is intended for human post-execution classification before the next LLM regeneration loop.

## Manual Columns

- `manual_final_category`: choose one of `same-root-cause failure`, `different-failure scenario`, `no-failure scenario`, `invalid scenario`, or `unknown`.
- `manual_same_root_cause`: use `yes`, `no`, or `uncertain`.
- `manual_failure_type`: use C/S/L/R combinations or a short free-text type.
- `manual_confidence`: use high/medium/low.
- `manual_checked`: set to yes after review.
- `manual_notes`: write the human evidence judgment.
- `loop2_action`: decide whether to keep, repair, regenerate, or discard for the next LLM loop.
- `loop2_feedback_for_llm`: short instruction to feed into the next generation prompt.

## Output

- CSV: `<WORKSPACE_ROOT>/processed/experiments/main_evaluation_prebatch/phase3_360_manual_review_table.csv`
