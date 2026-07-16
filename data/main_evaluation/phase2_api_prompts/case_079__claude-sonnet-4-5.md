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
{"case_id":"case_079","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_079","fault_layer":"unknown","causal_explanation":["Dataset.xlsx labels this case as lane_invasion=1 and red_light=1 (group L+R), but error.json reports only red_light=1 (group R). Critical-window evidence shows traffic lights exist with states 0 and 2, but route-light..."],"root_cause_pattern":"Conservative preservation pattern: ego approaches a traffic-light-controlled intersection with available traffic light states (red present), while vehicle_cmd remains zero and vehicle_status shows movement; module-level attribution and lane-invasion confirmation remain uncertain.","preservation_constraints":["The generated candidate should preserve the red_light oracle symptom from error.json.","Traffic light states (including red) should be present near the ego route before the failure.","Vehicle_cmd should remain zero or near-zero while vehicle_status shows non-zero velocity or throttle.","Post-execution validation should check traffic light state, vehicle_cmd vs. vehicle_status mismatch, and final waypoint stop_line_id validity."],"uncertainty":["Dataset.xlsx labels lane_invasion=1, but error.json does not confirm it; lane-boundary crossing evidence is absent.","Route-light relation and stop-line crossing are not confirmed by the summaries.","Vehicle_cmd is all zero while vehicle_status shows movement and throttle; controller behavior or simulator actuation is uncertain.","Final waypoint stop_line_id is 4294967295 (invalid), so stop-line planning cannot be verified.","The evidence does not directly localize the failure to perception, planning, or actuation."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Do not count a generated case as same-root-cause unless post-execution evidence preserves the red_light oracle symptom and the vehicle_cmd vs. vehicle_status...","Manual review is needed to resolve the lane_invasion label conflict before confirming root cause.","Check whether the vehicle_cmd zero / vehicle_status movement mismatch is a simulator artifact or a controller fault.","Verify traffic light state and route-light relation in the generated scenario before oracle validation."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":59,"rain":63,"puddle":75,"wind":24,"fog":32,"wetness":57,"angle":227,"altitude":22},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":318.806,"y":120.233,"z":1.5,"pitch":0.0,"yaw":77.296,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":0.63,"spawn":{"x":304.093,"y":135.488,"z":1.5,"pitch":0.0,"yaw":262.763,"roll":0.0}}],"puddles":[]}}