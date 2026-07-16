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
{"case_id":"case_147","model_name":"gpt-5.1","phase1_output":{"case_id":"case_147","fault_layer":"unknown","causal_explanation":"A collision is confirmed by the oracle around 47.125 s. In the preceding window the ego has nonzero speed per the collision-window summary, a nearby simulator object (~3.1 m away), active perception/prediction outputs, and a full set of final waypoints marked unblocked with a reported closest_object_distance of 0.0. However, vehicle_cmd target speed, accel, brake, and steer commands remain zero throughout the trace summary, while vehicle_status in the collision window reports nonzero throttle and velocity. This mismatch between command and status, plus incomplete motion data (global odometry shows almost no displacement while collision-window speed is several m/s), prevents a clear module-level attribution. The dataset indicates an additional lane-invasion symptom, but the error.json oracle does not, so lane invasion cannot be treated as confirmed.","root_cause_pattern":"Conservative preservation pattern: a collision occurs while a nearby actor is present and planning/perception topics are populated, but high-level control commands are effectively zero and module-level responsibility (including any lane invasion) remains unknown due to inconsistent motion and oracle information.","preservation_constraints":["The generated candidate should reproduce a collision reported by the collision oracle within a short time window after scenario start.","At least one non-ego actor should be present within a few meters of the ego before the collision, as indicated by a simulator objects topic or closest-actor summary.","Perception and prediction object topics should be available and report at least one object in the critical window before the collision.","Planning final_waypoints should be available with a stable waypoint count and no blocked flag immediately before the collision.","Vehicle_cmd should report near-zero or zero accel, brake, steer, and target speed values in the critical window, while collision-window summaries or status suggest ego motion, preserving the command–status ambiguity."],"uncertainty":["Dataset.xlsx labels a lane invasion but error.json lane_invasion is false, so lane invasion is not confirmed.","Collision-window ego velocity statistics show speeds up to ~3.45 m/s, while trace_summary vehicle_status velocity_range is near zero and odometry shows negligible displacement, creating ambiguity about actual ego motion.","The constant-zero vehicle_cmd signals alongside nonzero throttle/velocity in the collision window make controller and actuation behavior unclear.","No detailed lane-boundary or stop-line information is provided, so path-relative behavior (including lane invasion) cannot be verified.","Module-level failure attribution (perception vs planning vs control vs simulator) is not supported directly by the available evidence."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Treat the lane-invasion label as unconfirmed; do not require lane-boundary crossing when judging same-root-cause cases.","After executing a generated candidate, verify that the collision oracle triggers and that at least one non-ego actor is within a few meters of the ego just before the collision.","Check that perception and prediction topics contain at least one object in the critical window before the collision.","Confirm that final_waypoints remain available, unblocked, and structurally similar (stable size) immediately before collision.","Inspect vehicle_cmd logs to ensure accel, brake, steer, and target speed remain effectively zero in the critical window, while separate status or summary information suggests ego motion or at least a collision event, preserving the command–status ambiguity.","Because of conflicting velocity and lane-invasion information, classify same-root-cause only when the high-level pattern of a collision with nearby actor and ambiguous control commands is preserved, not based on exact numeric speeds or lane events."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":46.14997863769531,"y":326.9700012207031,"z":0.29999998211860657,"pitch":0.0,"yaw":179.999755859375,"roll":0.0},"destination":{"x":60.10997772216797,"y":330.4599914550781,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":69,"rain":0,"puddle":19,"wind":17,"fog":70,"wetness":26,"angle":92,"altitude":2},"actors":[{"index":0,"type":"walker","nav_type":"linear","speed":2.84,"spawn":{"x":61.23,"y":331.0,"z":1.5,"pitch":0.0,"yaw":303.518,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":1.53,"spawn":{"x":39.117,"y":331.0,"z":1.5,"pitch":0.0,"yaw":5.655,"roll":0.0}}],"puddles":[]}}