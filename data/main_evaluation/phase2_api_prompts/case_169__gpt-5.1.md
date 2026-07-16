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
{"case_id":"case_169","model_name":"gpt-5.1","phase1_output":{"case_id":"case_169","fault_layer":"unknown","causal_explanation":"The oracle reports a red-light violation, and traffic-light states are available, but the summaries do not confirm that the ego route intersected a specific red light or that any stop line was crossed at red. The ego shows nonzero velocity at some point during the run, with vehicle_cmd remaining all zeros and throttle/brake/steer reported as zero in vehicle_status, so the detailed control behavior and its relation to the traffic light timing remain uncertain.","root_cause_pattern":"Conservative preservation pattern: a red-light violation is flagged by the oracle while traffic-light state information is present, but the route–light relationship and stop-line crossing are not established, leaving the mechanism of the violation and the responsible module unknown.","preservation_constraints":["The generated candidate should preserve the same oracle symptom: a red-light violation is reported.","Traffic-light state information should be available on the /carla/traffic_lights topic during the run.","The ego vehicle should experience some movement during the scenario (nonzero velocity at some time).","Critical-window evidence should not conclusively establish route–light relation or explicit stop-line crossing at red.","Final waypoints should be available throughout the run, with no null rows reported."],"uncertainty":["Route–traffic-light relation and stop-line crossing are marked as unknown in the summaries.","The precise timing and location of the red-light violation are not provided.","vehicle_cmd remains all zeros while vehicle_status shows nonzero velocity at some point, so the true control pathway (Autoware vs simulator default control) is unclear.","It is unknown whether any internal perception, planning, or control logic explicitly disregarded a red light."],"ready_for_phase2_generation":"yes","notes_for_validator":["After executing a generated candidate, verify that the oracle again reports a red-light violation and no conflicting primary oracle symptoms (collision, stuck, lane invasion).","Confirm that /carla/traffic_lights is present and carries multiple state values, but that the logs do not provide a clear, deterministic mapping from the ego route to a specific red traffic light and its stop line.","Check that final_waypoints remain available and structurally similar (no null rows, stable waypoint count) near the time the oracle flags the violation.","Inspect ego odometry or vehicle_status to ensure the ego has nonzero velocity at some point, indicating actual movement in the scenario.","Do not infer the responsible Autoware module from these preservation conditions alone; keep fault_layer as unknown unless additional, more detailed evidence emerges."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":334.21539306640625,"y":145.67129516601562,"z":1.5,"pitch":0.0,"yaw":90.00005340576172,"roll":0.0},"destination":{"x":338.97998046875,"y":301.2599792480469,"z":1.5,"yaw":90.00005340576172}},"weather":{"cloud":73,"rain":14,"puddle":19,"wind":4,"fog":93,"wetness":23,"angle":272,"altitude":17},"actors":[],"puddles":[]}}