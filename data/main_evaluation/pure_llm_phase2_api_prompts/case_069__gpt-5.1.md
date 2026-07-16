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
{"case_id":"case_069","model_name":"gpt-5.1","fault_label":{"collision":1,"stuck":0,"lane_invasion":1,"red_light":0,"group":"C+L"},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":86.0,"y":145.0,"z":0.29999998211860657,"pitch":0.0,"yaw":90.0,"roll":0.0},"destination":{"x":182.91,"y":198.76,"z":0.29999998211860657,"yaw":179.999755859375}},"weather":{"cloud":98,"rain":5,"puddle":8,"wind":25,"fog":12,"wetness":10,"angle":47,"altitude":76},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":8.76,"spawn":{"x":67.271,"y":159.74,"z":1.5,"pitch":0.0,"yaw":100.714,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":12.56,"spawn":{"x":67.068,"y":165.818,"z":1.5,"pitch":0.0,"yaw":275.254,"roll":0.0}}],"puddles":[]},"baseline_input_limitation":"No root-cause pattern, no critical-window trace evidence, no preservation constraints."}