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
{"case_id":"case_118","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_118","fault_layer":"unknown","causal_explanation":["The oracle confirms a collision at 66.41s and error.json reports a red-light violation. Critical-window evidence shows ego was accelerating (throttle 0.41, speed 5.07 m/s) immediately before collision, with detected o..."],"root_cause_pattern":"Conservative preservation pattern: ego accelerates toward a collision while detected objects are present, final waypoints are available but not marked blocked, and vehicle_cmd remains zero despite active vehicle_status control, with unresolved red-light and lane-invasion label conflicts.","preservation_constraints":["The generated candidate should preserve the collision oracle symptom.","Detected objects (1-3 count) should be present in the critical window before collision.","Final waypoints should be available and not marked as blocked before the collision.","Ego should exhibit non-zero velocity and throttle in vehicle_status before collision.","Post-execution validation should check for vehicle_cmd vs vehicle_status mismatch and label consistency.","Red-light violation label should be preserved, though route-light relation remains unconfirmed."],"uncertainty":["Dataset labels lane_invasion=1 but error.json reports lane_invasion=0; lane-boundary crossing not confirmed by evidence.","Red-light violation reported by error.json, but route-light relation and stop-line crossing are not confirmed by summaries.","vehicle_cmd is all zero while vehicle_status shows throttle and steering; controller behavior is uncertain and fault_layer cannot be attributed to actuation from this mismatch a...","Evidence shows detected and predicted objects, final waypoints, but does not directly prove which module (perception, planning, or actuation) failed to prevent the collision.","Closest object distance in final_waypoints is 0.0, which may indicate missing data rather than actual proximity."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Do not count a generated case as same-root-cause unless post-execution evidence preserves: collision symptom, detected objects in critical window, final wayp...","Manually review dataset vs error.json label conflict for lane_invasion before finalizing root-cause attribution.","Check whether red-light violation can be confirmed by route-light relation and stop-line crossing in post-execution validation.","Verify that vehicle_cmd all-zero with active vehicle_status control is reproducible; if not, re-assess fault_layer."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":104.8687973022461,"y":59.99010467529297,"z":0.29999998211860657,"pitch":0.0,"yaw":0.0,"roll":0.0},"destination":{"x":392.4700012207031,"y":105.38999938964844,"z":0.29999998211860657,"yaw":90.00004577636719}},"weather":{"cloud":12,"rain":24,"puddle":39,"wind":17,"fog":46,"wetness":45,"angle":269,"altitude":38},"actors":[],"puddles":[{"index":0,"level":0.16,"location":{"x":130.218,"y":66.75,"z":0.0},"size":{"x":500.0,"y":500.0,"z":1000.0}},{"index":1,"level":0.93,"location":{"x":122.54,"y":39.454,"z":0.0},"size":{"x":300.0,"y":300.0,"z":1000.0}},{"index":2,"level":0.41,"location":{"x":113.367,"y":66.085,"z":0.0},"size":{"x":500.0,"y":500.0,"z":1000.0}}]}}