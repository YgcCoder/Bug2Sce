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
{"case_id":"case_029","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_029","fault_layer":"unknown","causal_explanation":"Dataset labels this case as having both lane invasion and red light violation, but error.json only confirms a red light event, with open conflict on the lane invasion label. No available critical-window evidence directly localizes the failure to a specific Autoware module.","root_cause_pattern":"Conservative preservation pattern: Ego vehicle encounters a red traffic light during its Town01 mission, with conflicting oracle labels for an additional lane invasion fault, and no confirmed module-level root cause from available evidence.","preservation_constraints":["Preserve the mission start and goal positions on the Town01 map","Preserve the presence of 2 actors in the scenario","Preserve the confirmed red light event reported by error.json","Preserve the conflicting lane invasion and fault group labels between dataset and error.json","Preserve enabled rain in the scenario weather conditions"],"uncertainty":["Dataset and error.json conflict on lane_invasion label and fault group assignment","Route-light relation and stop-line crossing for red light violation are unconfirmed","Lane boundary crossing for the reported lane invasion is unconfirmed","No critical-window evidence directly attributes fault to any specific Autoware module","All sampled vehicle_cmd values are zero while vehicle_status recorded non-zero velocity, so actuation behavior is uncertain"],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Resolve the label conflict between dataset and error.json before confirming same-root-cause status for generated cases","After generation, verify stop-line crossing to confirm red light violation and lane boundary crossing to confirm lane invasion if required"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"pitch":0.0,"yaw":-89.99993896484375,"roll":0.0},"destination":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":100,"rain":1,"puddle":8,"wind":6,"fog":12,"wetness":13,"angle":91,"altitude":81},"actors":[{"index":0,"type":"walker","nav_type":"linear","speed":2.78,"spawn":{"x":343.807,"y":136.276,"z":1.5,"pitch":0.0,"yaw":29.582,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":1.67,"spawn":{"x":340.651,"y":106.21,"z":1.5,"pitch":0.0,"yaw":267.899,"roll":0.0}}],"puddles":[]}}