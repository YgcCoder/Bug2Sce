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
{"case_id":"case_040","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_040","fault_layer":"unknown","causal_explanation":["The oracle confirms a red-light violation. Critical-window evidence shows traffic light states are available (states 0, 1, 2 observed), final waypoints exist with stop_line_id=4294967295, and vehicle_cmd is all zero w..."],"root_cause_pattern":"Conservative preservation pattern: ego encounters traffic lights while traveling on a route, and a red-light violation occurs, but module-level attribution (perception of light state, planning stop decision, or actuation enforcement) remains unknown.","preservation_constraints":["The generated candidate should preserve the red-light violation oracle symptom.","Traffic lights should be present in the environment near the ego route.","Final waypoints should be available before the failure.","Post-execution validation should check critical-window ego velocity, traffic light states, and final-waypoint stop_line_id values."],"uncertainty":["Route-light relation is not confirmed by the current summaries.","Stop-line crossing is not confirmed by the current summaries.","vehicle_cmd is all zero but vehicle_status shows movement; controller behavior is uncertain.","The evidence does not directly localize the failure to perception (light state detection), planning (stop decision), or actuation (command enforcement)."],"ready_for_phase2_generation":"yes","notes_for_validator":["Do not count a generated case as same-root-cause unless post-execution evidence preserves the red-light violation oracle symptom and traffic lights near the...","Check critical-window ego velocity and traffic light states to confirm the violation pattern.","Verify final-waypoint stop_line_id values; invalid IDs may indicate planning or map issues.","The mismatch between vehicle_cmd (all zero) and vehicle_status (movement) should be investigated but does not alone confirm actuation fault."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":110.0,"y":129.0,"z":1.0,"pitch":0.0,"yaw":180.0,"roll":0.0},"destination":{"x":113.0,"y":130.0,"z":0.0,"yaw":0.0}},"weather":{"cloud":81,"rain":83,"puddle":56,"wind":45,"fog":34,"wetness":86,"angle":169,"altitude":26},"actors":[{"index":0,"type":"walker","nav_type":"immobile","speed":0.0,"spawn":{"x":93.381,"y":131.014,"z":1.5,"pitch":0.0,"yaw":250.045,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":15.87,"spawn":{"x":109.979,"y":140.165,"z":1.5,"pitch":0.0,"yaw":178.512,"roll":0.0}}],"puddles":[]}}