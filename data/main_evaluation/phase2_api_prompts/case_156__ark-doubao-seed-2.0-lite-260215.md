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
{"case_id":"case_156","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_156","fault_layer":"unknown","causal_explanation":"The oracle consistently labels this case as a stuck failure. Ego has zero velocity and near-zero displacement over the last 60 seconds, all actuation commands and vehicle control status values are zero, but planning continuously publishes 101 non-empty final waypoints. No collision or red light event is detected.","root_cause_pattern":"Conservative pattern: Ego becomes fully stuck with all-zero actuation commands despite continuous availability of non-empty planned final waypoints, with no triggering collision or red light event.","preservation_constraints":["Preserve the stuck failure oracle symptom","Preserve continuous presence of non-empty final waypoints during the stuck window","Preserve all-zero actuation commands in vehicle_cmd during the stuck window","No collision or red light event occurs prior to the stuck state"],"uncertainty":["No available evidence explains why zero actuation commands are generated despite available final waypoints","Module-level failure attribution cannot be confirmed from the provided summarized evidence"],"ready_for_phase2_generation":"yes","notes_for_validator":["Verify that the generated test case maintains non-empty final waypoints during the stuck window and has no collision or red light trigger to confirm it matches the root cause class"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"pitch":0.0,"yaw":-9.1552734375e-05,"roll":0.0},"destination":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"yaw":-89.99993896484375}},"weather":{"cloud":48,"rain":15,"puddle":18,"wind":74,"fog":2,"wetness":7,"angle":77,"altitude":32},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":310.173,"y":331.0,"z":1.5,"pitch":0.0,"yaw":47.632,"roll":0.0}}],"puddles":[{"index":0,"level":0.57,"location":{"x":334.767,"y":331.0,"z":0.0},"size":{"x":300.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.46,"location":{"x":328.24,"y":331.0,"z":0.0},"size":{"x":300.0,"y":300.0,"z":1000.0}},{"index":2,"level":0.21,"location":{"x":297.744,"y":331.0,"z":0.0},"size":{"x":350.0,"y":350.0,"z":1000.0}}]}}