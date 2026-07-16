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
{"case_id":"case_112","model_name":"gemini-2.5-pro","phase1_output":{"case_id":"case_112","fault_layer":"planning","causal_explanation":["The vehicle collides while moving, despite the planning module publishing zero-value motion commands, indicating a control command generation failure."],"root_cause_pattern":"A collision occurs when the planning module outputs null vehicle commands while the vehicle is in motion.","preservation_constraints":["A collision must occur.","Vehicle motion commands must be zero before collision.","Ego vehicle must be in motion before collision."],"uncertainty":["Lane invasion label is disputed between oracles.","The discrepancy between zero vehicle_cmd and actual motion is uncertain (planning vs actuation/simulator)."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["vehicle_cmd is all zeros while vehicle_status shows motion.","Fault could be planning, actuation, or simulator bridge.","Lane invasion label is inconsistent."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":86.0,"y":145.0,"z":0.29999998211860657,"pitch":0.0,"yaw":90.0,"roll":0.0},"destination":{"x":182.91,"y":198.76,"z":0.29999998211860657,"yaw":179.999755859375}},"weather":{"cloud":94,"rain":14,"puddle":7,"wind":28,"fog":31,"wetness":23,"angle":59,"altitude":-16},"actors":[{"index":0,"type":"walker","nav_type":"autopilot","speed":2.32,"spawn":{"x":109.808,"y":152.81,"z":1.5,"pitch":0.0,"yaw":108.29,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":13.06,"spawn":{"x":80.262,"y":164.766,"z":1.5,"pitch":0.0,"yaw":70.365,"roll":0.0}}],"puddles":[]}}