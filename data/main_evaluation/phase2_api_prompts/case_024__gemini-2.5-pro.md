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
{"case_id":"case_024","model_name":"gemini-2.5-pro","phase1_output":{"case_id":"case_024","fault_layer":"planning","causal_explanation":["The ego vehicle did not plan to stop for a red light, causing a red-light violation and a collision with an actor in the intersection."],"root_cause_pattern":"Planner fails to generate a stopping trajectory for a red light on the ego's route.","preservation_constraints":["Preserve red light violation and collision.","An actor is present in the intersection.","A traffic light on the ego's path is red."],"uncertainty":["Route-light relation is not directly confirmed.","Controller behavior is uncertain due to zero vehicle_cmd."],"ready_for_phase2_generation":"yes","notes_for_validator":["Key evidence: final_waypoints lack a stop plan.","The red light violation and collision are linked.","Controller uncertainty is a known platform issue."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":86.0,"y":145.0,"z":0.29999998211860657,"pitch":0.0,"yaw":90.0,"roll":0.0},"destination":{"x":182.91,"y":198.76,"z":0.29999998211860657,"yaw":179.999755859375}},"weather":{"cloud":100,"rain":8,"puddle":10,"wind":22,"fog":0,"wetness":3,"angle":26,"altitude":85},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":7.03,"spawn":{"x":104.973,"y":144.182,"z":1.5,"pitch":0.0,"yaw":108.846,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":3.01,"spawn":{"x":91.918,"y":129.675,"z":1.5,"pitch":0.0,"yaw":89.829,"roll":0.0}}],"puddles":[{"index":0,"level":0.54,"location":{"x":94.397,"y":120.413,"z":0.0},"size":{"x":350.0,"y":300.0,"z":1000.0}}]}}