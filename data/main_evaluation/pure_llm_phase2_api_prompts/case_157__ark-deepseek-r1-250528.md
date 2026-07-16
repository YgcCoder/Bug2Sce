You are the Pure-LLM baseline scenario generator for an Autoware DriveFuzz experiment.
Task: generate one high-level candidate scenario spec from only the seed scenario summary and failure label.

Important baseline rule:
- Do not use root-cause patterns, critical-window evidence, trace evidence, or preservation constraints.
- You only know the seed scenario and the DriveFuzz symptom label.
- Generate candidate specs only; local rule-based code will concretize them into DriveFuzz-style JSON.

Formatting and safety rules:
- Return exactly one JSON object. Do not use markdown fences.
- Generate exactly 1 candidate_specs item.
- Do not invent new oracle labels beyond the provided fault label.
- Keep actor position offsets within [-8, 8] meters on x/y.
- Keep actor speed_delta within [-3, 3].
- Keep mission spawn/destination offsets within [-5, 5] meters, or set keep_original=true.
- Keep weather deltas conservative: each weather_delta should be within [-20, 20].
- Keep puddle level_delta within [-0.2, 0.2] and size_scale within [0.8, 1.2].
- Keep every string short. Do not write explanatory paragraphs.
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
{"case_id":"case_157","model_name":"ark-deepseek-r1-250528","fault_label":{"collision":1,"stuck":0,"lane_invasion":0,"red_light":0,"group":"C"},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":61,"rain":47,"puddle":40,"wind":72,"fog":45,"wetness":45,"angle":219,"altitude":40},"actors":[{"index":0,"type":"walker","nav_type":"linear","speed":3.18,"spawn":{"x":354.436,"y":124.582,"z":1.5,"pitch":0.0,"yaw":94.79,"roll":0.0}},{"index":1,"type":"walker","nav_type":"autopilot","speed":1.54,"spawn":{"x":321.791,"y":141.759,"z":1.5,"pitch":0.0,"yaw":4.735,"roll":0.0}},{"index":2,"type":"vehicle","nav_type":"autopilot","speed":9.39,"spawn":{"x":354.221,"y":129.106,"z":1.5,"pitch":0.0,"yaw":275.69,"roll":0.0}},{"index":3,"type":"vehicle","nav_type":"autopilot","speed":6.64,"spawn":{"x":303.289,"y":126.562,"z":1.5,"pitch":0.0,"yaw":130.751,"roll":0.0}}],"puddles":[]},"baseline_input_limitation":"No root-cause pattern, no critical-window trace evidence, no preservation constraints."}