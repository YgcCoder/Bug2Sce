# RQ4 Loop2 Minimal Plan: Claude-only

Decision: use `claude-sonnet-4-5` as the single feedback-loop model.

Rationale:
- In Pure-LLM manual review, Claude is tied for the highest strict YES count among models.
- In B2S manual review, Claude is tied for the highest strict YES count among models.
- Claude is newer and easier to justify than GPT-4o as the selected loop2 model.
- Single-model loop2 keeps the RQ4 budget small under time pressure.

Budget:
- 9 zero-success seed cases from B2S first pass.
- 1 model per case: Claude Sonnet 4.5.
- Total: 9 loop2 candidates.

Selected cases:
- case_024 expected=C+R first_round_label=uncertain observed=C
- case_037 expected=C+L+R first_round_label=no observed=R
- case_039 expected=L+S first_round_label=no observed=
- case_061 expected=C+L+R first_round_label=no observed=R
- case_069 expected=C+L first_round_label=no observed=
- case_094 expected=C+L+S first_round_label=uncertain observed=C
- case_112 expected=C+L first_round_label=no observed=
- case_118 expected=C+L+R first_round_label=no observed=R
- case_147 expected=C+L first_round_label=no observed=

CSV: `<WORKSPACE_ROOT>/processed/experiments/matched_main_review/loop2_recommended_zero_success_cases_claude_only.csv`