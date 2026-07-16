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
{"case_id":"case_061","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_061","fault_layer":"unknown","causal_explanation":"Both dataset and error.json confirm collision and red light violation, but lane invasion status is conflicting. All Autoware actuation commands are zero in the pre-collision window, but vehicle_status shows non-zero throttle, zero braking, and ego moving at ~5m/s before collision. No blocked waypoints are detected, the closest detected object is 55m from ego, and no direct evidence attributes failure to a specific module.","root_cause_pattern":"Conservative preservation pattern: Ego proceeds to collision and confirmed red light violation when all Autoware actuation commands are zero, but ego continues moving with non-zero throttle and no braking in the pre-collision window, with module-level fault attribution unconfirmed.","preservation_constraints":["Preserve confirmed collision and red light violation as failure symptoms","Preserve all-zero actuation commands in the pre-collision critical window","Preserve non-zero throttle, zero brake, and forward ego movement in pre-collision vehicle status","Preserve no detected blocked waypoints before collision","Preserve the lane invasion label conflict between dataset and error.json"],"uncertainty":["Lane invasion label conflicts between dataset and error.json, so lane invasion failure is unconfirmed","Mismatch between all-zero vehicle_cmd and non-zero vehicle_status throttle is not sufficient to confirm actuation fault per rules","No direct evidence localizes failure to sensing, perception, or planning layers","Collision cause is unconfirmed because the closest detected object is far from ego before collision"],"ready_for_phase2_generation":"yes","notes_for_validator":["Resolve the lane invasion label conflict before confirming generated case failure modes","Verify pre-collision all-zero vehicle_cmd and forward vehicle movement match the preserved root pattern"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"pitch":0.0,"yaw":-9.1552734375e-05,"roll":0.0},"destination":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"yaw":-89.99993896484375}},"weather":{"cloud":22,"rain":1,"puddle":72,"wind":86,"fog":3,"wetness":33,"angle":47,"altitude":40},"actors":[{"index":0,"type":"walker","nav_type":"linear","speed":2.52,"spawn":{"x":307.106,"y":326.717,"z":1.5,"pitch":0.0,"yaw":273.916,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":1.91,"spawn":{"x":312.164,"y":331.0,"z":1.5,"pitch":0.0,"yaw":340.961,"roll":0.0}}],"puddles":[]}}