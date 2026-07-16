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
{"case_id":"case_029","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_029","fault_layer":"unknown","causal_explanation":"Conflicting labels exist between the dataset (lane invasion + red light violation, group L+R) and error.json (only red light violation, group R). No direct evidence attributes failure to a specific Autoware module, and route-light relation, stop-line crossing, and lane invasion event are unconfirmed.","root_cause_pattern":"Conservative pattern: a Town01 map scenario with conflicting oracle labels for lane invasion and a confirmed red light event in error.json, with unknown module-level root cause.","preservation_constraints":["Preserve conflicting label status between dataset and error.json","Preserve traffic light state data availability in the critical window","Preserve original mission start and goal on Town01 map","Preserve 2 actors in the scenario"],"uncertainty":["Dataset and error.json have conflicting labels for lane invasion and case group","Route-light relation and stop-line crossing for red light violation are not confirmed","Lane invasion event is not confirmed by error.json","No critical-window evidence directly localizes failure to a specific module"],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Resolve the label conflict between dataset and error.json via manual review before root cause generalization","Post-execution validation must check for both lane invasion and red light violation to confirm the actual failure mode"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"pitch":0.0,"yaw":-89.99993896484375,"roll":0.0},"destination":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":100,"rain":1,"puddle":8,"wind":6,"fog":12,"wetness":13,"angle":91,"altitude":81},"actors":[{"index":0,"type":"walker","nav_type":"linear","speed":2.78,"spawn":{"x":343.807,"y":136.276,"z":1.5,"pitch":0.0,"yaw":29.582,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":1.67,"spawn":{"x":340.651,"y":106.21,"z":1.5,"pitch":0.0,"yaw":267.899,"roll":0.0}}],"puddles":[]}}