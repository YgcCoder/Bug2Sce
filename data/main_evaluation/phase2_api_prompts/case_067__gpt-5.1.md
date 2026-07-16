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
{"case_id":"case_067","model_name":"gpt-5.1","phase1_output":{"case_id":"case_067","fault_layer":"unknown","causal_explanation":"The oracle error.json reports only a red-light violation, while the dataset labels additionally mark stuck and lane-invasion, creating unresolved label conflict. Critical-window evidence confirms a red-light event with traffic light states available but does not confirm any route–light relation, stop-line crossing, lane-boundary crossing, or long-term immobility. Ego continues to move over the last 60 seconds with nonzero displacement and speed, and vehicle_status shows motion while vehicle_cmd remains zero throughout, making internal controller behavior unclear. With no confirmed collision, lane invasion, or verified stop-line interaction, the precise mechanism behind the reported red-light violation and the extra dataset labels remains uncertain.","root_cause_pattern":"Conservative preservation pattern: a run in which the external oracle flags a red-light violation while traffic-light states are present but route–light and stop-line relations are not established, and additional dataset labels (stuck, lane invasion) conflict with the oracle, leaving root-cause attribution and exact failure mechanism unknown.","preservation_constraints":["The generated candidate should preserve an oracle-reported red-light violation in error.json.","Traffic light state information should be available on the traffic_lights topic during the critical window.","Route–light relation and stop-line crossing should remain unconfirmed or unknown in the available summaries.","No collision event should be reported by error.json.","Label or symptom ambiguity (e.g., between dataset labels and oracle events) should be preserved or not fully resolved."],"uncertainty":["Dataset.xlsx labels indicate stuck and lane_invasion while error.json does not, leading to unresolved label conflict.","The summaries explicitly mark route–light relation and stop-line crossing as unknown, so the exact nature of the red-light violation is not proven.","Lane invasion is not confirmed by any lane-boundary crossing evidence.","Despite nonzero movement and eventual zero velocity, the oracle does not flag stuck; the cause of stopping behavior is unclear.","vehicle_cmd remains zero while vehicle_status shows motion and control efforts, making the controller and actuation chain behavior uncertain."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Verify post-execution that error.json again reports a red-light violation without collision.","Check that /carla/traffic_lights is available and that summaries cannot conclusively establish the ego route–light relation or stop-line crossing at the violation time.","Confirm that no explicit lane-boundary crossing evidence is present before labeling any generated case as same-root-cause.","Inspect post-run logs for continued ambiguity or conflict between dataset-level labels and oracle events; do not require that this conflict be resolved.","Do not attribute the bug to a specific Autoware layer unless additional execution logs directly link the red-light event to perception, planning, or actuation behavior."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":3,"rain":23,"puddle":46,"wind":93,"fog":27,"wetness":36,"angle":347,"altitude":44},"actors":[],"puddles":[]}}