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
{"case_id":"case_168","model_name":"gpt-5.1","phase1_output":{"case_id":"case_168","fault_layer":"unknown","causal_explanation":"The oracle reports a red-light violation without lane invasion, while the dataset labels indicate both lane invasion and red-light violation. During the critical window, the ego vehicle is moving at nonzero speed with nonzero steering reported in vehicle_status, even though all vehicle_cmd fields remain zero. Traffic light messages show multiple signals, including red states, but the summaries do not establish which light, if any, governs the ego route or whether a stop line was crossed. A collision is recorded by the oracle near the end of the run despite the error.json crash flag being false. Because the route–light relation, lane-boundary interaction, and control pipeline behavior are not directly evidenced, the mechanism leading to the red-light violation and collision is uncertain.","root_cause_pattern":"Conservative preservation pattern: an ego vehicle in Town01 approaches an intersection environment with active traffic lights and puddles present, receives traffic-light state information and nonempty final_waypoints, but later exhibits an oracle red-light violation (and a collision symptom) under zero-valued vehicle_cmd outputs and nonzero ego motion, with unclear route–light relation and lane-boundary behavior.","preservation_constraints":["The generated case should preserve an oracle-detected red-light violation as the primary symptom.","Traffic light topic data must be available with multiple lights and at least one red state before the violation.","Final_waypoints must remain available and populated (nonzero waypoint counts) through the critical window.","vehicle_cmd messages should remain effectively zeroed while vehicle_status shows the ego moving with nonzero speed near the violation window.","The scenario should occur on the Town01 map with a similar mission type and no additional dynamic actors."],"uncertainty":["Dataset.xlsx reports lane_invasion=1 while error.json reports lane_invasion=false, so lane invasion is not confirmed.","The oracle marks a red-light violation, but route–light relation and stop-line crossing are explicitly unknown in the summaries.","Collision messages exist with a significant impulse range, but error_json crash=false, so the collision severity or oracle criteria are unclear.","The cause of the mismatch between zero vehicle_cmd commands and nonzero vehicle_status motion cannot be localized to actuation, planning, or simulator based on the available summaries.","Lane-boundary interactions and exact ego position relative to stop lines are not provided."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Verify after execution that the oracle flags a red-light violation; do not require lane invasion as a success criterion because of dataset–error_json conflict.","Check that traffic_lights data include at least one red light active before the violation, but do not assume any particular light governs the ego without explicit route–light evidence.","Confirm that final_waypoints remain available and nonempty during the critical window leading to the violation.","Confirm that vehicle_cmd remains effectively zero while vehicle_status indicates the ego is moving at nonzero speed around the violation window; this pattern is part of the root-cause preservation, not definitive evidence of an actuation bug.","Do not require a confirmed collision or lane-boundary crossing for same-root-cause matching; use the red-light violation plus the command–status mismatch and traffic-light presence as primary matching conditions.","If future logs provide precise route–light association or stop-line crossing information, they may refine module attribution; until then, keep fault_layer as unknown."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":104.8687973022461,"y":59.99010467529297,"z":0.29999998211860657,"pitch":0.0,"yaw":0.0,"roll":0.0},"destination":{"x":392.4700012207031,"y":105.38999938964844,"z":0.29999998211860657,"yaw":90.00004577636719}},"weather":{"cloud":65,"rain":37,"puddle":36,"wind":55,"fog":52,"wetness":46,"angle":91,"altitude":17},"actors":[],"puddles":[{"index":0,"level":1.78,"location":{"x":102.653,"y":36.356,"z":0.0},"size":{"x":300.0,"y":500.0,"z":1000.0}},{"index":1,"level":1.69,"location":{"x":107.359,"y":89.751,"z":0.0},"size":{"x":500.0,"y":500.0,"z":1000.0}}]}}