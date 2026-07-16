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

Return JSON schema:
{
  "case_id": "case_XXX",
  "candidate_specs": [
    {
      "candidate_id": "cand_001",
      "high_level_variant": "short scenario variant description",
      "mutation_intent": "why this variant preserves the Phase 1 pattern",
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
      "pre_execution_validation_rules": ["rule"],
      "post_execution_validation_rules": ["rule"],
      "uncertainty": ["missing evidence"]
    }
  ]
}

Input JSON:
{"case_id":"case_157","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_157","fault_layer":"unknown","causal_explanation":"A confirmed collision occurred. All vehicle commands (accel, brake, steer) are zero in the pre-collision critical window, while ego maintained positive speed (~4.7 m/s) with non-zero throttle reported by vehicle status. Perception detected one object ahead, but planning reported no blocked waypoints on the planned route, and no braking occurred before collision.","root_cause_pattern":"Candidate conservative pattern: Zero commanded output in vehicle_cmd despite a colliding object on the planned route, with ongoing ego movement leading to collision, while module-level root cause is unconfirmed.","preservation_constraints":["Ego travels toward its goal on the Town01 map","A colliding object is present ahead of ego on the planned route pre-collision","All acceleration, brake, and steer commands in vehicle_cmd are zero in the pre-collision critical window","Ego maintains positive forward speed with non-zero throttle reported by vehicle status pre-collision","Collision with the forward object is confirmed by oracle"],"uncertainty":["Zero vehicle_cmd vs non-zero ego movement mismatch prevents confirmed attribution to actuation per rules","It is unknown if zero vehicle_cmd stems from planning failure, actuation failure, or logging error","No direct internal evidence proves planning failed to detect the blocking object, only that the blocked waypoint flag was false"],"ready_for_phase2_generation":"yes","notes_for_validator":["Verify vehicle_cmd is all zero in the pre-collision critical window after generation","Confirm the mismatch between zero vehicle commands and non-zero ego speed/throttle in vehicle status","Check that collision with the forward object occurs as in the original case"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":61,"rain":47,"puddle":40,"wind":72,"fog":45,"wetness":45,"angle":219,"altitude":40},"actors":[{"index":0,"type":"walker","nav_type":"linear","speed":3.18,"spawn":{"x":354.436,"y":124.582,"z":1.5,"pitch":0.0,"yaw":94.79,"roll":0.0}},{"index":1,"type":"walker","nav_type":"autopilot","speed":1.54,"spawn":{"x":321.791,"y":141.759,"z":1.5,"pitch":0.0,"yaw":4.735,"roll":0.0}},{"index":2,"type":"vehicle","nav_type":"autopilot","speed":9.39,"spawn":{"x":354.221,"y":129.106,"z":1.5,"pitch":0.0,"yaw":275.69,"roll":0.0}},{"index":3,"type":"vehicle","nav_type":"autopilot","speed":6.64,"spawn":{"x":303.289,"y":126.562,"z":1.5,"pitch":0.0,"yaw":130.751,"roll":0.0}}],"puddles":[]}}