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
{"case_id":"case_010","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_010","fault_layer":"unknown","causal_explanation":"Dataset labels this case as lane invasion, but error_json oracle detects no lane invasion, creating a label conflict. No critical-window evidence directly localizes a failure to any specific Autoware module. An unresolved mismatch exists: all vehicle_cmd control values are zero, but vehicle_status reports non-zero ego velocity.","root_cause_pattern":"Conservative preservation pattern: Ego traverses to the goal on Town01 with no other dynamic actors, under high wetness/rain with multiple puddles, and has conflicting lane invasion labels across dataset and error oracle, with no confirmed module-level failure.","preservation_constraints":["Preserve no other dynamic actors in the scenario","Preserve the original start and goal mission positions on Town01 map","Preserve high wetness and rain conditions with multiple puddle regions","Preserve the conflicting label structure for validation"],"uncertainty":["Dataset labels lane_invasion=1 while error.json reports lane_invasion=0, confirmed label conflict","No evidence of actual lane boundary crossing is provided","No module-level failure attribution is supported by critical-window evidence","Mismatch between all-zero vehicle_cmd and non-zero velocity is unresolved"],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Manual review is required to resolve the lane invasion label conflict before validating reproductions","Check for actual lane boundary crossing in any generated reproduction","Check if the vehicle_cmd/vehicle_status mismatch reproduces"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":110.0,"y":129.0,"z":1.0,"pitch":0.0,"yaw":180.0,"roll":0.0},"destination":{"x":113.0,"y":130.0,"z":0.0,"yaw":0.0}},"weather":{"cloud":83,"rain":57,"puddle":74,"wind":30,"fog":3,"wetness":79,"angle":278,"altitude":7},"actors":[],"puddles":[{"index":0,"level":0.08,"location":{"x":111.012,"y":125.676,"z":0.0},"size":{"x":800.0,"y":700.0,"z":1000.0}},{"index":1,"level":0.57,"location":{"x":131.334,"y":131.335,"z":0.0},"size":{"x":800.0,"y":800.0,"z":1000.0}},{"index":2,"level":0.21,"location":{"x":107.58,"y":139.272,"z":0.0},"size":{"x":650.0,"y":650.0,"z":1000.0}}]}}