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
{"case_id":"case_004","model_name":"gpt-5.1","phase1_output":{"case_id":"case_004","fault_layer":"unknown","causal_explanation":"The oracle reports a red-light violation while the ego essentially does not move from its start pose and there are no dynamic actors. Traffic-light states are available, but the summaries do not confirm whether any of the observed lights govern the ego’s route or whether the ego crossed a stop line. Dataset labels additionally mark lane invasion, but the online oracle does not. Given these conflicts and the lack of precise route–light or lane-boundary evidence, the underlying cause is unknown; the most conservative interpretation is an oracle-level red violation with minimal ego motion in a static scene.","root_cause_pattern":"Conservative preservation pattern: a red-light violation is reported by the oracle in a scenario with available traffic-light state data and minimal ego displacement, without confirmed route–light relation, lane-boundary crossing, or dynamic actors.","preservation_constraints":["The generated scenario should reproduce an oracle-reported red-light violation (error_json red=true).","Traffic-light state messages should be available before the reported violation.","No collision and no stuck condition should be reported by the oracle.","The ego vehicle should exhibit minimal net displacement between start and end of the run.","No additional dynamic actors should be present beyond those implied by the oracle traffic-light objects."],"uncertainty":["Dataset.xlsx marks lane_invasion=1 and group=L+R, while error.json reports lane_invasion=false and group=R.","The summaries do not confirm any route–light relation or stop-line crossing, so the mechanism of the red-light violation is unknown.","Vehicle_cmd is all zeros while vehicle_status shows small nonzero velocity and throttle; controller and actuation behavior cannot be reliably interpreted from this mismatch.","Perception and prediction objects are present, but without detailed spatial context their role in the red violation cannot be determined."],"ready_for_phase2_generation":"yes","notes_for_validator":["Post-execution, verify that error_json (or equivalent oracle) reports red=true, crash=false, stuck=false, and lane_invasion=false for a candidate to be considered same-root-cause.","Check odometry to ensure the ego’s net displacement between the first and last samples remains very small, matching the minimal-motion condition.","Confirm that the traffic_lights topic is present with varying states but that route–light and stop-line relations remain unconfirmed in the logs, preserving the mechanism ambiguity.","Do not require evidence of lane invasion when judging same-root-cause; dataset-level lane labels are explicitly marked as conflicting and should not be enforced.","Treat any clear confirmation of lane-boundary crossing or explicit route–stop-line association as a deviation from this case’s conservative root-cause pattern."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":24,"rain":7,"puddle":9,"wind":93,"fog":19,"wetness":29,"angle":105,"altitude":71},"actors":[],"puddles":[{"index":0,"level":0.09,"location":{"x":350.843,"y":129.224,"z":0.0},"size":{"x":650.0,"y":500.0,"z":1000.0}}]}}