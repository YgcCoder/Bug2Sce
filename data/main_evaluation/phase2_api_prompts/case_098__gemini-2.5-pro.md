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
{"case_id":"case_098","model_name":"gemini-2.5-pro","phase1_output":{"case_id":"case_098","fault_layer":"unknown","causal_explanation":["The ego vehicle collided with an actor while `vehicle_cmd` was zero, but `vehicle_status` showed movement and the planner did not mark the path as blocked."],"root_cause_pattern":"Preserve collision where `vehicle_cmd` is zero, the vehicle moves, and the planner does not command a stop.","preservation_constraints":["Preserve the collision event.","Preserve zero-value `vehicle_cmd` messages.","Preserve non-zero throttle in `vehicle_status`."],"uncertainty":["The specific module at fault is unclear.","Planner did not block path.","Vehicle moved despite zero-value vehicle_cmd."],"ready_for_phase2_generation":"yes","notes_for_validator":["Key issue: `vehicle_cmd` vs `vehicle_status` mismatch.","Planner also did not mark path as blocked."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"pitch":0.0,"yaw":-89.99993896484375,"roll":0.0},"destination":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":15,"rain":4,"puddle":3,"wind":13,"fog":2,"wetness":1,"angle":268,"altitude":66},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":13.58,"spawn":{"x":339.675,"y":97.818,"z":1.5,"pitch":0.0,"yaw":1.063,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":3.78,"spawn":{"x":339.455,"y":109.061,"z":1.5,"pitch":0.0,"yaw":352.555,"roll":0.0}}],"puddles":[{"index":0,"level":0.05,"location":{"x":336.857,"y":124.696,"z":0.0},"size":{"x":500.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.55,"location":{"x":328.699,"y":118.075,"z":0.0},"size":{"x":300.0,"y":300.0,"z":1000.0}}]}}