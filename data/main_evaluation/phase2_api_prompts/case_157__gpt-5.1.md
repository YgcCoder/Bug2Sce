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
{"case_id":"case_157","model_name":"gpt-5.1","phase1_output":{"case_id":"case_157","fault_layer":"unknown","causal_explanation":"A collision is reported at 20.38s while the ego is moving at about 4.7 m/s with nonzero throttle and zero brake. Perception and prediction topics report at least one object throughout the window, and planning publishes a full set of final waypoints with no blocked flags; the closest-object distance in the waypoint summary is recorded as 0.0 with 0.0 velocity despite the oracle reporting a nearby actor at 3.486 m. The control command topic shows all-zero accel/brake/steer/target speed while the low-level vehicle status indicates the ego is actually moving under throttle, so the interaction between planning outputs, control commands, and the vehicle’s motion is unclear. Available evidence confirms that the ego continues forward into another actor without braking, but it does not isolate whether the root cause lies in perception, prediction, planning, actuation, or the simulator interface.","root_cause_pattern":"Conservative preservation pattern: the ego vehicle is in motion and approaches a nearby actor before a collision, with object and prediction topics active and unblocked final waypoints available, while there is no braking and the vehicle_cmd stream remains all zero despite continued ego motion.","preservation_constraints":["The generated scenario should preserve a collision between the ego vehicle and another actor as reported by the oracle collision topic.","The ego should be moving (nonzero velocity in vehicle_status or odometry) in the seconds leading up to the collision, with no significant braking behavior recorded.","Perception and prediction object topics should be present and report at least one nearby actor before the collision.","Planning final_waypoints should be available with a full set of waypoints and no blocked flags in the critical window before the collision.","The vehicle_cmd topic should remain with zero accel, brake, steer, and target speed ranges while vehicle_status shows nonzero velocity in the same window."],"uncertainty":["Module-level attribution is unclear because perception detects objects, prediction produces trajectories, planning publishes unblocked waypoints, yet vehicle_cmd is all zero while vehicle_status shows motion.","The discrepancy between closest_object_distance=0.0 in final_waypoints summary and 3.486 m distance in oracle objects is not explained by the evidence.","The data does not reveal whether the collision resulted from perception mislocalization, planning decisions, controller behavior, or simulator/vehicle interface issues."],"ready_for_phase2_generation":"yes","notes_for_validator":["Verify that the oracle collision topic in the generated case confirms a collision between ego and at least one non-ego actor near the end of the run.","Check that ego velocity from vehicle_status or odometry is nonzero and does not significantly decrease due to braking within several seconds before the collision.","Confirm that detection and prediction object topics are populated and show at least one actor near ego in the critical window.","Ensure final_waypoints are present with a consistent waypoint count and no blocked flags before the collision event.","Confirm that vehicle_cmd accel_cmd, brake_cmd, steer_cmd, and target_speed remain effectively zero while vehicle_status indicates ego motion, reproducing the command–status mismatch pattern."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":61,"rain":47,"puddle":40,"wind":72,"fog":45,"wetness":45,"angle":219,"altitude":40},"actors":[{"index":0,"type":"walker","nav_type":"linear","speed":3.18,"spawn":{"x":354.436,"y":124.582,"z":1.5,"pitch":0.0,"yaw":94.79,"roll":0.0}},{"index":1,"type":"walker","nav_type":"autopilot","speed":1.54,"spawn":{"x":321.791,"y":141.759,"z":1.5,"pitch":0.0,"yaw":4.735,"roll":0.0}},{"index":2,"type":"vehicle","nav_type":"autopilot","speed":9.39,"spawn":{"x":354.221,"y":129.106,"z":1.5,"pitch":0.0,"yaw":275.69,"roll":0.0}},{"index":3,"type":"vehicle","nav_type":"autopilot","speed":6.64,"spawn":{"x":303.289,"y":126.562,"z":1.5,"pitch":0.0,"yaw":130.751,"roll":0.0}}],"puddles":[]}}