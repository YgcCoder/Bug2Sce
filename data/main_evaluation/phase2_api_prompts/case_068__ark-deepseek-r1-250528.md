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
{"case_id":"case_068","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_068","fault_layer":"unknown","causal_explanation":"Both dataset and error.json oracle consistently label this as a red-light violation case. No direct evidence confirms which Autoware module failed, and critical window evidence does not confirm stop-line crossing or the relation between ego's route and the red traffic light. All commands in vehicle_cmd are zero while vehicle_status reports non-zero velocity, leaving actuation behavior uncertain.","root_cause_pattern":"Conservative preservation pattern: consistently labeled red-light violation case with available core topics, while module-level root cause remains unconfirmed.","preservation_constraints":["Preserve consistent red-light violation labeling from both dataset and error.json oracle","Preserve availability of all core Autoware perception, planning, actuation and traffic light topics","Preserve one actor in the scenario","Preserve Town01 map for the scenario"],"uncertainty":["Stop-line crossing on a red light is not confirmed by available evidence","Relation between ego's planned route and the nearest red traffic light is unconfirmed","Mismatch between all-zero vehicle_cmd and non-zero measured velocity leaves actuation behavior uncertain","No critical-window evidence directly localizes failure to a specific module or layer"],"ready_for_phase2_generation":"yes","notes_for_validator":["Confirm stop-line crossing and red traffic light state for the ego route after executing the generated case","Check for module-level failure evidence in post-generation traces to refine root cause attribution"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":104.8687973022461,"y":59.99010467529297,"z":0.29999998211860657,"pitch":0.0,"yaw":0.0,"roll":0.0},"destination":{"x":392.4700012207031,"y":105.38999938964844,"z":0.29999998211860657,"yaw":90.00004577636719}},"weather":{"cloud":13,"rain":10,"puddle":13,"wind":71,"fog":19,"wetness":26,"angle":199,"altitude":29},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":93.216,"y":57.452,"z":1.5,"pitch":0.0,"yaw":300.718,"roll":0.0}}],"puddles":[]}}