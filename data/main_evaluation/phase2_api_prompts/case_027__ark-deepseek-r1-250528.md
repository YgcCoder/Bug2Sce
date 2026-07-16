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
{"case_id":"case_027","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_027","fault_layer":"unknown","causal_explanation":"This is a confirmed stuck failure consistent between dataset and error.json. In the 60-second critical stuck window, ego has zero velocity and near-zero displacement, vehicle_cmd outputs all zero control commands, and final waypoints remain available from planning. No module-level failure is directly confirmed, and there is an unexplained mismatch between zero brake command and non-zero reported brake in vehicle status.","root_cause_pattern":"Conservative pattern: Ego becomes stuck with zero velocity and near-zero displacement, while vehicle_cmd outputs all zero control commands, planning still provides available final waypoints, and vehicle status reports active non-zero braking.","preservation_constraints":["Preserve the stuck failure symptom","Ego must have near-zero displacement and zero velocity in the critical stuck window","Vehicle_cmd must output all zero acceleration, brake, and steering commands in the critical window","Final waypoints must be consistently available throughout the critical stuck window","One actor must be present in the scenario"],"uncertainty":["Module-level attribution of all-zero vehicle_cmd is not confirmed by available evidence","The mismatch between zero brake command and non-zero reported brake is unexplained","It is unknown why zero commands are issued despite available final waypoints"],"ready_for_phase2_generation":"yes","notes_for_validator":["Check that the generated stuck case preserves the all-zero vehicle_cmd and available final waypoints condition before marking as same-root-cause","Verify near-zero displacement and zero velocity in the critical stuck window of generated cases"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":46.14997863769531,"y":326.9700012207031,"z":0.29999998211860657,"pitch":0.0,"yaw":179.999755859375,"roll":0.0},"destination":{"x":60.10997772216797,"y":330.4599914550781,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":95,"rain":2,"puddle":6,"wind":15,"fog":2,"wetness":14,"angle":196,"altitude":58},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":25.844,"y":326.231,"z":1.5,"pitch":0.0,"yaw":326.065,"roll":0.0}}],"puddles":[{"index":0,"level":0.53,"location":{"x":52.31,"y":331.0,"z":0.0},"size":{"x":500.0,"y":300.0,"z":1000.0}}]}}