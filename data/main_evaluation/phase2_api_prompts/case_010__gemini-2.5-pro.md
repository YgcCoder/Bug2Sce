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
{"case_id":"case_010","model_name":"gemini-2.5-pro","phase1_output":{"case_id":"case_010","fault_layer":"unknown","causal_explanation":["The dataset labels a lane invasion, but simulator logs and odometry show the vehicle barely moved and reached its goal, indicating a likely labeling or data logging error."],"root_cause_pattern":"A scenario where dataset labels conflict with simulator oracle events and odometry data.","preservation_constraints":["Preserve dataset label vs. oracle event conflict.","Preserve zero-value vehicle commands.","Preserve goal proximity to start."],"uncertainty":["Dataset label (lane invasion) is contradicted by simulator events.","Vehicle velocity data is inconsistent across topics.","The actual vehicle behavior is unclear due to conflicting data."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["The lane invasion label is unconfirmed and contradicted.","The case appears to be a false positive in the dataset.","Resolve data conflict before generating new scenarios."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":110.0,"y":129.0,"z":1.0,"pitch":0.0,"yaw":180.0,"roll":0.0},"destination":{"x":113.0,"y":130.0,"z":0.0,"yaw":0.0}},"weather":{"cloud":83,"rain":57,"puddle":74,"wind":30,"fog":3,"wetness":79,"angle":278,"altitude":7},"actors":[],"puddles":[{"index":0,"level":0.08,"location":{"x":111.012,"y":125.676,"z":0.0},"size":{"x":800.0,"y":700.0,"z":1000.0}},{"index":1,"level":0.57,"location":{"x":131.334,"y":131.335,"z":0.0},"size":{"x":800.0,"y":800.0,"z":1000.0}},{"index":2,"level":0.21,"location":{"x":107.58,"y":139.272,"z":0.0},"size":{"x":650.0,"y":650.0,"z":1000.0}}]}}