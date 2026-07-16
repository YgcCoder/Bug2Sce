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
{"case_id":"case_143","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_143","fault_layer":"unknown","causal_explanation":"Conflicting failure labels exist between dataset and error.json: dataset labels both lane invasion and red-light violation, while error.json only confirms red-light violation. No module-level failure is directly supported by critical-window evidence, and route-light relation, stop-line crossing, and lane boundary crossing are all unconfirmed.","root_cause_pattern":"Conservative preservation pattern: Ego travels on Town01 map with no other actors or puddles, encounters a red traffic light, with conflicting oracle labels for lane invasion, and root cause attribution to a specific module remains unknown.","preservation_constraints":["Preserve the red-light violation symptom confirmed by error.json","Preserve zero dynamic actors and zero puddle regions in the scenario","Preserve the ego's start and goal mission on Town01 map","Preserve the conflicting lane invasion label between dataset and error.json","Require post-generation validation to check stop-line crossing and lane boundary crossing status"],"uncertainty":["Dataset and error.json have conflicting labels for lane invasion and failure group assignment","Route-light relation and stop-line crossing are not confirmed by available evidence","Lane boundary crossing is not confirmed for the dataset-labeled lane invasion","No critical-window evidence directly localizes failure to a specific Autoware layer or component","Mismatch between all-zero vehicle_cmd and non-zero velocity in vehicle_status means controller behavior cannot be confirmed"],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Manual review is required to resolve the label conflict between dataset and error.json before confirming same-root-cause classification","Post-execution validation must check stop-line crossing to confirm red-light violation and lane boundary crossing to confirm lane invasion status","Validate the controller command-velocity mismatch when replicating this case"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":19,"rain":43,"puddle":36,"wind":22,"fog":41,"wetness":71,"angle":148,"altitude":56},"actors":[],"puddles":[]}}