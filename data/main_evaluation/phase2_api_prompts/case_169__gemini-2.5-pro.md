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
{"case_id":"case_169","model_name":"gemini-2.5-pro","phase1_output":{"case_id":"case_169","fault_layer":"perception","causal_explanation":["The ego vehicle ran a red light as the planner did not command a stop, likely because the perception module failed to detect the light in heavy fog."],"root_cause_pattern":"Planner proceeds through a red light when the perception module provides no traffic light status.","preservation_constraints":["Preserve the red light violation oracle symptom.","Maintain heavy fog conditions.","Ensure planner does not command a stop for the light."],"uncertainty":["Specific traffic light perception module is unknown.","Route-to-light relationship is not confirmed by evidence.","Vehicle moves despite zero-value vehicle_cmd topic."],"ready_for_phase2_generation":"yes","notes_for_validator":["Absence of a traffic light perception topic is key evidence.","Planner's lack of a stop command is confirmed."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":334.21539306640625,"y":145.67129516601562,"z":1.5,"pitch":0.0,"yaw":90.00005340576172,"roll":0.0},"destination":{"x":338.97998046875,"y":301.2599792480469,"z":1.5,"yaw":90.00005340576172}},"weather":{"cloud":73,"rain":14,"puddle":19,"wind":4,"fog":93,"wetness":23,"angle":272,"altitude":17},"actors":[],"puddles":[]}}