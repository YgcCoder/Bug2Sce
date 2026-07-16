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
{"case_id":"case_029","model_name":"gpt-5.1","phase1_output":{"case_id":"case_029","fault_layer":"unknown","causal_explanation":"The oracle error_json reports a red-light violation while dataset labels additionally report lane invasion, but the two disagree on lane invasion. Traffic light states and planning/actuation topics are present throughout the run, and error_json marks no collision or stuck. Route–light relation and stop-line crossing are explicitly unknown, so only a generic red-light violation symptom is supported without clear module-level attribution.","root_cause_pattern":"Conservative preservation pattern: ego is driving in a scenario with multiple active traffic lights, reaches the red-light oracle violation condition without crash or stuck, while route–light relation and lane-boundary behavior remain unconfirmed and module-level responsibility is unknown.","preservation_constraints":["The generated candidate should reproduce the same oracle symptom type: a red-light violation flagged in error_json, without collision or stuck.","Traffic lights should be present and publishing multiple state values (including a red state) during the critical window.","Planning outputs (final_waypoints) and vehicle_status should be available up to the violation time.","Route–light geometric relation and exact stop-line crossing may remain unconfirmed by summaries (unknown in evidence).","Lane invasion status may be absent or conflicting between dataset and oracle, preserving label uncertainty."],"uncertainty":["Dataset.xlsx reports lane_invasion=1 and group=L+R, while error_json reports lane_invasion=false and group=R only.","The exact relationship between the ego route and traffic lights (route-light relation) and stop-line crossing is explicitly marked unknown.","Internal behaviors of perception, prediction, planning, and control modules around the violation are not directly observable from the summaries.","The cause of the vehicle_cmd all-zero pattern relative to nonzero vehicle_status velocity is unclear and cannot be attributed to a specific layer."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["For same-root-cause candidates, verify post-execution that error_json reports a red-light violation without crash or stuck.","Check that traffic_lights messages are present with multiple states, including red, before the violation time.","Confirm that planning (final_waypoints) and vehicle_status data are available near the violation, without requiring proof of specific internal planning or control errors.","Do not require evidence of lane invasion or exact stop-line crossing; allow these to remain unknown or conflicting as in the original case.","Avoid attributing the cause to a specific module unless additional run-time evidence beyond these summaries becomes available."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"pitch":0.0,"yaw":-89.99993896484375,"roll":0.0},"destination":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":100,"rain":1,"puddle":8,"wind":6,"fog":12,"wetness":13,"angle":91,"altitude":81},"actors":[{"index":0,"type":"walker","nav_type":"linear","speed":2.78,"spawn":{"x":343.807,"y":136.276,"z":1.5,"pitch":0.0,"yaw":29.582,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":1.67,"spawn":{"x":340.651,"y":106.21,"z":1.5,"pitch":0.0,"yaw":267.899,"roll":0.0}}],"puddles":[]}}