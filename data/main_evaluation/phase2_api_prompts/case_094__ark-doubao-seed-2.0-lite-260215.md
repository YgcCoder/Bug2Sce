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
{"case_id":"case_094","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_094","fault_layer":"unknown","causal_explanation":"Collision is confirmed by both dataset and error.json, but stuck and lane invasion labels conflict between the two sources. All commands in vehicle_cmd are zero in the pre-collision critical window, but vehicle_status reports non-zero throttle and ego movement with no braking. The closest detected object before collision is ~48m from ego, and no blocked waypoints are reported by planning. No direct evidence localizes failure to a specific Autoware module.","root_cause_pattern":"Conservative failure pattern: Ego vehicle experiences a collision when all actuation commands output on vehicle_cmd are zero, while vehicle_status reports non-zero throttle and ongoing ego movement, with conflicting labels for additional failure symptoms.","preservation_constraints":["Preserve the confirmed collision failure symptom","Preserve the mismatch between all-zero vehicle_cmd commands and non-zero throttle/ego movement reported by vehicle_status","Preserve 2 actors and 2 puddle regions on the Town01 map","Preserve the absence of reported blocked waypoints in pre-collision planning data"],"uncertainty":["Conflict between dataset and error.json on stuck and lane invasion labels","No direct evidence to localize root cause to a specific module layer","The vehicle_cmd/vehicle_status mismatch cannot be confirmed as root cause from available evidence"],"ready_for_phase2_generation":"yes","notes_for_validator":["Resolve the label conflict between dataset and error.json before confirming generated case root cause","Verify the mismatch between all-zero vehicle_cmd and non-zero vehicle_status movement in the generated critical window"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":46.14997863769531,"y":326.9700012207031,"z":0.29999998211860657,"pitch":0.0,"yaw":179.999755859375,"roll":0.0},"destination":{"x":60.10997772216797,"y":330.4599914550781,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":18,"rain":0,"puddle":5,"wind":4,"fog":2,"wetness":5,"angle":147,"altitude":86},"actors":[{"index":0,"type":"walker","nav_type":"linear","speed":0.47,"spawn":{"x":34.621,"y":323.083,"z":1.5,"pitch":0.0,"yaw":5.957,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":2.97,"spawn":{"x":47.075,"y":306.825,"z":1.5,"pitch":0.0,"yaw":122.545,"roll":0.0}}],"puddles":[{"index":0,"level":0.23,"location":{"x":40.714,"y":317.459,"z":0.0},"size":{"x":650.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.07,"location":{"x":59.924,"y":321.923,"z":0.0},"size":{"x":400.0,"y":400.0,"z":1000.0}}]}}