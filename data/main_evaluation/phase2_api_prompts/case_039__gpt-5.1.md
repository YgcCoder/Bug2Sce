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
{"case_id":"case_039","model_name":"gpt-5.1","phase1_output":{"case_id":"case_039","fault_layer":"unknown","causal_explanation":"The dataset labels this case as stuck with lane invasion, but the error.json oracle reports only a goal-related failure with no stuck or lane-invasion events. Critical-window data show that the ego moves over 100 m in the last 60 seconds with nonzero velocity and active vehicle_status actuation, while vehicle_cmd remains zero throughout. Planning outputs stable final_waypoints and lane_waypoints_array. Because the oracle does not confirm stuck or lane invasion and the actuation mismatch (nonzero motion with zero vehicle_cmd) cannot be resolved with the given evidence, the underlying root cause and module-level fault remain unknown.","root_cause_pattern":"Conservative preservation pattern: a goal-related failure occurs in a scenario with continuous ego motion, stable final_waypoints, available perception and prediction objects, zeroed vehicle_cmd, and vehicle_status indicating nonzero velocity and displacement, while oracle events for stuck and lane invasion are absent despite dataset labels.","preservation_constraints":["The generated case should reproduce a non-success goal outcome (e.g., significant goal error) without oracle-confirmed collision, stuck, lane-invasion, red-light, or speeding events.","Perception and prediction objects should be published throughout the critical window.","Planning topics (final_waypoints and a lane_waypoints_array-style route) should be present and stable in count during the critical window.","vehicle_cmd should remain effectively zero for acceleration, braking, steering, and target speed during the critical window.","vehicle_status or equivalent feedback should show nonzero ego motion and displacement over the same interval."],"uncertainty":["Dataset.xlsx labels indicate stuck and lane invasion, but error.json reports none; the true oracle symptom is uncertain.","The cause of nonzero ego motion with zero vehicle_cmd is unclear; it could stem from controller behavior, simulator behavior, or logging/bridging artifacts.","No direct evidence links the goal failure to specific perception, planning, control, map, or simulator defects.","Lane invasion is not supported by any lane-boundary crossing evidence despite the dataset label."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Treat dataset stuck and lane-invasion labels as unconfirmed; rely primarily on error_json for oracle symptom verification.","After executing a generated scenario, verify that error_json (or equivalent oracle) still reports a goal-related failure without explicit collision, stuck, lane-invasion, red-light, or speeding events.","Check that vehicle_cmd remains effectively zero while vehicle_status (or equivalent) confirms nonzero ego motion during the critical window.","Confirm that planning topics (final waypoints and route) remain available and non-null up to the failure time.","Do not infer module-level root cause (perception vs. planning vs. actuation vs. simulator) solely from the command-status mismatch; this pattern is only a candidate mechanism."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":46.14997863769531,"y":326.9700012207031,"z":0.29999998211860657,"pitch":0.0,"yaw":179.999755859375,"roll":0.0},"destination":{"x":60.10997772216797,"y":330.4599914550781,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":18,"rain":3,"puddle":0,"wind":9,"fog":0,"wetness":2,"angle":23,"altitude":84},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":59.223,"y":331.0,"z":1.5,"pitch":0.0,"yaw":18.019,"roll":0.0}}],"puddles":[{"index":0,"level":0.71,"location":{"x":37.563,"y":312.431,"z":0.0},"size":{"x":650.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.73,"location":{"x":50.849,"y":319.366,"z":0.0},"size":{"x":250.0,"y":250.0,"z":1000.0}},{"index":2,"level":0.16,"location":{"x":74.893,"y":331.0,"z":0.0},"size":{"x":650.0,"y":650.0,"z":1000.0}}]}}