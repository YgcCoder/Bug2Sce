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
{"case_id":"case_002","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_002","fault_layer":"unknown","causal_explanation":["The oracle confirms a red-light violation. Critical-window evidence shows traffic light states transitioning from all-green (state 0) to mixed states including red (state 2), and final waypoints with stop_line_id=4294..."],"root_cause_pattern":"Conservative preservation pattern: ego approaches an intersection with traffic lights transitioning to red while final waypoints lack valid stop-line association, and the vehicle continues moving despite zero vehicle commands.","preservation_constraints":["The generated candidate should preserve the red-light violation oracle symptom.","Traffic lights should transition to red state near the ego route before the violation.","Final waypoints should show invalid or missing stop-line IDs during the critical window.","Post-execution validation should check traffic light states, final waypoint stop-line IDs, and ego velocity profile near the intersection."],"uncertainty":["Route-light relation and stop-line crossing are not confirmed by evidence.","Vehicle_cmd is all zero but vehicle_status shows movement; controller behavior is uncertain.","The evidence does not localize the failure to perception (traffic light detection), planning (stop decision), or actuation (command execution).","No direct evidence of which traffic light ID is relevant to the ego route."],"ready_for_phase2_generation":"yes","notes_for_validator":["Do not count a generated case as same-root-cause unless post-execution evidence shows: (1) red-light violation oracle, (2) traffic light state transition to...","Verify that the relevant traffic light ID and stop-line crossing are captured in post-execution logs if available.","Check whether vehicle_cmd vs. vehicle_status mismatch persists; if so, investigate simulator or actuation layer separately."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"pitch":0.0,"yaw":-9.1552734375e-05,"roll":0.0},"destination":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"yaw":-89.99993896484375}},"weather":{"cloud":80,"rain":64,"puddle":90,"wind":69,"fog":23,"wetness":99,"angle":289,"altitude":36},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":286.887,"y":327.035,"z":1.5,"pitch":0.0,"yaw":12.1,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":24.0,"spawn":{"x":306.513,"y":331.0,"z":1.5,"pitch":0.0,"yaw":309.044,"roll":0.0}}],"puddles":[]}}