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
{"case_id":"case_010","model_name":"gpt-5.1","phase1_output":{"case_id":"case_010","fault_layer":"unknown","causal_explanation":"The dataset labels this case as a lane invasion, but the error.json oracle reports no lane invasion and only a goal-related issue. Critical-window evidence shows the ego moving a short distance from the start pose while planning outputs, perception outputs, and control commands are continuously available. However, no direct lane-boundary or lane-marking information is provided, so the presence, timing, or mechanism of any lane invasion cannot be determined from the available traces.","root_cause_pattern":"Conservative preservation pattern: ego vehicle executes a short-distance mission on Town01 in rainy, puddled conditions with active perception, planning (stable final_waypoints), and zeroed vehicle_cmd, where the external oracle does not confirm lane invasion despite the dataset label.","preservation_constraints":["The generated case should preserve a Town01 mission with a short start-to-goal separation similar to the original scenario.","Rainy, high-wetness and puddled weather conditions should be present during the run.","Perception object and prediction topics should remain active before the failure or termination condition.","Planning final_waypoints should remain continuously available with a stable waypoint count.","The external oracle (error.json) should not report lane_invasion while the dataset or meta-labeling treats the case as a lane-invasion-group scenario."],"uncertainty":["Dataset.xlsx flags lane_invasion while error.json reports lane_invasion=false, so the presence of a true lane invasion is not confirmed.","No lane-marking, lane-boundary, or explicit lane-crossing evidence is provided, preventing direct observation of lane invasion.","vehicle_cmd is always zero while vehicle_status velocity reaches up to about 8.9 m/s, making controller and actuation behavior ambiguous.","Odometry and current_pose summaries show only limited motion and do not include detailed trajectory geometry relative to lanes."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Do not assume lane invasion occurred; post-execution validation must use lane-boundary ground truth or a trusted oracle to check for lane crossing.","Confirm that error.json in generated cases still reports lane_invasion=false while any higher-level labeling treats the case as lane-related to match the original conflict pattern.","Verify that perception, planning, and actuation topics are present and show similar availability patterns before the termination condition.","Check ego trajectory length and ensure the mission remains a short-distance route on Town01, without adding complex multi-actor interactions unless explicitly intended."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":110.0,"y":129.0,"z":1.0,"pitch":0.0,"yaw":180.0,"roll":0.0},"destination":{"x":113.0,"y":130.0,"z":0.0,"yaw":0.0}},"weather":{"cloud":83,"rain":57,"puddle":74,"wind":30,"fog":3,"wetness":79,"angle":278,"altitude":7},"actors":[],"puddles":[{"index":0,"level":0.08,"location":{"x":111.012,"y":125.676,"z":0.0},"size":{"x":800.0,"y":700.0,"z":1000.0}},{"index":1,"level":0.57,"location":{"x":131.334,"y":131.335,"z":0.0},"size":{"x":800.0,"y":800.0,"z":1000.0}},{"index":2,"level":0.21,"location":{"x":107.58,"y":139.272,"z":0.0},"size":{"x":650.0,"y":650.0,"z":1000.0}}]}}