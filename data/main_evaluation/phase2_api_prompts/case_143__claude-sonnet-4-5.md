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
{"case_id":"case_143","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_143","fault_layer":"unknown","causal_explanation":["Dataset.xlsx labels this case as lane_invasion=1 and red_light=1 (group L+R), but error.json reports only red_light=1 (group R). The critical-window evidence shows traffic lights exist and changed state (from mixed 0/..."],"root_cause_pattern":"Conservative preservation pattern: ego encounters a red-light scenario (confirmed by error.json) with possible lane-invasion symptom (dataset-only), while vehicle_cmd remains zero and vehicle_status shows movement, and module-level attribution remains unknown.","preservation_constraints":["The generated candidate should preserve the red-light oracle symptom (error.json confirmed).","Traffic light state transitions should be present near the ego route.","Vehicle_cmd should remain zero or near-zero while vehicle_status shows non-zero velocity during the critical window.","Post-execution validation should check for red-light violation and, if dataset label is trusted, lane-invasion symptom."],"uncertainty":["Dataset.xlsx reports lane_invasion=1, but error.json reports lane_invasion=0; manual review needed.","Route-light relation and stop-line crossing are not confirmed by evidence.","Lane-boundary crossing is not confirmed by evidence.","Vehicle_cmd is all zero but vehicle_status shows movement; controller behavior is uncertain.","No direct evidence localizes the failure to perception, planning, or actuation modules."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Manual review is required to resolve the dataset vs. error.json conflict on lane_invasion before treating this case as ground truth.","Do not count a generated case as same-root-cause unless post-execution evidence preserves the red-light violation and the vehicle_cmd-zero/vehicle_status-mov...","If the dataset lane_invasion label is trusted after review, add a lane-boundary crossing check to the validation rules.","The vehicle_cmd/vehicle_status mismatch may indicate a simulator or actuation issue, but current evidence does not support definitive attribution."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":19,"rain":43,"puddle":36,"wind":22,"fog":41,"wetness":71,"angle":148,"altitude":56},"actors":[],"puddles":[]}}