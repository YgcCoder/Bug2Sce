You are the Phase 2 scenario amplifier for Bug2Scenario.
Task: generate high-level, root-cause-preserving candidate scenario specs.

Rules:
- Return exactly one JSON object. Do not use markdown fences.
- Use the Phase 1 root-cause pattern and preservation constraints from the same LLM backbone.
- Do not invent new oracle labels. Preserve the intended oracle/failure pattern when evidence supports it.
- Generate candidate specs only; local rule-based code will concretize them into DriveFuzz-style JSON.
- Keep actor position offsets within [-8, 8] meters on x/y.
- Keep actor speed_delta within [-3, 3].
- Keep mission spawn/destination offsets within [-5, 5] meters, or set keep_original=true.
- Keep weather deltas conservative: each weather_delta should be within [-20, 20].
- Keep puddle level_delta within [-0.2, 0.2] and size_scale within [0.8, 1.2].
- If Phase 1 is uncertainty-heavy, create conservative variants and preserve uncertainty in the output.
- Generate exactly 2 candidate_specs.

Return JSON schema:
{
  "case_id": "case_XXX",
  "candidate_specs": [
    {
      "candidate_id": "cand_001",
      "high_level_variant": "short scenario variant description",
      "mutation_intent": "why this variant preserves the Phase 1 pattern",
      "expected_oracle": "collision | red_light | lane_invasion | stuck | compound | unknown",
      "modifications": {
        "weather_delta": {"rain": 0, "fog": 0, "wetness": 0, "puddle": 0},
        "actor_mutations": [
          {"actor_index": 0, "position_offset": {"x": 0.0, "y": 0.0}, "speed_delta": 0.0}
        ],
        "puddle_mutations": [
          {"puddle_index": 0, "location_offset": {"x": 0.0, "y": 0.0}, "level_delta": 0.0, "size_scale": 1.0}
        ],
        "mission_mutation": {"keep_original": true, "spawn_offset": {"x": 0.0, "y": 0.0}, "destination_offset": {"x": 0.0, "y": 0.0}}
      },
      "pre_execution_validation_rules": ["rule"],
      "post_execution_validation_rules": ["rule"],
      "uncertainty": ["missing evidence"]
    }
  ]
}

Input JSON:
{"case_id":"case_067","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_067","fault_layer":"unknown","causal_explanation":"Conflicting failure labels exist between dataset (stuck, lane invasion, red light violation) and error.json (only red light violation confirmed). Final window has zero ego velocity and all-zero actuation commands, but no direct evidence identifies a failing Autoware module. Stop-line crossing and route-light relation are unconfirmed, no actors or puddles are present.","root_cause_pattern":"Conservative preservation pattern: Ego ends with zero velocity and all-zero actuation commands, with conflicting failure labels between dataset and error.json, only red light event confirmed, no proven module-level root cause.","preservation_constraints":["Preserve conflicting failure label status between dataset and error.json","Preserve all-zero vehicle actuation commands in the final critical window","Preserve absence of dynamic actors and puddles","Preserve unconfirmed status of route-light relation and stop-line crossing"],"uncertainty":["Label conflict between dataset and error.json for stuck and lane invasion","Route-light relation and stop-line crossing are not confirmed","No direct evidence localizes failure to a specific module or layer","Mismatch between historic non-zero throttle and final zero commands cannot confirm actuation fault"],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Resolve label conflict between dataset and error.json before validating generated cases","Check for zero actors, zero puddles, and all-zero final vehicle_cmd after generation"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":3,"rain":23,"puddle":46,"wind":93,"fog":27,"wetness":36,"angle":347,"altitude":44},"actors":[],"puddles":[]}}