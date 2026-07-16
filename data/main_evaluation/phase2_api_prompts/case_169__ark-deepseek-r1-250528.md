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
{"case_id":"case_169","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_169","fault_layer":"unknown","causal_explanation":"Consistent labeling between dataset and error.json confirms a red light violation event. No actors or puddles are present in the scenario. All sampled vehicle_cmd outputs are zero in the critical window, but vehicle status shows non-zero velocity up to 9.75 m/s. Route-light relation and stop-line crossing are not confirmed by available evidence, and no specific module failure is directly proven.","root_cause_pattern":"Conservative candidate pattern: Ego travels on a route with red traffic lights, all-zero critical window vehicle command outputs are observed while ego has non-zero movement, resulting in a consistently labeled red light violation with unconfirmed stop-line crossing.","preservation_constraints":["Preserve consistent red light violation labeling between dataset and error json","Preserve zero dynamic actors and zero puddle regions in the scenario","Preserve Town01 map and ego's start-goal mission route","Preserve all-zero vehicle command values in the critical sampling window"],"uncertainty":["Route-light relation is unconfirmed: it is unknown if the red light was on ego's planned route","Stop-line crossing is unconfirmed, so the red light violation is not geographically verified","Module-level fault cannot be attributed due to missing critical evidence of internal module behavior","Mismatch between all-zero vehicle_cmd and non-zero vehicle velocity is unexplained"],"ready_for_phase2_generation":"yes","notes_for_validator":["Record stop-line crossing status during execution to verify the red light violation event","Check if the mismatch between all-zero vehicle_cmd and non-zero ego movement is preserved in generated cases"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":334.21539306640625,"y":145.67129516601562,"z":1.5,"pitch":0.0,"yaw":90.00005340576172,"roll":0.0},"destination":{"x":338.97998046875,"y":301.2599792480469,"z":1.5,"yaw":90.00005340576172}},"weather":{"cloud":73,"rain":14,"puddle":19,"wind":4,"fog":93,"wetness":23,"angle":272,"altitude":17},"actors":[],"puddles":[]}}