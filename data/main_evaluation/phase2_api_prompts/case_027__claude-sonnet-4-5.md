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
{"case_id":"case_027","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_027","fault_layer":"unknown","causal_explanation":["The oracle confirms a stuck failure lasting 244.3 seconds. In the last 60 seconds, ego traveled 11.955 m but ended with near-zero displacement (0.014 m), zero velocity, and zero vehicle_cmd (accel, brake, steer all 0...."],"root_cause_pattern":"Conservative preservation pattern: ego becomes stuck with available final waypoints, zero vehicle_cmd output, nonzero vehicle_status brake, and minimal net displacement despite small cumulative movement, while module-level attribution remains unknown.","preservation_constraints":["The generated candidate should preserve the stuck oracle symptom with similar duration characteristics.","Final waypoints should be continuously available during the stuck period.","Vehicle_cmd should remain at or near zero (accel, brake, steer) during the stuck window.","Vehicle_status should show nonzero brake and zero velocity in the stuck window.","Post-execution validation should check last-60-second movement distance, displacement, velocity stats, and vehicle_cmd vs. vehicle_status mismatch."],"uncertainty":["The evidence does not localize the failure to planning, actuation, or simulator.","The mismatch between zero vehicle_cmd and nonzero vehicle_status brake suggests a possible controller or simulator issue, but direct module-level evidence is absent.","The small movement distance (11.955 m) with near-zero displacement (0.014 m) may indicate oscillation or drift, but the mechanism is not confirmed."],"ready_for_phase2_generation":"yes","notes_for_validator":["Do not count a generated case as same-root-cause unless post-execution evidence preserves the stuck symptom, final waypoints availability, vehicle_cmd near-z...","Check last-60-second movement distance and displacement to confirm minimal net movement.","The vehicle_cmd vs. vehicle_status mismatch should be preserved in the generated candidate."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":46.14997863769531,"y":326.9700012207031,"z":0.29999998211860657,"pitch":0.0,"yaw":179.999755859375,"roll":0.0},"destination":{"x":60.10997772216797,"y":330.4599914550781,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":95,"rain":2,"puddle":6,"wind":15,"fog":2,"wetness":14,"angle":196,"altitude":58},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":25.844,"y":326.231,"z":1.5,"pitch":0.0,"yaw":326.065,"roll":0.0}}],"puddles":[{"index":0,"level":0.53,"location":{"x":52.31,"y":331.0,"z":0.0},"size":{"x":500.0,"y":300.0,"z":1000.0}}]}}