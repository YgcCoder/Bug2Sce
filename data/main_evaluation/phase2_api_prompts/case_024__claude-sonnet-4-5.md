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
{"case_id":"case_024","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_024","fault_layer":"unknown","causal_explanation":["The oracle confirms both collision and red-light violation. Critical-window evidence shows ego was moving (2.2 m/s at collision), braking occurred (vehicle_status brake nonzero), and detected/predicted objects were pr..."],"root_cause_pattern":"Conservative preservation pattern: ego encounters a nearby actor while approaching or at an intersection with traffic lights, resulting in both collision and red-light violation, with module-level attribution uncertain due to zero vehicle_cmd despite vehicle movement.","preservation_constraints":["Generated candidate must preserve both collision and red-light violation oracle symptoms","A nearby actor should be present near ego route before collision","Traffic lights should be present on or near the planned route","Post-execution validation should confirm ego movement, actor proximity, and traffic light interaction in critical window","Validator should check for vehicle_cmd/vehicle_status consistency in generated case"],"uncertainty":["vehicle_cmd is all zero while vehicle_status shows movement and braking, making actuation layer attribution uncertain","route-light relation is not confirmed by evidence","stop-line crossing is not confirmed by evidence","red-light violation timestamp is unknown","cannot determine if planning failed to stop, perception failed to detect lights/actor, or actuation failed to execute commands"],"ready_for_phase2_generation":"yes","notes_for_validator":["Do not count generated case as same-root-cause unless both collision and red-light violation occur in post-execution","Verify actor-route interaction and traffic light presence in critical window","Check vehicle_cmd/vehicle_status consistency in generated case to rule out simulator artifact","Confirm ego movement and braking behavior before collision"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":86.0,"y":145.0,"z":0.29999998211860657,"pitch":0.0,"yaw":90.0,"roll":0.0},"destination":{"x":182.91,"y":198.76,"z":0.29999998211860657,"yaw":179.999755859375}},"weather":{"cloud":100,"rain":8,"puddle":10,"wind":22,"fog":0,"wetness":3,"angle":26,"altitude":85},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":7.03,"spawn":{"x":104.973,"y":144.182,"z":1.5,"pitch":0.0,"yaw":108.846,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":3.01,"spawn":{"x":91.918,"y":129.675,"z":1.5,"pitch":0.0,"yaw":89.829,"roll":0.0}}],"puddles":[{"index":0,"level":0.54,"location":{"x":94.397,"y":120.413,"z":0.0},"size":{"x":350.0,"y":300.0,"z":1000.0}}]}}