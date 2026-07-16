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
{"case_id":"case_157","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_157","fault_layer":"unknown","causal_explanation":["The oracle confirms a collision at 20.381s with actor 10283. Critical-window evidence shows ego was moving at 4.7 m/s before collision, with 1-3 detected objects and 1-23 predicted objects. Final waypoints were availa..."],"root_cause_pattern":"Conservative preservation pattern: ego encounters a nearby actor (classification 6, distance ~3.5m) on or near the planned route and collides while moving at moderate speed, with detection and prediction active but vehicle_cmd logging all-zero values despite vehicle_status showing actuation.","preservation_constraints":["The generated candidate should preserve a collision oracle event.","A nearby actor should be present within a few meters of ego before the collision.","Ego should be moving at moderate speed (3-5 m/s) in the final seconds before collision.","Detection and prediction topics should report at least one object in the critical window.","Final waypoints should be available and not blocked.","Post-execution validation should check for collision, ego speed, actor proximity, and object detection presence."],"uncertainty":["vehicle_cmd reports all-zero commands while vehicle_status shows throttle and steering activity; the cause of this mismatch is unknown.","The evidence does not directly prove whether perception failed to classify the actor correctly, planning failed to generate avoidance commands, or the controller failed to issue...","No evidence of braking or deceleration before collision, but cannot confirm if this is a planning, control, or logging issue."],"ready_for_phase2_generation":"yes","notes_for_validator":["Do not count a generated case as same-root-cause unless post-execution evidence shows a collision with a nearby actor present in the critical window.","Check that ego speed is moderate (3-5 m/s) before collision and that detection/prediction report at least one object.","The vehicle_cmd all-zero anomaly may or may not reproduce; focus validation on the collision symptom and actor-ego interaction.","If vehicle_cmd remains all-zero in the generated case, investigate whether this is a simulator, controller, or logging issue."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":61,"rain":47,"puddle":40,"wind":72,"fog":45,"wetness":45,"angle":219,"altitude":40},"actors":[{"index":0,"type":"walker","nav_type":"linear","speed":3.18,"spawn":{"x":354.436,"y":124.582,"z":1.5,"pitch":0.0,"yaw":94.79,"roll":0.0}},{"index":1,"type":"walker","nav_type":"autopilot","speed":1.54,"spawn":{"x":321.791,"y":141.759,"z":1.5,"pitch":0.0,"yaw":4.735,"roll":0.0}},{"index":2,"type":"vehicle","nav_type":"autopilot","speed":9.39,"spawn":{"x":354.221,"y":129.106,"z":1.5,"pitch":0.0,"yaw":275.69,"roll":0.0}},{"index":3,"type":"vehicle","nav_type":"autopilot","speed":6.64,"spawn":{"x":303.289,"y":126.562,"z":1.5,"pitch":0.0,"yaw":130.751,"roll":0.0}}],"puddles":[]}}