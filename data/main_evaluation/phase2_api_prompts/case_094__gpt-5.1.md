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
{"case_id":"case_094","model_name":"gpt-5.1","phase1_output":{"case_id":"case_094","fault_layer":"unknown","causal_explanation":"The oracle confirms a collision around 98.6s while ego is moving at about 5 m/s with nonzero throttle and zero brake in the last 5 seconds. An external actor is present within tens of meters before impact, perception and prediction topics show at least one tracked object, and planning provides stable, unblocked final waypoints. However, the control command topic contains only zero commands throughout the run, while vehicle_status reports varying throttle, steering, and speed, indicating a mismatch between Autoware command outputs and the executed motion. The available evidence does not localize the cause of the eventual collision to a specific Autoware layer; the apparent controller–status inconsistency could stem from actuation, simulator, or logging behavior.","root_cause_pattern":"Conservative preservation pattern: ego is in motion along a planned route with valid final waypoints and at least one nearby actor present before a collision, while the actuator command topic remains effectively zeroed throughout the run and vehicle_status shows nonzero motion and control, leaving the true module-level cause of the collision unknown.","preservation_constraints":["The generated case should reproduce an oracle-reported collision event during ego motion.","At least one non-ego actor should be present within a moderate distance of the ego before the collision, as indicated by simulator or perception topics.","Planning should publish valid final waypoints (nonempty, unblocked) up to shortly before the collision.","The actuator command topic (vehicle_cmd or equivalent) should remain at or near zero for accel, brake, and steering across the critical window.","Vehicle status or odometry should indicate that the ego actually moves with nonzero speed and control variation before the collision."],"uncertainty":["Dataset.xlsx labels indicate stuck and lane_invasion, but error.json only reports collision; the true presence of stuck or lane invasion is uncertain.","The mismatch between zero vehicle_cmd and varying vehicle_status may be due to simulator behavior, logging configuration, or an actuation/controller issue; the root module is not identifiable from the evidence.","The mechanism by which ego and the nearby actor come into contact (who yields, right-of-way, exact geometry) is not specified in the summaries."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Check that the generated case produces an oracle collision event similar in timing (near the end of the run) and that ego is moving with nonzero speed shortly before impact.","Verify that planning publishes stable, non-blocked final waypoints up to the critical window before the collision.","Confirm that actuator command topics remain effectively zero (no significant accel, brake, or steering commands) while vehicle_status or odometry still shows ego motion and control variation.","Ensure at least one non-ego actor is present within a moderate distance of ego before collision and is represented in either simulator objects or perception/prediction topics.","Do not require stuck or lane_invasion symptoms as correctness criteria due to label conflicts; they may or may not appear in valid same-root-cause reproductions."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":46.14997863769531,"y":326.9700012207031,"z":0.29999998211860657,"pitch":0.0,"yaw":179.999755859375,"roll":0.0},"destination":{"x":60.10997772216797,"y":330.4599914550781,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":18,"rain":0,"puddle":5,"wind":4,"fog":2,"wetness":5,"angle":147,"altitude":86},"actors":[{"index":0,"type":"walker","nav_type":"linear","speed":0.47,"spawn":{"x":34.621,"y":323.083,"z":1.5,"pitch":0.0,"yaw":5.957,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":2.97,"spawn":{"x":47.075,"y":306.825,"z":1.5,"pitch":0.0,"yaw":122.545,"roll":0.0}}],"puddles":[{"index":0,"level":0.23,"location":{"x":40.714,"y":317.459,"z":0.0},"size":{"x":650.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.07,"location":{"x":59.924,"y":321.923,"z":0.0},"size":{"x":400.0,"y":400.0,"z":1000.0}}]}}