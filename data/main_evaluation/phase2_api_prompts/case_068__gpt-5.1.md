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
{"case_id":"case_068","model_name":"gpt-5.1","phase1_output":{"case_id":"case_068","fault_layer":"unknown","causal_explanation":"The oracle reports a red-light violation, and traffic light states are logged, but the summaries do not confirm that the ego route was governed by any specific light or that a stop line was crossed on red. Ego motion is minimal over the run and vehicle_cmd target speed, accel, and brake commands remain zero while vehicle_status indicates low-speed movement early on. With no confirmed route–light relation or stop-line crossing, the concrete mechanism of the reported red violation and the responsible Autoware layer cannot be localized from the available evidence.","root_cause_pattern":"Conservative preservation pattern: a scenario where an oracle-level red-light violation is reported while traffic light states are available but the relation between the ego route and the signalized intersection, as well as stop-line crossing on red, remains unconfirmed, and module-level responsibility cannot be determined.","preservation_constraints":["The generated candidate should preserve the same oracle symptom: a red-light violation is reported by the oracle or equivalent evaluator.","Traffic light state information should be available from a traffic_lights-like topic during the critical window.","The relation between the ego route and any particular traffic signal should remain unconfirmed in the critical-window summaries (no explicit route-light binding).","Stop-line crossing relative to the controlling light should remain unconfirmed in the critical-window summaries.","Ego vehicle motion should be low or limited, so that red-light violation is not trivially attributable to obvious high-speed intersection running."],"uncertainty":["The oracle indicates a red-light violation but the exact violation timestamp is unknown.","The current summaries mark route_light_relation_confirmed and stop_line_crossing_confirmed as unknown, so it is unclear whether the ego actually crossed a relevant stop line on red.","All vehicle_cmd actuation fields remain zero while vehicle_status shows nonzero velocity for part of the run, so controller and actuation behavior cannot be reliably interpreted.","Module-level attribution (perception vs planning vs actuation vs simulator) is not directly supported by the evidence.","The oracle-level definition of a red-light violation in this scenario is not fully observable from the provided summaries."],"ready_for_phase2_generation":"yes","notes_for_validator":["Post-execution validation must first confirm that the oracle or equivalent evaluator reports a red-light violation for the generated case.","Check that a traffic_lights-like topic exists with multiple signals and state changes during the critical window.","Verify that the analysis pipeline for the generated run does not explicitly resolve route-light relation or stop-line crossing, keeping them unknown as in the original case.","Do not classify a generated case as same-root-cause if module-level evidence clearly shows a standard intersection run-through on red with well-defined route-light linkage; such cases may reflect a different mechanism than this conservative unknown-attribution pattern.","Confirm that ego motion in the generated case is limited or modest, broadly consistent with the low-displacement behavior observed in the original evidence."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":104.8687973022461,"y":59.99010467529297,"z":0.29999998211860657,"pitch":0.0,"yaw":0.0,"roll":0.0},"destination":{"x":392.4700012207031,"y":105.38999938964844,"z":0.29999998211860657,"yaw":90.00004577636719}},"weather":{"cloud":13,"rain":10,"puddle":13,"wind":71,"fog":19,"wetness":26,"angle":199,"altitude":29},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":93.216,"y":57.452,"z":1.5,"pitch":0.0,"yaw":300.718,"roll":0.0}}],"puddles":[]}}