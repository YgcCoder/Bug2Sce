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
{"case_id":"case_040","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_040","fault_layer":"unknown","causal_explanation":"Dataset and error.json consistently label this case as a red light violation. Traffic light topic data is available, but route-light relation and stop-line crossing are unconfirmed, and no critical-window evidence directly proves which module caused the violation.","root_cause_pattern":"Conservative preservation pattern: Ego completes a mission in Town01 where the oracle consistently labels a red light violation, with module-level root cause unconfirmed.","preservation_constraints":["Preserve the consistent red light violation oracle label","Preserve the same Town01 map","Preserve the same mission start and goal positions","Preserve 36 total traffic lights in the scenario","Post-generation validation must confirm stop-line crossing and route-light relation"],"uncertainty":["Route-light relation (whether ego route passes the relevant red light) is not confirmed","Stop-line crossing (required to confirm red light violation) is not confirmed","vehicle_cmd reports all zero control commands but vehicle_status shows non-zero velocity, so actuation behavior is uncertain","No critical-window evidence directly localizes failure to a specific module or layer"],"ready_for_phase2_generation":"yes","notes_for_validator":["Do not count a generated case as matching this root cause unless stop-line crossing and route-light relation are confirmed post-execution","Verify that red light violation labels are consistent across dataset and error.json after generation","Check for consistency between control commands and vehicle movement in generated cases"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":110.0,"y":129.0,"z":1.0,"pitch":0.0,"yaw":180.0,"roll":0.0},"destination":{"x":113.0,"y":130.0,"z":0.0,"yaw":0.0}},"weather":{"cloud":81,"rain":83,"puddle":56,"wind":45,"fog":34,"wetness":86,"angle":169,"altitude":26},"actors":[{"index":0,"type":"walker","nav_type":"immobile","speed":0.0,"spawn":{"x":93.381,"y":131.014,"z":1.5,"pitch":0.0,"yaw":250.045,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":15.87,"spawn":{"x":109.979,"y":140.165,"z":1.5,"pitch":0.0,"yaw":178.512,"roll":0.0}}],"puddles":[]}}