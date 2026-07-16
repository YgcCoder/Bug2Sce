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
- Keep every string short. Do not write explanatory paragraphs.
- Each validation/uncertainty array must contain at most 3 short strings.
- Use plain ASCII quotes and valid JSON syntax only.
- Do not include trailing commas, comments, markdown, or extra keys.

Return JSON schema:
{
  "case_id": "case_XXX",
  "candidate_specs": [
    {
      "candidate_id": "cand_001",
      "high_level_variant": "under 20 words",
      "mutation_intent": "under 30 words",
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
      "pre_execution_validation_rules": ["under 18 words"],
      "post_execution_validation_rules": ["under 18 words"],
      "uncertainty": ["under 18 words"]
    }
  ]
}

Input JSON:
{"case_id":"case_037","model_name":"gemini-2.5-pro","phase1_output":{"case_id":"case_037","fault_layer":"unknown","causal_explanation":["The ego vehicle moves, violates a red light, and collides while receiving zero-value vehicle commands, indicating a disconnect between planning and vehicle state."],"root_cause_pattern":"A mismatch between zero-value vehicle_cmd and non-zero vehicle_status precedes an oracle-reported failure.","preservation_constraints":["Preserve the red light violation oracle event.","Preserve the vehicle_cmd vs. vehicle_status mismatch.","A collision event is published by the simulator."],"uncertainty":["Dataset.xlsx reports collision and lane invasion, but error.json does not.","The root cause of the vehicle_cmd/vehicle_status mismatch is unknown.","Route-to-traffic-light relationship is not confirmed."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Major conflict between dataset (C+L+R) and error.json (R).","Key issue: vehicle_cmd is all zeros but vehicle moves.","Collision topic exists, but error.json reports no crash."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"pitch":0.0,"yaw":-9.1552734375e-05,"roll":0.0},"destination":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"yaw":-89.99993896484375}},"weather":{"cloud":76,"rain":93,"puddle":42,"wind":54,"fog":4,"wetness":81,"angle":178,"altitude":16},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":15.22,"spawn":{"x":280.971,"y":331.0,"z":1.5,"pitch":0.0,"yaw":216.15,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":0.53,"spawn":{"x":286.686,"y":331.0,"z":1.5,"pitch":0.0,"yaw":31.215,"roll":0.0}}],"puddles":[]}}