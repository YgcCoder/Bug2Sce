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
{"case_id":"case_061","model_name":"gemini-2.5-pro","phase1_output":{"case_id":"case_061","fault_layer":"planning","causal_explanation":["The planning module published zero-value vehicle commands, causing the ego to continue moving without control, run a red light, and collide."],"root_cause_pattern":"Planning fails to publish valid control commands, leading to uncontrolled motion and collision.","preservation_constraints":["Preserve zero-value vehicle commands before collision.","Preserve a red light on the ego's route.","Preserve the collision event."],"uncertainty":["Dataset and error.json conflict on lane invasion label.","The specific cause for zero-value vehicle commands is unknown."],"ready_for_phase2_generation":"yes","notes_for_validator":["Key evidence is zero vehicle_cmd vs non-zero vehicle_status.","Ignore the lane invasion conflict for generation."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"pitch":0.0,"yaw":-9.1552734375e-05,"roll":0.0},"destination":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"yaw":-89.99993896484375}},"weather":{"cloud":22,"rain":1,"puddle":72,"wind":86,"fog":3,"wetness":33,"angle":47,"altitude":40},"actors":[{"index":0,"type":"walker","nav_type":"linear","speed":2.52,"spawn":{"x":307.106,"y":326.717,"z":1.5,"pitch":0.0,"yaw":273.916,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":1.91,"spawn":{"x":312.164,"y":331.0,"z":1.5,"pitch":0.0,"yaw":340.961,"roll":0.0}}],"puddles":[]}}