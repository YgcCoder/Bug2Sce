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
{"case_id":"case_027","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_027","fault_layer":"unknown","causal_explanation":"The oracle consistently labels this as a stuck failure. In the critical last 60-second window of the stuck event, ego has zero velocity and near-zero total displacement, all vehicle commands are zero, but vehicle status reports constant non-zero applied brake. Planning continues to output 101 unblocked final waypoints, but no available evidence directly confirms which module caused the failure.","root_cause_pattern":"Conservative pattern: Ego becomes stuck with zero velocity and near-zero displacement while planning still outputs unblocked final waypoints, with a mismatch between all-zero vehicle commands and non-zero applied brake reported in vehicle status.","preservation_constraints":["Preserve the stuck failure oracle label","Ego has zero velocity and near-zero displacement in the final 60 seconds before failure","Planning outputs unblocked final waypoints throughout the stuck window","All vehicle commands are zero during the critical stuck window","Vehicle status reports non-zero applied brake during the critical stuck window"],"uncertainty":["Module-level attribution between planning, actuation, map, and simulator is unknown","Mismatch between zero brake command and non-zero applied brake is not explained by available evidence","The 11.95m total movement over 60s with 0.014m net displacement is not interpreted in provided evidence"],"ready_for_phase2_generation":"yes","notes_for_validator":["Verify the stuck symptom is correctly reported by the oracle for generated cases","Check that the command-brake mismatch is preserved in generated test cases","Confirm that unblocked final waypoints are present during the stuck period"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":46.14997863769531,"y":326.9700012207031,"z":0.29999998211860657,"pitch":0.0,"yaw":179.999755859375,"roll":0.0},"destination":{"x":60.10997772216797,"y":330.4599914550781,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":95,"rain":2,"puddle":6,"wind":15,"fog":2,"wetness":14,"angle":196,"altitude":58},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":25.844,"y":326.231,"z":1.5,"pitch":0.0,"yaw":326.065,"roll":0.0}}],"puddles":[{"index":0,"level":0.53,"location":{"x":52.31,"y":331.0,"z":0.0},"size":{"x":500.0,"y":300.0,"z":1000.0}}]}}