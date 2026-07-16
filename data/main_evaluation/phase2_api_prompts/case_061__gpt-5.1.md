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
{"case_id":"case_061","model_name":"gpt-5.1","phase1_output":{"case_id":"case_061","fault_layer":"unknown","causal_explanation":"A collision occurs around 46.611s while the ego is moving at about 5 m/s with nonzero throttle in vehicle_status and no braking, yet all vehicle_cmd fields remain zero throughout the critical window. Perception and prediction topics report at least one object before impact and planning continuously provides 101 unblocked final waypoints with closest_object_distance reported as 0.0 at the nearest pre-collision row. The evidence confirms a crash and a red-light oracle event, but does not show route–signal association, lane-boundary geometry, or internal decision logic, so the precise module-level cause of the collision and red-light violation remains uncertain.","root_cause_pattern":"Conservative preservation pattern: ego vehicle is under motion (nonzero velocity and throttle in vehicle_status) and collides with another actor while a red-light violation is reported and planning, perception, and prediction topics are populated, but actuation commands in vehicle_cmd remain zero and there is no clear evidence of braking or a blocked path before impact.","preservation_constraints":["The generated case should preserve the oracle symptom of a collision before scenario end.","The ego vehicle should have nonzero velocity in the last seconds before collision, with no clear deceleration trend within the critical window.","Perception and prediction object topics should be available with at least one object reported before the collision.","Planning final_waypoints should be available and non-null up to the collision, without blocked flags in the nearest pre-collision row.","A red-light violation event should be reported by the oracle or equivalent error-tracking mechanism.","vehicle_cmd should show zero (or effectively null) accel, brake, steer, and target speed commands throughout the critical window while vehicle_status indicates motion."],"uncertainty":["Dataset.xlsx marks lane_invasion=1 while error.json reports lane_invasion=false, so lane invasion is not confirmed.","The exact timing and spatial relation between the ego route, traffic lights, and any stop line are not confirmed; the mechanism of the red-light violation is unknown.","The other collision actor is only identified by ID in the collision oracle; its type, exact trajectory, and relation to ego waypoints are not detailed.","The reason vehicle_cmd remains all zeros despite ego motion is unclear; this may reflect logging configuration, controller behavior, or another integration issue rather than a pure actuation fault.","The internal behavior of perception, prediction, and planning modules (e.g., whether they correctly assessed risk or planned to stop) cannot be determined from the summaries."],"ready_for_phase2_generation":"yes","notes_for_validator":["Verify that the generated case reproduces a collision and a red-light violation according to the same oracle/error_json mechanism used in this case.","Check that vehicle_status shows nonzero velocity in the last seconds before collision and that there is no significant speed decrease indicative of strong braking within the critical window.","Confirm that vehicle_cmd reports all-zero accel, brake, steer, and target speed commands during the critical window while ego is moving, matching the pattern in this case.","Ensure perception and prediction object topics contain at least one object in the pre-collision window and that planning final_waypoints are present, non-null, and not flagged as blocked up to the collision.","Do not require lane_invasion as a necessary symptom for same-root-cause, because lane invasion is disputed between Dataset.xlsx and error_json and should remain uncertain.","Because route–signal relation is unknown, treat any successful reproduction of a red-light oracle event plus collision under similar module/topic availability as satisfying the preserved root-cause pattern."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"pitch":0.0,"yaw":-9.1552734375e-05,"roll":0.0},"destination":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"yaw":-89.99993896484375}},"weather":{"cloud":22,"rain":1,"puddle":72,"wind":86,"fog":3,"wetness":33,"angle":47,"altitude":40},"actors":[{"index":0,"type":"walker","nav_type":"linear","speed":2.52,"spawn":{"x":307.106,"y":326.717,"z":1.5,"pitch":0.0,"yaw":273.916,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":1.91,"spawn":{"x":312.164,"y":331.0,"z":1.5,"pitch":0.0,"yaw":340.961,"roll":0.0}}],"puddles":[]}}