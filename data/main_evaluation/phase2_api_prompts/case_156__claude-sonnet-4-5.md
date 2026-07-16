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
{"case_id":"case_156","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_156","fault_layer":"unknown","causal_explanation":["The oracle confirms a stuck failure lasting 237.15 seconds. In the last 60-second window, ego displacement is 0.01m despite 11.834m cumulative movement distance, and final velocity is 0.0. Both vehicle_cmd (all zero)..."],"root_cause_pattern":"Conservative preservation pattern: ego becomes stuck with zero velocity and zero actuation commands despite available final waypoints, while module-level attribution remains unknown.","preservation_constraints":["The generated candidate should preserve the stuck oracle symptom with near-zero final velocity and displacement over an extended window.","Final waypoints should be present and non-empty during the stuck period.","Vehicle commands (accel, brake, steer) should remain at or near zero during the stuck window.","Post-execution validation should check last-window velocity, displacement, and final-waypoint availability."],"uncertainty":["The evidence does not directly localize the failure to perception, planning, or actuation.","Detection and prediction objects are present (avg 1.995 and 8.895 respectively), but their correctness or relevance to the stuck condition is not confirmed.","It is unclear whether planning failed to generate valid commands, actuation failed to execute them, or another module caused the stoppage."],"ready_for_phase2_generation":"yes","notes_for_validator":["Do not count a generated case as same-root-cause unless post-execution evidence shows extended stuck behavior with zero actuation and available final waypoints.","Verify that the stuck symptom persists for a significant duration (e.g., >30 seconds) with near-zero displacement.","Check that final waypoints remain present and non-empty during the stuck period.","Do not assume planning or actuation fault without additional evidence; the conservative pattern is symptom-based."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"pitch":0.0,"yaw":-9.1552734375e-05,"roll":0.0},"destination":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"yaw":-89.99993896484375}},"weather":{"cloud":48,"rain":15,"puddle":18,"wind":74,"fog":2,"wetness":7,"angle":77,"altitude":32},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":310.173,"y":331.0,"z":1.5,"pitch":0.0,"yaw":47.632,"roll":0.0}}],"puddles":[{"index":0,"level":0.57,"location":{"x":334.767,"y":331.0,"z":0.0},"size":{"x":300.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.46,"location":{"x":328.24,"y":331.0,"z":0.0},"size":{"x":300.0,"y":300.0,"z":1000.0}},{"index":2,"level":0.21,"location":{"x":297.744,"y":331.0,"z":0.0},"size":{"x":350.0,"y":350.0,"z":1000.0}}]}}