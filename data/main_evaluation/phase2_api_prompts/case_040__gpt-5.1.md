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
{"case_id":"case_040","model_name":"gpt-5.1","phase1_output":{"case_id":"case_040","fault_layer":"unknown","causal_explanation":"The oracle reports a red-light violation, and traffic light states are available and changing, but the summaries do not confirm whether the ego’s route is governed by any of these lights or whether a stop line was crossed. Vehicle commands are zero throughout despite nonzero ego velocity, making controller behavior uncertain. Given the lack of explicit route–light association and stop-line evidence, the mechanism behind the violation is unknown from the provided data.","root_cause_pattern":"Conservative preservation pattern: a red-light violation is flagged by the oracle while traffic light state information is available during the run, but the route–light relationship and actual stop-line crossing remain unconfirmed and module-level responsibility is unknown.","preservation_constraints":["The generated candidate should reproduce an oracle-reported red-light violation (red=true).","Traffic light state messages should be available throughout the approach to the violation.","Traffic light states should vary across at least two distinct values (e.g., including a red state code) before the violation window ends.","Ego-vehicle motion should be present (nonzero velocity at some time) during the scenario.","Final waypoints should be available and non-null over the critical window."],"uncertainty":["The route–light relation is explicitly marked unknown; it is not confirmed that any observed traffic light governs the ego lane.","Stop-line crossing is explicitly unknown, so the physical nature of the red-light violation is not evidenced.","Module-level attribution (perception vs. planning vs. actuation) is not supported by critical-window data.","vehicle_cmd is all zeros while vehicle_status shows movement, making the control signal path and its interpretation uncertain.","The specific mapping of traffic light state codes (0,1,2) to colors is not given."],"ready_for_phase2_generation":"yes","notes_for_validator":["Post-execution, confirm that the oracle reports red=true without crash, stuck, lane invasion, or speeding, matching the original symptom.","Verify that traffic light messages exist and that at least one light attains a red-state code at some time before the end of the run.","Do not assume that any specific traffic light governs the ego route unless explicit route–light association or stop-line evidence is available; same-root-cause classification should not require a confirmed governing light.","Check that the ego vehicle exhibits nonzero velocity at some point, ensuring that a static-start artifact is not mistaken for a red-light violation.","Confirm that final_waypoints are present and structurally consistent (non-null, stable count) across the critical window, indicating that a full planning pipeline is active."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":110.0,"y":129.0,"z":1.0,"pitch":0.0,"yaw":180.0,"roll":0.0},"destination":{"x":113.0,"y":130.0,"z":0.0,"yaw":0.0}},"weather":{"cloud":81,"rain":83,"puddle":56,"wind":45,"fog":34,"wetness":86,"angle":169,"altitude":26},"actors":[{"index":0,"type":"walker","nav_type":"immobile","speed":0.0,"spawn":{"x":93.381,"y":131.014,"z":1.5,"pitch":0.0,"yaw":250.045,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":15.87,"spawn":{"x":109.979,"y":140.165,"z":1.5,"pitch":0.0,"yaw":178.512,"roll":0.0}}],"puddles":[]}}