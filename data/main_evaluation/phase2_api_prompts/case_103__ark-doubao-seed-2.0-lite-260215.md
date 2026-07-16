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
{"case_id":"case_103","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_103","fault_layer":"unknown","causal_explanation":"Dataset labels indicate both lane invasion and red light violation, while error.json only confirms red light violation, creating a label conflict. No evidence confirms stop-line crossing for red light or lane-boundary crossing for lane invasion. A mismatch exists between all-zero vehicle commands and non-zero velocity/throttle in vehicle status, but this mismatch alone cannot confirm actuation failure. No critical-window evidence directly localizes the failure to a specific module.","root_cause_pattern":"Conservative preservation pattern: Ego travels on Town01 map in heavy rainy wet conditions with puddles, has a confirmed red light event and conflicting labels for an additional lane invasion, with an observed mismatch between all-zero actuation commands and non-zero vehicle movement, while module-level root cause remains unconfirmed.","preservation_constraints":["Preserve Town01 map and the given mission start and goal positions","Preserve heavy rain, high wetness conditions, and 2 puddle regions","Preserve presence of 1 nearby actor","Preserve the label conflict between dataset and error.json for lane invasion","Preserve the confirmed red light event reported in error.json"],"uncertainty":["Dataset and error.json conflict on lane invasion status and overall failure group","Route-light relation and stop-line crossing for red light are not confirmed","Lane-boundary crossing for lane invasion is not confirmed","Actuation command and vehicle status mismatch cannot confirm actuation failure alone","No evidence supports module-level failure attribution"],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Resolve the label conflict between dataset and error.json before confirming generated case root cause","Validate whether stop-line crossing (for red light) and lane-boundary crossing (for lane invasion) occur after generation","Check if the mismatch between vehicle_cmd and vehicle_status is reproduced in generated cases"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":74,"rain":96,"puddle":72,"wind":56,"fog":26,"wetness":69,"angle":135,"altitude":9},"actors":[{"index":0,"type":"vehicle","nav_type":"linear","speed":3.55,"spawn":{"x":331.013,"y":149.095,"z":1.5,"pitch":0.0,"yaw":68.769,"roll":0.0}}],"puddles":[{"index":0,"level":0.26,"location":{"x":339.0,"y":129.159,"z":0.0},"size":{"x":350.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.24,"location":{"x":313.918,"y":140.757,"z":0.0},"size":{"x":800.0,"y":800.0,"z":1000.0}}]}}