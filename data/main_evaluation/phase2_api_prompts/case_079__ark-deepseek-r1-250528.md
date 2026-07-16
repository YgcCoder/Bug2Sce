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
{"case_id":"case_079","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_079","fault_layer":"unknown","causal_explanation":"Dataset labels this case as both lane invasion and red-light violation, while error.json only confirms red-light violation, with lane invasion unconfirmed. Vehicle_cmd reports all zero commands but vehicle_status shows non-zero movement, and no critical-window evidence directly localizes failure to a specific module.","root_cause_pattern":"Conservative preservation pattern: Ego encounters a red-state traffic light during mission execution on Town01, with conflicting symptom labels between dataset and oracle output, and module-level cause unconfirmed.","preservation_constraints":["Preserve mission start and goal positions on Town01 map","Preserve presence of 2 actors in the scenario","Preserve the original weather condition values","Preserve the conflicting label status between dataset and error.json","Preserve presence of at least one red-state traffic light encountered during mission"],"uncertainty":["Conflicting labels: dataset lane_invasion=1, error_json lane_invasion=0; dataset group=L+R, error_json group=R","Route-light relation and stop-line crossing for red-light violation are not confirmed","No evidence directly localizes failure to a specific Autoware module","Lane invasion event is not confirmed by error.json","Vehicle_cmd is all zero but vehicle_status shows non-zero movement, so controller behavior is uncertain"],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Manual review is required to resolve conflicting labels before root cause classification","Post-generation validation must check for both red-light violation and lane invasion to align with original labels"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":59,"rain":63,"puddle":75,"wind":24,"fog":32,"wetness":57,"angle":227,"altitude":22},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":318.806,"y":120.233,"z":1.5,"pitch":0.0,"yaw":77.296,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":0.63,"spawn":{"x":304.093,"y":135.488,"z":1.5,"pitch":0.0,"yaw":262.763,"roll":0.0}}],"puddles":[]}}