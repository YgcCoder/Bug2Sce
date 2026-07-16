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
{"case_id":"case_037","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_037","fault_layer":"unknown","causal_explanation":"Labels conflict between dataset (marks collision, lane invasion, red light violation) and error.json (only red light violation is confirmed). Vehicle_cmd output is all-zero throughout the trace, but vehicle_status reports non-zero throttle and moving ego in the critical window. No module-level failure is directly confirmed by available evidence, and red light event details are unconfirmed.","root_cause_pattern":"Conservative preservation pattern: Autoware outputs all-zero vehicle actuation commands while the ego vehicle continues moving in heavy rain high-wetness conditions, with conflicting failure labels and an unconfirmed red light event.","preservation_constraints":["Preserve the original Town01 map and mission start/goal positions","Preserve the original heavy rain and high wetness weather conditions","Preserve 2 actors in the scenario","Preserve all-zero vehicle_cmd output observed in the original trace","Preserve the conflicting label status between dataset and error.json"],"uncertainty":["Conflicting labels for collision and lane invasion between dataset and error.json","Route-light relation and stop-line crossing for the red light event are not confirmed","Mismatch between all-zero vehicle_cmd and moving vehicle status cannot confirm actuation fault alone","No module-level failure is directly confirmed by critical-window evidence"],"ready_for_phase2_generation":"yes","notes_for_validator":["Verify all-zero vehicle_cmd output in the generated trace to confirm root cause preservation","Manually check which failures (collision, lane invasion, red light violation) actually occur after execution","Confirm whether the mismatch between all-zero commands and ego movement reproduces in the generated case"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"pitch":0.0,"yaw":-9.1552734375e-05,"roll":0.0},"destination":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"yaw":-89.99993896484375}},"weather":{"cloud":76,"rain":93,"puddle":42,"wind":54,"fog":4,"wetness":81,"angle":178,"altitude":16},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":15.22,"spawn":{"x":280.971,"y":331.0,"z":1.5,"pitch":0.0,"yaw":216.15,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":0.53,"spawn":{"x":286.686,"y":331.0,"z":1.5,"pitch":0.0,"yaw":31.215,"roll":0.0}}],"puddles":[]}}