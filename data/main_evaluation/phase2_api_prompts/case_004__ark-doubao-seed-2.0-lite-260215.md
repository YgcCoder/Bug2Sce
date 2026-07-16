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
{"case_id":"case_004","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_004","fault_layer":"unknown","causal_explanation":"Dataset labels this case as having both lane invasion and red-light violation, but error.json only confirms red-light violation with no lane invasion. No critical-window evidence confirms stop-line crossing for red-light violation or lane-boundary crossing for lane invasion, and failure cannot be localized to any specific Autoware module. The scenario has 0 dynamic actors and 1 puddle region.","root_cause_pattern":"Conservative preservation pattern: Ego travels a mission on Town01 with 0 dynamic actors and 1 puddle, has a confirmed red-light event and conflicting lane invasion labels, with no confirmed module-level root cause.","preservation_constraints":["Preserve the conflicting lane invasion label status between dataset and error.json","Preserve 1 puddle region and 0 dynamic actors in the scenario","Preserve the same start and goal mission on the Town01 map","Preserve the confirmed red-light event from error.json"],"uncertainty":["Dataset and error.json disagree on lane invasion label and scenario group","Route-light relation and stop-line crossing for red-light violation are not confirmed","Lane boundary crossing for lane invasion is not confirmed by evidence","Failure cannot be localized to any specific Autoware module"],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Resolve label conflict between dataset and error.json before confirming generated case root cause","Validate both stop-line crossing for red-light violation and lane-boundary crossing for lane invasion after execution","Check if any module failure can be localized from post-generation critical window evidence"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":24,"rain":7,"puddle":9,"wind":93,"fog":19,"wetness":29,"angle":105,"altitude":71},"actors":[],"puddles":[{"index":0,"level":0.09,"location":{"x":350.843,"y":129.224,"z":0.0},"size":{"x":650.0,"y":500.0,"z":1000.0}}]}}