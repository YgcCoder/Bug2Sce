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
{"case_id":"case_029","model_name":"gemini-2.5-pro","phase1_output":{"case_id":"case_029","fault_layer":"planning","causal_explanation":["The ego vehicle ran a red light because the planner did not generate a stopping trajectory, possibly due to failing to associate the red light with its route."],"root_cause_pattern":"Planner does not command a stop for a relevant red light on the route.","preservation_constraints":["Preserve the red light violation oracle symptom.","Ego route intersects with a red traffic light.","Planner does not associate a stop line with the route."],"uncertainty":["Dataset.xlsx and error.json disagree on lane invasion.","Root cause of planning failure is unknown (perception vs. map vs. planner logic).","vehicle_cmd is all zero while vehicle is moving."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Resolve conflict between dataset (L+R) and error.json (R) labels.","The label conflict makes this case uncertain for generation.","Investigate why planner did not associate stop line with route."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"pitch":0.0,"yaw":-89.99993896484375,"roll":0.0},"destination":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":100,"rain":1,"puddle":8,"wind":6,"fog":12,"wetness":13,"angle":91,"altitude":81},"actors":[{"index":0,"type":"walker","nav_type":"linear","speed":2.78,"spawn":{"x":343.807,"y":136.276,"z":1.5,"pitch":0.0,"yaw":29.582,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":1.67,"spawn":{"x":340.651,"y":106.21,"z":1.5,"pitch":0.0,"yaw":267.899,"roll":0.0}}],"puddles":[]}}