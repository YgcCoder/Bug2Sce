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
{"case_id":"case_156","model_name":"gpt-5.1","phase1_output":{"case_id":"case_156","fault_layer":"unknown","causal_explanation":"The oracle reports a stuck outcome over ~237 seconds. Throughout the run the ego remains essentially stationary, with odometry and current_pose showing only centimeter-level displacement. In the final 60 seconds, ego velocity is zero and both vehicle_cmd and vehicle_status controls (throttle, brake, steer) stay at zero while planning continues to publish a full set of final_waypoints. This indicates that the system reaches a state where it has a valid route but no longitudinal or steering commands are issued to move the vehicle, though the evidence does not show why upstream modules choose (or are forced) to keep target speed and actuator commands at zero.","root_cause_pattern":"Conservative preservation pattern: ego starts from rest, receives continuous final_waypoints and perception/prediction/object topics, but remains effectively stationary for an extended duration while vehicle_cmd target speed and actuator-related commands stay at zero.","preservation_constraints":["The oracle should report a stuck outcome (no collision, no lane invasion, no red-light violation).","Ego odometry and pose should show only negligible displacement over the full scenario duration, especially in the final window.","Planning/final_waypoints should remain available with a stable, non-empty set of waypoints during the stuck period.","vehicle_cmd should be present with target_speed and accel/brake/steer commands effectively zero in the critical stuck window.","Sensing (image_raw and points_raw) and basic perception/prediction topics should remain available during the stuck period."],"uncertainty":["The evidence does not reveal why target_speed and actuator commands remain zero (e.g., whether due to planning, safety logic, or controller constraints).","No direct internal state or cost-function information is available from planning or control modules.","The relation between nearby actors, traffic lights, or map features and the decision to keep the ego stopped is not observable from the provided summaries."],"ready_for_phase2_generation":"yes","notes_for_validator":["Post-execution, confirm that the oracle again flags the scenario as stuck with no collision, lane invasion, or red-light violation.","Verify via odometry and current_pose that the ego remains within a very small radius of its start position and that velocity stays near zero in the critical window.","Check that final_waypoints remain continuously available with a non-zero, stable count during the period when the ego is stuck.","Check that vehicle_cmd is present and that target_speed and actuator commands (accel, brake, steer) remain effectively zero during the stuck interval.","Do not assign module-level blame in validation; only confirm that the same high-level pattern (planned route plus persistent zero commands and no movement) is reproduced."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"pitch":0.0,"yaw":-9.1552734375e-05,"roll":0.0},"destination":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"yaw":-89.99993896484375}},"weather":{"cloud":48,"rain":15,"puddle":18,"wind":74,"fog":2,"wetness":7,"angle":77,"altitude":32},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":310.173,"y":331.0,"z":1.5,"pitch":0.0,"yaw":47.632,"roll":0.0}}],"puddles":[{"index":0,"level":0.57,"location":{"x":334.767,"y":331.0,"z":0.0},"size":{"x":300.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.46,"location":{"x":328.24,"y":331.0,"z":0.0},"size":{"x":300.0,"y":300.0,"z":1000.0}},{"index":2,"level":0.21,"location":{"x":297.744,"y":331.0,"z":0.0},"size":{"x":350.0,"y":350.0,"z":1000.0}}]}}