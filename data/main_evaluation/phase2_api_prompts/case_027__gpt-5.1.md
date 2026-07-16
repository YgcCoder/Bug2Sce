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
{"case_id":"case_027","model_name":"gpt-5.1","phase1_output":{"case_id":"case_027","fault_layer":"unknown","causal_explanation":"The oracle marks the ego as stuck for over 240 seconds. In the last 60 seconds, ego velocity is zero while odometry shows essentially no net displacement, yet ego_movement_distance over the same window is non-zero, suggesting small back-and-forth or oscillatory motion that does not produce meaningful progress toward the goal. During this period, final_waypoints are consistently available and vehicle_cmd target speed and accel_cmd remain at zero, while vehicle_status reports a constant non-zero brake value. This indicates the system remains in a persistently stopped state despite having a planned path, but the evidence does not clearly localize whether this behavior originates in planning, control, or simulator dynamics.","root_cause_pattern":"Conservative preservation pattern: with valid sensing and continuously available final waypoints, ego spends an extended period with near-zero net displacement while vehicle_cmd target speed and acceleration commands stay at zero and braking remains applied, leading to a stuck outcome without clear module-level attribution.","preservation_constraints":["The generated case should reproduce a stuck outcome with near-zero net displacement over a long duration despite an active mission.","Final waypoints should remain present with stable waypoint counts during the critical stuck window.","During the critical window, vehicle_cmd target_speed and accel_cmd should remain at or near zero.","During the critical window, vehicle_status should indicate zero velocity.","Sensing topics (camera and lidar) and basic pose/odometry should remain available throughout the run."],"uncertainty":["The mechanism that keeps target_speed and accel_cmd at zero is not observable; attribution between planning, control, and higher-level logic is unknown.","The cause of the non-zero ego_movement_distance with near-zero displacement (possible oscillations or localization noise) is unclear.","The influence of nearby actors or traffic lights on the stuck behavior cannot be determined from the provided summaries."],"ready_for_phase2_generation":"yes","notes_for_validator":["Confirm that the generated case is labeled stuck by the oracle with a comparable stuck duration to the original.","Verify that in the critical stuck window, odometry and vehicle_status show near-zero ego velocity and negligible net displacement.","Check that final_waypoints remain continuously available with a stable, non-zero waypoint count and no blocked flags in the stuck window.","Ensure that vehicle_cmd target_speed and accel_cmd remain at or near zero during the stuck window, despite the continued availability of final_waypoints.","Do not attempt to validate specific internal planning or control faults; treat the root cause as a behavioral pattern where the system remains stationary with an available path and zero motion commands."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":46.14997863769531,"y":326.9700012207031,"z":0.29999998211860657,"pitch":0.0,"yaw":179.999755859375,"roll":0.0},"destination":{"x":60.10997772216797,"y":330.4599914550781,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":95,"rain":2,"puddle":6,"wind":15,"fog":2,"wetness":14,"angle":196,"altitude":58},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":25.844,"y":326.231,"z":1.5,"pitch":0.0,"yaw":326.065,"roll":0.0}}],"puddles":[{"index":0,"level":0.53,"location":{"x":52.31,"y":331.0,"z":0.0},"size":{"x":500.0,"y":300.0,"z":1000.0}}]}}