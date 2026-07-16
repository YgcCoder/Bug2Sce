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
{"case_id":"case_169","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_169","fault_layer":"unknown","causal_explanation":["The oracle confirms a red-light violation. Critical-window evidence shows traffic light states are available (36 lights with states 0, 1, 2), final waypoints exist with stop_line_id=4294967295, and vehicle_cmd is all..."],"root_cause_pattern":"Conservative preservation pattern: ego violates a red light while final waypoints and traffic light states are available, but module-level attribution and stop-line crossing remain unconfirmed.","preservation_constraints":["The generated candidate should preserve the red-light violation oracle symptom.","Traffic light states and final waypoints should be available in the critical window.","Post-execution validation should check that ego velocity is non-zero near a red light and that the red-light violation is reproduced.","Stop-line ID 4294967295 (invalid) suggests waypoint-light association may be missing or incorrect."],"uncertainty":["Route-light relation is not confirmed by the current summaries.","Stop-line crossing is not confirmed by the current summaries.","vehicle_cmd is all zero but vehicle_status shows movement; controller behavior is uncertain.","The evidence does not directly localize the failure to perception, planning, or actuation."],"ready_for_phase2_generation":"yes","notes_for_validator":["Do not count a generated case as same-root-cause unless post-execution evidence preserves the red-light violation and non-zero ego velocity near a red light.","Check that traffic light states and final waypoints are available in the critical window.","Verify that stop-line crossing or route-light relation is confirmed in the generated case if possible.","The vehicle_cmd/vehicle_status mismatch suggests possible actuation or simulator issues, but this is not confirmed as the root cause."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":334.21539306640625,"y":145.67129516601562,"z":1.5,"pitch":0.0,"yaw":90.00005340576172,"roll":0.0},"destination":{"x":338.97998046875,"y":301.2599792480469,"z":1.5,"yaw":90.00005340576172}},"weather":{"cloud":73,"rain":14,"puddle":19,"wind":4,"fog":93,"wetness":23,"angle":272,"altitude":17},"actors":[],"puddles":[]}}