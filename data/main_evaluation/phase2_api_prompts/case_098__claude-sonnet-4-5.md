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
{"case_id":"case_098","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_098","fault_layer":"unknown","causal_explanation":["The oracle confirms a collision at 29.09s with actor 5275. Critical-window evidence shows ego moving at ~4.8 m/s before collision, with detected and predicted objects present (last count: 1 detected, 11 predicted). Ho..."],"root_cause_pattern":"Conservative preservation pattern: ego encounters a nearby actor (classification 6, distance ~4m) on or near the planned route before a collision, while vehicle_cmd remains zero despite vehicle_status showing active throttle and steering. Module-level attribution remains unknown.","preservation_constraints":["The generated candidate should preserve the collision oracle symptom.","A nearby actor should be present near the ego route before the failure (distance <10m).","Ego should be moving (velocity >3 m/s) in the critical window before collision.","Final waypoints should be available and not blocked before the collision.","Post-execution validation should check critical-window ego speed, actor proximity, and vehicle_cmd/vehicle_status consistency."],"uncertainty":["vehicle_cmd is all zero while vehicle_status shows nonzero throttle and steering; the cause of this mismatch is unclear.","The evidence does not directly localize the failure to perception, planning, or actuation.","Closest object info shows actor 5275 at 4.048m distance, but it is unclear whether planning or control failed to respond.","No evidence of braking or stopping attempts in vehicle_status or vehicle_cmd."],"ready_for_phase2_generation":"yes","notes_for_validator":["Do not count a generated case as same-root-cause unless post-execution evidence preserves the actor-route interaction, ego moving before collision, and colli...","Check vehicle_cmd vs vehicle_status consistency in the generated case.","Verify that final waypoints are available and not blocked before the collision.","Confirm that ego speed is >3 m/s and actor distance is <10m in the critical window."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"pitch":0.0,"yaw":-89.99993896484375,"roll":0.0},"destination":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":15,"rain":4,"puddle":3,"wind":13,"fog":2,"wetness":1,"angle":268,"altitude":66},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":13.58,"spawn":{"x":339.675,"y":97.818,"z":1.5,"pitch":0.0,"yaw":1.063,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":3.78,"spawn":{"x":339.455,"y":109.061,"z":1.5,"pitch":0.0,"yaw":352.555,"roll":0.0}}],"puddles":[{"index":0,"level":0.05,"location":{"x":336.857,"y":124.696,"z":0.0},"size":{"x":500.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.55,"location":{"x":328.699,"y":118.075,"z":0.0},"size":{"x":300.0,"y":300.0,"z":1000.0}}]}}