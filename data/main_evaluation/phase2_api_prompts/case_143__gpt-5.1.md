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
{"case_id":"case_143","model_name":"gpt-5.1","phase1_output":{"case_id":"case_143","fault_layer":"unknown","causal_explanation":"The oracle reports a red-light violation without collision or stuck, while dataset labels additionally flag lane invasion. Ego travels some distance (velocity up to ~8.9 m/s) under nonzero throttle, but the recorded vehicle_cmd topic contains zeros for steering, acceleration, braking, and target_speed throughout the run, creating an unexplained mismatch between commanded and actual motion. Traffic light states are available and include red phases, but the relation between the ego route and any specific light, as well as whether a stop line was crossed during red, is not confirmed by the summaries. The lane-invasion label is disputed (dataset=1, error_json=0), so it cannot be treated as confirmed. Consequently, the failure is characterized primarily as an oracle red-light violation with uncertain internal cause and uncertain lane behavior.","root_cause_pattern":"Conservative preservation pattern: a red-light violation is reported by the oracle while the ego vehicle is moving in an environment with active traffic light states, but available evidence does not confirm route–light association, stop-line crossing geometry, lane-boundary crossing, or the responsible Autoware layer; vehicle command logs also show all-zero values despite observed ego motion, leaving controller behavior uncertain.","preservation_constraints":["The generated candidate should reproduce a red-light violation reported by the same oracle mechanism (error_json red=true, no crash, no stuck).","Traffic light topic messages with varying states, including at least one red phase, should be present before the violation.","The ego vehicle should exhibit nonzero velocity at some point during the run, indicating motion in the presence of traffic lights.","Available planning outputs (final_waypoints) and perception summaries (detection_objects, prediction_objects) should exist in the critical window, even if not directly implicated.","The relation between the ego route and any specific traffic light, as well as explicit stop-line crossing and lane-boundary crossing, should remain unconfirmed in the high-level summaries."],"uncertainty":["Dataset.xlsx labels indicate lane_invasion=1 and group=L+R, while error.json reports lane_invasion=false and group=R only; lane invasion is not confirmed.","The oracle confirms a red-light violation but does not provide geometric evidence of stop-line crossing or which traffic light, if any, governed the ego route.","The vehicle_cmd topic shows all-zero commands, yet vehicle_status indicates nonzero velocity and throttle at times; the cause of this mismatch and the behavior of the controller layer are unclear.","No direct module-level evidence explains why the red-light violation occurred (e.g., whether due to sensing, perception, planning, or actuation).","The exact spatial relation between ego pose, traffic lights, and any lane boundaries is not specified in the summaries."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["For any generated candidate labeled as same-root-cause, verify that error_json again reports a red-light violation (red=true) without collision or stuck, regardless of dataset label discrepancies.","Check that traffic_lights topic data exist with at least one red phase before the oracle-detected violation, but that high-level analysis still cannot unequivocally link ego route to a specific light or confirm stop-line crossing.","Confirm that ego achieves nonzero velocity at some time, using vehicle_status or odometry, so that the violation occurs under motion rather than a static mislabel.","Do not require lane_invasion to be present or confirmed; lane invasion should not be used as a matching criterion due to dataset vs. oracle conflict.","Do not infer the responsible Autoware module solely from presence of topics or the vehicle_cmd/vehicle_status mismatch; module-level attribution should remain unknown unless additional evidence is available."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":19,"rain":43,"puddle":36,"wind":22,"fog":41,"wetness":71,"angle":148,"altitude":56},"actors":[],"puddles":[]}}