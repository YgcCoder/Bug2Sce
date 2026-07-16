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
{"case_id":"case_104","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_104","fault_layer":"unknown","causal_explanation":["Dataset.xlsx labels this case as red_light=1 (group R), but error.json shows red=false and other='goal'. The vehicle remained nearly stationary (velocity max 0.23 m/s, odometry shows minimal movement) with all vehicle..."],"root_cause_pattern":"Conservative preservation pattern: ego remains nearly stationary near mission start with available traffic light state transitions, while dataset and error.json oracles conflict on red-light violation and module-level attribution remains unknown.","preservation_constraints":["The generated candidate should preserve the oracle conflict or require manual review of red-light violation status.","Ego should remain nearly stationary (velocity < 0.5 m/s) near mission start for an extended period.","Traffic light states should be available and transition during the scenario.","Post-execution validation should check ego velocity, position drift, traffic light state availability, and oracle consistency."],"uncertainty":["Dataset.xlsx labels red_light=1, but error.json shows red=false; oracle conflict requires manual review.","No route-light relation or stop-line crossing evidence is provided.","No red-light violation timestamp is confirmed.","Evidence does not directly prove whether perception, planning, or actuation failed, or whether the dataset label is correct.","Vehicle_cmd is all zero and vehicle_status shows minimal movement; controller behavior and mission progress are unclear."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Manual review is required to resolve the dataset vs. error.json oracle conflict before using this case for generation.","Do not count a generated case as same-root-cause unless post-execution evidence preserves near-stationary ego behavior, traffic light state availability, and...","If the dataset label is confirmed correct after manual review, re-analyze with red-light violation as ground truth and update fault_layer and root_cause_patt...","If error.json is confirmed correct, re-classify as a goal-reaching or stuck case rather than red-light violation."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"pitch":0.0,"yaw":-89.99993896484375,"roll":0.0},"destination":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":63,"rain":10,"puddle":2,"wind":18,"fog":82,"wetness":50,"angle":315,"altitude":3},"actors":[],"puddles":[{"index":0,"level":0.64,"location":{"x":314.031,"y":100.78,"z":0.0},"size":{"x":500.0,"y":700.0,"z":1000.0}}]}}