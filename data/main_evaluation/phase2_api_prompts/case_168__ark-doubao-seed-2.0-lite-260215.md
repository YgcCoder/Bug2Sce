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
{"case_id":"case_168","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_168","fault_layer":"unknown","causal_explanation":"Dataset labels this case as having both lane invasion and red-light violation, while error.json only confirms red-light violation (no lane invasion). There is a mismatch between all-zero actuation commands in /vehicle_cmd and non-zero velocity, throttle, and steering reported in /vehicle_status. No direct module-level fault evidence is available in the provided critical window summary.","root_cause_pattern":"Conservative preservation pattern: Ego vehicle has a confirmed red-light violation (per error.json) with conflicting lane invasion labels, and exhibits movement despite all-zero actuation commands from the Autoware stack.","preservation_constraints":["Preserve the original Town01 map and mission start/goal configuration","Preserve 0 dynamic actors and 2 puddle regions in the scenario","Preserve the mismatch between all-zero /vehicle_cmd commands and non-zero ego movement in the critical window","Preserve a red light along the ego route for violation validation"],"uncertainty":["Conflict between dataset and error.json labels: dataset claims lane invasion, error.json does not","No confirmed stop-line crossing for red-light violation per provided evidence","No confirmed lane boundary crossing for lane invasion per provided evidence","Actuation fault cannot be confirmed from vehicle_cmd/vehicle_status mismatch alone per analysis rules"],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Resolve the lane invasion label conflict via manual review before confirming generated same-root-cause cases","Verify the vehicle_cmd/vehicle_status mismatch is preserved in generated candidate scenarios","Check for stop-line crossing to confirm red-light violation after scenario execution"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":104.8687973022461,"y":59.99010467529297,"z":0.29999998211860657,"pitch":0.0,"yaw":0.0,"roll":0.0},"destination":{"x":392.4700012207031,"y":105.38999938964844,"z":0.29999998211860657,"yaw":90.00004577636719}},"weather":{"cloud":65,"rain":37,"puddle":36,"wind":55,"fog":52,"wetness":46,"angle":91,"altitude":17},"actors":[],"puddles":[{"index":0,"level":1.78,"location":{"x":102.653,"y":36.356,"z":0.0},"size":{"x":300.0,"y":500.0,"z":1000.0}},{"index":1,"level":1.69,"location":{"x":107.359,"y":89.751,"z":0.0},"size":{"x":500.0,"y":500.0,"z":1000.0}}]}}