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
{"case_id":"case_103","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_103","fault_layer":"unknown","causal_explanation":"Label conflict exists between dataset and error_json: dataset labels this case as both lane invasion and red-light violation (group L+R), while error_json only confirms red-light violation with no lane invasion. No available evidence directly identifies which Autoware module caused the violation, and route-light relation/stop-line crossing for the red event are unconfirmed.","root_cause_pattern":"Conservative preservation pattern: Ego operates in heavy rainy weather with puddles on Town01 map, with a confirmed red light in the critical window and conflicting oracle labels for lane invasion, no confirmed module-level root cause is available from evidence.","preservation_constraints":["Preserve Town01 base map and original mission start/goal region","Preserve high rain intensity, high wetness, and multiple puddle regions","Preserve one non-ego actor in the scenario","Preserve a red traffic light in the critical window","Preserve the original conflicting lane invasion label status"],"uncertainty":["Conflicting lane invasion and fault group labels between dataset and error_json","Route-light relation and stop-line crossing for red-light violation are unconfirmed","Mismatch between all-zero vehicle_cmd and non-zero velocity/throttle in vehicle_status makes actuation behavior uncertain","No critical-window evidence directly attributes failure to a specific Autoware module"],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Resolve the label conflict via manual review before grouping same-root-cause generated cases","Post-generation validation must confirm red light presence in critical window and preserve weather/puddle conditions"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":74,"rain":96,"puddle":72,"wind":56,"fog":26,"wetness":69,"angle":135,"altitude":9},"actors":[{"index":0,"type":"vehicle","nav_type":"linear","speed":3.55,"spawn":{"x":331.013,"y":149.095,"z":1.5,"pitch":0.0,"yaw":68.769,"roll":0.0}}],"puddles":[{"index":0,"level":0.26,"location":{"x":339.0,"y":129.159,"z":0.0},"size":{"x":350.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.24,"location":{"x":313.918,"y":140.757,"z":0.0},"size":{"x":800.0,"y":800.0,"z":1000.0}}]}}