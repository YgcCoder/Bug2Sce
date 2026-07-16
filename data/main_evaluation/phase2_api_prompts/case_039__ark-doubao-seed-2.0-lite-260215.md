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
{"case_id":"case_039","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_039","fault_layer":"unknown","causal_explanation":"Dataset labels this case as stuck and lane invasion, but error.json does not detect either failure. All published vehicle_cmd commands are zero in the critical window, but the ego vehicle exhibits non-zero velocity and movement. No module-level failure can be confirmed due to label conflict and unproven mismatch cause.","root_cause_pattern":"Conservative candidate pattern: Ego vehicle maintains non-zero movement and velocity when all published actuation commands are zero, with conflicting failure annotations between the dataset and error.json.","preservation_constraints":["Preserve conflicting stuck and lane invasion labels between dataset and error.json","Preserve all-zero accel, brake, and steer commands in vehicle_cmd during the critical window","Preserve non-zero ego velocity and movement during the critical window","Preserve consistent availability of final waypoints throughout the critical window","Preserve 1 actor and 3 puddle regions on the Town01 map"],"uncertainty":["Dataset and error.json have conflicting labels: dataset labels stuck=1, lane_invasion=1; error.json labels both 0","Mismatch between zero vehicle_cmd and non-zero ego movement has no confirmed module-level cause per available evidence","No direct evidence of lane boundary crossing to confirm lane invasion is present"],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Resolve conflicting failure labels via manual review before confirming generated cases match this root cause","Verify the mismatch between zero vehicle_cmd and non-zero ego movement in all generated candidate cases"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":46.14997863769531,"y":326.9700012207031,"z":0.29999998211860657,"pitch":0.0,"yaw":179.999755859375,"roll":0.0},"destination":{"x":60.10997772216797,"y":330.4599914550781,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":18,"rain":3,"puddle":0,"wind":9,"fog":0,"wetness":2,"angle":23,"altitude":84},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":59.223,"y":331.0,"z":1.5,"pitch":0.0,"yaw":18.019,"roll":0.0}}],"puddles":[{"index":0,"level":0.71,"location":{"x":37.563,"y":312.431,"z":0.0},"size":{"x":650.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.73,"location":{"x":50.849,"y":319.366,"z":0.0},"size":{"x":250.0,"y":250.0,"z":1000.0}},{"index":2,"level":0.16,"location":{"x":74.893,"y":331.0,"z":0.0},"size":{"x":650.0,"y":650.0,"z":1000.0}}]}}