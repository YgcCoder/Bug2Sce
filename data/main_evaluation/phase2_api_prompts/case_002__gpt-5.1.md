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
{"case_id":"case_002","model_name":"gpt-5.1","phase1_output":{"case_id":"case_002","fault_layer":"unknown","causal_explanation":"The oracle reports a red-light violation while traffic-light messages and final waypoints are available, but the summary explicitly states that the relation between the ego route and any red light, as well as whether a stop line was crossed, is unknown. Ego motion is effectively zero throughout the run, and vehicle_cmd is always zero despite non-zero ego velocity early on, leaving controller behavior and the precise mechanism of the violation uncertain.","root_cause_pattern":"Conservative preservation pattern: a red-light violation is flagged by the oracle in a scenario where traffic-light states and a continuous planned route (final_waypoints) are available, but route–light association, stop-line crossing, and module-level responsibility remain unknown.","preservation_constraints":["The generated candidate should preserve the same oracle symptom: a red-light violation is reported by error.json.","Traffic-light messages should be available during the critical window with multiple light states observed over time.","A sequence of final_waypoints should be available up to (or near) the failure time with non-null content.","The route–light relation and stop-line crossing should remain unconfirmed or ambiguous in the available summaries.","Ego odometry and/or current_pose should indicate little or no net displacement over the scenario."],"uncertainty":["The exact traffic light relevant to the violation and its geometric relation to the ego route are not confirmed.","Stop-line crossing is explicitly marked as unknown in the summary.","Vehicle_cmd is all zeros while vehicle_status shows non-zero velocity at some times, so controller behavior and responsibility are unclear.","Module-level attribution among perception, planning, actuation, or simulator cannot be determined from the summaries alone."],"ready_for_phase2_generation":"yes","notes_for_validator":["Confirm that error.json for the generated candidate still reports a red-light violation without additional primary symptoms (collision, lane invasion, stuck, speeding) unless explicitly intended.","Check that /carla/traffic_lights remains available and that multiple traffic-light states (e.g., including red) appear in the sampled window.","Verify that /final_waypoints are present, non-null, and cover the period up to just before the violation time.","Confirm that post-execution summaries do not explicitly resolve route_light_relation_confirmed or stop_line_crossing_confirmed to a definite true/false; the relationship should remain unknown or ambiguous.","Inspect odometry/current_pose to ensure the ego vehicle shows little or no overall displacement, preserving the low-movement characteristic of this case.","Do not attribute the cause to a specific module unless additional evidence beyond these summaries clearly supports that attribution."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"pitch":0.0,"yaw":-9.1552734375e-05,"roll":0.0},"destination":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"yaw":-89.99993896484375}},"weather":{"cloud":80,"rain":64,"puddle":90,"wind":69,"fog":23,"wetness":99,"angle":289,"altitude":36},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":286.887,"y":327.035,"z":1.5,"pitch":0.0,"yaw":12.1,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":24.0,"spawn":{"x":306.513,"y":331.0,"z":1.5,"pitch":0.0,"yaw":309.044,"roll":0.0}}],"puddles":[]}}