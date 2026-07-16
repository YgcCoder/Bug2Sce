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
{"case_id":"case_002","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_002","fault_layer":"unknown","causal_explanation":"Dataset and error.json consistently label this case as a red light violation. Critical window evidence shows all-zero vehicle control commands, while vehicle status reports non-zero velocity. No evidence confirms stop-line crossing, route-red-light relation, or identifies a faulty module.","root_cause_pattern":"Conservative preservation pattern: Ego vehicle is consistently labeled as having a red light violation with all-zero control commands in the critical window, with no confirmed module-level root cause.","preservation_constraints":["Preserve the consistent red light violation label from dataset and oracle","Preserve all-zero values for all vehicle control commands in the critical window","Preserve original mission start and goal positions","Post-generation validation must confirm stop-line crossing and route-light relation"],"uncertainty":["Route-light relation and stop-line crossing are not confirmed by available evidence","Mismatch between all-zero vehicle_cmd and non-zero velocity in vehicle_status leaves actuation behavior uncertain","No critical-window evidence directly identifies a faulty module, so root cause attribution is unknown"],"ready_for_phase2_generation":"yes","notes_for_validator":["Validate that generated cases preserve the red light violation label and all-zero critical window vehicle_cmd. Check stop-line crossing and route-light relation post-execution to confirm root cause consistency."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"pitch":0.0,"yaw":-9.1552734375e-05,"roll":0.0},"destination":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"yaw":-89.99993896484375}},"weather":{"cloud":80,"rain":64,"puddle":90,"wind":69,"fog":23,"wetness":99,"angle":289,"altitude":36},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":286.887,"y":327.035,"z":1.5,"pitch":0.0,"yaw":12.1,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":24.0,"spawn":{"x":306.513,"y":331.0,"z":1.5,"pitch":0.0,"yaw":309.044,"roll":0.0}}],"puddles":[]}}