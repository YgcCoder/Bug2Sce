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
{"case_id":"case_079","model_name":"gpt-5.1","phase1_output":{"case_id":"case_079","fault_layer":"unknown","causal_explanation":"The oracle reports a red-light violation, while dataset labels additionally mark lane invasion; however, the error.json lane_invasion flag is false, so only the red-light symptom is supported by the oracle. Traffic-light states are available and include red lights, but the summaries do not confirm that the ego route aligns with any specific signal or that a stop line was crossed on red. Ego pose and odometry show limited longitudinal movement overall, and planning, perception, and actuation topics are present, with vehicle_cmd remaining zero despite nonzero velocity in vehicle_status; this mismatch does not by itself localize the fault to any module. Consequently, the underlying mechanism and responsible layer remain uncertain.","root_cause_pattern":"Conservative preservation pattern: the ego vehicle is in a mapped urban environment with active traffic-light signals (including red states), the oracle flags a red-light violation, and Autoware perception, prediction, planning, and actuation topics are all active, but the available summaries do not establish the exact route-light relation or stop-line crossing mechanism.","preservation_constraints":["The generated case should preserve an oracle-reported red-light violation symptom.","Traffic-light signals should be present on the map with sampled states that include red.","Autoware perception outputs for objects and prediction objects should be available during the critical window.","Autoware planning final_waypoints should be continuously available during the approach to the violation.","Vehicle status should indicate ego motion at some point in the run, even if vehicle_cmd outputs are low or zero."],"uncertainty":["Dataset.xlsx marks lane_invasion=1 and group=L+R, but error.json reports lane_invasion=false and group=R, so the lane-invasion label cannot be treated as confirmed.","The route-light relation and whether the ego actually crossed a stop line on red are marked as unknown in the summaries.","The internal cause of the red-light violation (e.g., misperception, misplanning, or control behavior) is not identifiable from the provided evidence.","Vehicle_cmd remains all zeros while vehicle_status shows nonzero velocity, leaving controller behavior and responsibility ambiguous."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Do not assume lane invasion as part of the ground-truth symptom because dataset and error.json conflict; only the oracle red-light violation is confirmed.","Post-execution validation must check that the oracle again reports a red-light violation and that traffic_lights states include red during the relevant window.","Do not infer a specific module failure (sensing, perception, planning, or actuation) without additional logs beyond the provided summaries.","If a generated case shows a red-light oracle event but with fundamentally different conditions (e.g., no traffic-light objects or different Autoware topic availability), it should not be counted as same-root-cause.","Controller-layer responsibility must not be inferred solely from mismatches between vehicle_cmd and vehicle_status; additional evidence would be required."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":59,"rain":63,"puddle":75,"wind":24,"fog":32,"wetness":57,"angle":227,"altitude":22},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":318.806,"y":120.233,"z":1.5,"pitch":0.0,"yaw":77.296,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":0.63,"spawn":{"x":304.093,"y":135.488,"z":1.5,"pitch":0.0,"yaw":262.763,"roll":0.0}}],"puddles":[]}}