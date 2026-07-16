# Data dictionary

## Preservation labels

- `strictly preserved`: the candidate retains the seed's failure mechanism under the available execution, trace, oracle, and manual evidence.
- `partial or boundary`: the candidate retains relevant mechanism evidence but crosses a boundary or lacks enough evidence for the strict label.
- `not preserved`: the scenario is invalid, produces no relevant failure, or exhibits a different failure mechanism.

The paper's **strict** rate uses only the first category. Its **inclusive** rate is the set union of the first two categories; the categories are not added twice.

## Main identifiers

- `case_id`: one of the 30 selected DriveFuzz seed failures.
- `model`: the LLM backbone used for the generation call.
- `candidate_id`: a unique seed-model-candidate tuple.
- `expected_oracle_codes`: seed oracles (`C`, `R`, `L`, and `S`).
- `observed_oracle_codes`: oracle symptoms observed during candidate execution.
- `manual_same_root_cause`: final strict/partial/not-preserved judgment in the normalized review tables.

## RQ4 fields

- `round`: feedback iteration (`1`-`5` in data; figures display `Rd1`-`Rd5` to avoid confusion with workflow arrows).
- `active_seeds`: seeds not removed by the seed-level stopping rule.
- `cumulative_strict_seeds`: seeds with at least one strictly preserved candidate by that round.
- `cumulative_evidence_seeds`: seeds with strict or partial/boundary evidence by that round.
- `request_tokens_per_actual_context_object`: request tokens normalized by the actual context records used for the call.
- `response_tokens_per_generated_candidate`: response tokens normalized by generated candidates.
