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
{"case_id":"case_147","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_147","fault_layer":"unknown","causal_explanation":["The oracle confirms a collision at 47.125s. Critical-window evidence shows ego moving at 3.45 m/s before impact, with detected objects (last count: 2) and predicted objects (last count: 12) present. Final waypoints we..."],"root_cause_pattern":"Conservative preservation pattern: ego encounters nearby detected and predicted objects while moving on a planned route before a collision, with vehicle_cmd all-zero despite vehicle_status showing actuation, and module-level attribution remains unknown.","preservation_constraints":["The generated candidate should preserve the collision oracle symptom.","Detected and predicted objects should be present near the ego route before the collision.","Ego should be moving (velocity > 3 m/s) in the final seconds before impact.","Final waypoints should be available and not blocked before the collision.","Post-execution validation should check critical-window ego speed, object detection/prediction counts, and vehicle_cmd vs vehicle_status consistency."],"uncertainty":["Dataset.xlsx labels lane_invasion=1 but error.json reports lane_invasion=0; oracle inconsistency requires manual review.","vehicle_cmd is all-zero while vehicle_status shows throttle and steering activity; controller behavior is uncertain.","The provided evidence does not directly localize the failure to perception, planning, or actuation.","Closest object distance is 3.128m at collision window start, but causal relationship to collision is not directly proven."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Do not count a generated case as same-root-cause unless post-execution evidence preserves: (1) collision oracle, (2) detected and predicted objects near ego...","Manual review is required to resolve the lane_invasion oracle conflict before confirming Phase 2 readiness.","Investigate vehicle_cmd all-zero vs vehicle_status actuation mismatch in post-execution validation.","Check whether the closest object at 3.128m is the collision actor or a separate entity."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":46.14997863769531,"y":326.9700012207031,"z":0.29999998211860657,"pitch":0.0,"yaw":179.999755859375,"roll":0.0},"destination":{"x":60.10997772216797,"y":330.4599914550781,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":69,"rain":0,"puddle":19,"wind":17,"fog":70,"wetness":26,"angle":92,"altitude":2},"actors":[{"index":0,"type":"walker","nav_type":"linear","speed":2.84,"spawn":{"x":61.23,"y":331.0,"z":1.5,"pitch":0.0,"yaw":303.518,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":1.53,"spawn":{"x":39.117,"y":331.0,"z":1.5,"pitch":0.0,"yaw":5.655,"roll":0.0}}],"puddles":[]}}