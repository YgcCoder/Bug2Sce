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
{"case_id":"case_004","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_004","fault_layer":"unknown","causal_explanation":["The oracle shows a red-light violation (error.json) but the dataset also labels lane_invasion=1, creating a conflict (dataset=L+R, error.json=R). Critical-window evidence confirms traffic light states exist and final..."],"root_cause_pattern":"Conservative preservation pattern: ego approaches a traffic light with available final waypoints and traffic light state data, but exhibits minimal movement with zero vehicle commands, leading to a red-light violation (error.json) while dataset also flags lane invasion (unconfirmed).","preservation_constraints":["The generated candidate should preserve a red-light violation oracle event.","Traffic light state data and final waypoints should be available in the critical window.","Ego should exhibit minimal or near-zero movement in the final window.","Post-execution validation should check for red-light violation, traffic light state availability, and ego velocity profile."],"uncertainty":["Dataset labels lane_invasion=1 but error.json does not confirm it; oracle_consistency=dataset_only with conflict.","Route-light relation and stop-line crossing are not confirmed by evidence.","Vehicle_cmd is all zero but vehicle_status shows non-zero throttle and minimal velocity; controller behavior is uncertain.","The evidence does not directly localize the failure to perception, planning, or actuation.","No actors are configured in the scenario, yet perception reports detected objects; origin and relevance are unclear."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Manual review is required to resolve the dataset vs. error.json conflict before treating this as a confirmed red-light or lane-invasion case.","Do not count a generated case as same-root-cause unless post-execution confirms red-light violation and minimal ego movement.","Check whether the zero vehicle_cmd with non-zero throttle/velocity indicates a simulator artifact or actuation fault.","Verify traffic light state relevance to the ego route and stop-line crossing in post-execution validation."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":24,"rain":7,"puddle":9,"wind":93,"fog":19,"wetness":29,"angle":105,"altitude":71},"actors":[],"puddles":[{"index":0,"level":0.09,"location":{"x":350.843,"y":129.224,"z":0.0},"size":{"x":650.0,"y":500.0,"z":1000.0}}]}}