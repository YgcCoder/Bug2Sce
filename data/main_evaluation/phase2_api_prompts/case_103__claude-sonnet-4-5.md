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
{"case_id":"case_103","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_103","fault_layer":"unknown","causal_explanation":["The dataset labels a red-light violation and lane invasion (group L+R), while error.json confirms only a red-light violation (group R). Critical-window evidence shows traffic light states exist, final waypoints are av..."],"root_cause_pattern":"Conservative preservation pattern: ego approaches a traffic light with an invalid stop-line ID in final waypoints, vehicle_cmd remains zero while vehicle_status shows movement, and a red-light violation is confirmed by error.json, with dataset also labeling lane invasion (unconfirmed by error.json).","preservation_constraints":["The generated candidate should preserve a red-light violation oracle symptom.","Traffic light states should be available near the ego route before the failure.","Final waypoints should be present with an invalid or missing stop-line ID.","Vehicle_cmd should remain zero or near-zero while vehicle_status shows non-zero velocity or throttle.","Post-execution validation should check critical-window traffic light state, stop-line ID validity, and vehicle_cmd vs. vehicle_status mismatch."],"uncertainty":["Dataset labels lane_invasion=1, but error.json shows lane_invasion=0; lane-boundary crossing is not confirmed.","Route-light relation and stop-line crossing are not confirmed by the current summaries.","Vehicle_cmd is all zero but vehicle_status shows movement; controller behavior is uncertain.","The evidence does not directly localize the failure to perception, planning, or actuation."],"ready_for_phase2_generation":"yes","notes_for_validator":["Do not count a generated case as same-root-cause unless post-execution evidence preserves the red-light violation, invalid stop-line ID, and vehicle_cmd vs....","Manual review is needed to resolve the dataset vs. error.json conflict on lane_invasion.","Check whether the generated case exhibits the same vehicle_cmd=0 and vehicle_status>0 pattern.","Verify that traffic light states and final waypoints are available in the critical window."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":74,"rain":96,"puddle":72,"wind":56,"fog":26,"wetness":69,"angle":135,"altitude":9},"actors":[{"index":0,"type":"vehicle","nav_type":"linear","speed":3.55,"spawn":{"x":331.013,"y":149.095,"z":1.5,"pitch":0.0,"yaw":68.769,"roll":0.0}}],"puddles":[{"index":0,"level":0.26,"location":{"x":339.0,"y":129.159,"z":0.0},"size":{"x":350.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.24,"location":{"x":313.918,"y":140.757,"z":0.0},"size":{"x":800.0,"y":800.0,"z":1000.0}}]}}