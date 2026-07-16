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
{"case_id":"case_169","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_169","fault_layer":"unknown","causal_explanation":"The consistent oracle label marks this as a red-light violation. Evidence shows the traffic light topic exists with sampled red states, but route-light relation and stop-line crossing are unconfirmed. Vehicle_cmd has all-zero commands while vehicle_status reports non-zero velocity, but no module-level failure is directly proven by available evidence.","root_cause_pattern":"Conservative preservation pattern: A reported red-light violation occurs in a scenario with no dynamic actors, available traffic light state data including red states, and no confirmed module-level attribution of the failure.","preservation_constraints":["Preserve the red-light violation oracle symptom","No dynamic actors are present in the generated scenario","Scenario uses the Town01 map","Preserve the original start-to-goal mission","Traffic light topic is available with sampled red traffic light states"],"uncertainty":["Route-light relation and stop-line crossing are not confirmed by provided evidence","All-zero vehicle_cmd conflicts with non-zero velocity in vehicle_status, no firm actuation fault attribution","No critical-window evidence directly localizes failure to a specific Autoware module"],"ready_for_phase2_generation":"yes","notes_for_validator":["Confirm stop-line crossing and route-light relation after generation to validate the reported violation","Check for vehicle_cmd/vehicle_status mismatch in the generated case to support module fault attribution"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":334.21539306640625,"y":145.67129516601562,"z":1.5,"pitch":0.0,"yaw":90.00005340576172,"roll":0.0},"destination":{"x":338.97998046875,"y":301.2599792480469,"z":1.5,"yaw":90.00005340576172}},"weather":{"cloud":73,"rain":14,"puddle":19,"wind":4,"fog":93,"wetness":23,"angle":272,"altitude":17},"actors":[],"puddles":[]}}