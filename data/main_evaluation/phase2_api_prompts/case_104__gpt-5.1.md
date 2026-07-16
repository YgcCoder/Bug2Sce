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
{"case_id":"case_104","model_name":"gpt-5.1","phase1_output":{"case_id":"case_104","fault_layer":"unknown","causal_explanation":"The dataset labels this case as a red-light violation, but the error.json oracle reports only a goal-related failure with no red event. Traffic light states (red/yellow/green) are available, yet the current summaries do not confirm any route-light relation or stop-line crossing. Ego motion is essentially zero throughout (very small maximum velocity and no effective displacement), while final_waypoints are continuously available and vehicle_cmd remains all zeros. This evidence indicates that the ego barely moves and does not provide direct proof of a red-light violation or a specific Autoware module malfunction.","root_cause_pattern":"Conservative preservation pattern: a low-motion scenario where the ego remains near its start pose with essentially zero commanded motion despite available route and traffic-light information, under an oracle symptom labeled as red-light violation only in the dataset and not confirmed by the runtime oracle.","preservation_constraints":["The generated candidate should preserve the same type of oracle symptom at the dataset level (red_light) while allowing that runtime oracle logs may show no red event.","Traffic light state information should be available on the /carla/traffic_lights topic with multiple states (e.g., 0,1,2) observed during the run.","The ego vehicle should remain near its start position with very small net displacement between initial and final odometry/current_pose samples.","Final waypoints should be available throughout the critical window with a stable waypoint count and no blocked flag in sampled rows.","Vehicle command messages should be present with target speed and longitudinal commands sampled near zero over the run."],"uncertainty":["Dataset.xlsx marks a red-light violation while error.json reports no red event, so the presence of an actual violation is not confirmed.","Route-light relation and stop-line crossing are explicitly reported as unknown; whether the ego ever reaches a stop line is unclear.","Vehicle_cmd is all zeros while vehicle_status shows a small nonzero maximum velocity; controller and actuation behavior cannot be reliably inferred from this mismatch.","The mechanism by which the dataset or oracle determines red-light violations is not visible in the provided evidence, preventing module-level attribution.","Object and prediction topics exist but contain only generic or unknown labels, so interactions with specific traffic infrastructure or rules cannot be analyzed."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Do not assume a true red-light violation occurred; treat red_light as a dataset-level label that may not align with runtime oracle events.","Before claiming same-root-cause, verify that the reproduced case has a similar mismatch pattern: dataset or external label indicates red-light group while error_json (or equivalent runtime oracle) does not log a red event.","Check that traffic light states are being published with multiple distinct values and that the ego remains near its start pose with very limited motion.","Confirm that final_waypoints are available with stable counts during the critical window and that vehicle_cmd target_speed remains near zero.","Do not attribute the cause to perception, planning, or actuation modules unless additional evidence beyond these summaries becomes available."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"pitch":0.0,"yaw":-89.99993896484375,"roll":0.0},"destination":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":63,"rain":10,"puddle":2,"wind":18,"fog":82,"wetness":50,"angle":315,"altitude":3},"actors":[],"puddles":[{"index":0,"level":0.64,"location":{"x":314.031,"y":100.78,"z":0.0},"size":{"x":500.0,"y":700.0,"z":1000.0}}]}}