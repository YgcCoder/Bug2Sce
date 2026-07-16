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
{"case_id":"case_067","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_067","fault_layer":"unknown","causal_explanation":["Dataset.xlsx labels this case as S+L+R (stuck, lane_invasion, red_light), but error.json reports only a red-light violation. The last 60-second window shows ego traveled 271.9 m with mean velocity 4.03 m/s, contradict..."],"root_cause_pattern":"Conservative preservation pattern: ego exhibits zero vehicle_cmd output while vehicle_status shows active throttle and steering, leading to uncontrolled movement and a red-light violation, with module-level attribution uncertain due to conflicting oracle labels and lack of direct failure evidence.","preservation_constraints":["Generated candidate should preserve the red-light violation oracle symptom.","vehicle_cmd should remain zero or near-zero while vehicle_status shows non-zero throttle and steering.","Final waypoints should be available during the critical window.","Post-execution validation should confirm vehicle_cmd vs. vehicle_status mismatch and red-light violation."],"uncertainty":["Dataset.xlsx labels stuck=1 and lane_invasion=1, but error.json reports stuck=0 and lane_invasion=0; last-60s movement (271.9 m, mean 4.03 m/s) contradicts stuck.","vehicle_cmd is all zero, but vehicle_status shows throttle and steering; controller or actuation layer behavior is uncertain.","Route-light relation and stop-line crossing are not confirmed by evidence.","Lane invasion is not supported by lane-boundary crossing evidence.","No direct evidence localizes the failure to perception, planning, or actuation modules."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Manual review is required to resolve the dataset vs. error.json conflict before using this case for generation.","Do not count a generated case as same-root-cause unless post-execution confirms vehicle_cmd vs. vehicle_status mismatch and red-light violation.","Check whether the vehicle_cmd=0 / vehicle_status≠0 mismatch is a simulator artifact or an Autoware actuation failure.","Verify route-light relation and stop-line crossing in any generated candidate before claiming red-light violation preservation."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":3,"rain":23,"puddle":46,"wind":93,"fog":27,"wetness":36,"angle":347,"altitude":44},"actors":[],"puddles":[]}}