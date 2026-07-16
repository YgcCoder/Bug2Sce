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
{"case_id":"case_151","model_name":"gpt-5.1","phase1_output":{"case_id":"case_151","fault_layer":"unknown","causal_explanation":"The oracle error_json reports no stuck or lane-invasion event and instead flags a goal-related deviation, while the dataset labels this case as both stuck and lane-invasion. Within the critical window the ego continues to move some distance with low but nonzero average velocity and has consistently available final waypoints and perception/prediction objects. Vehicle_cmd remains zero throughout the log, yet control-related fields in the stuck_window summary indicate nonzero throttle and brake activity, and higher ego velocity than the trace_summary vehicle_status range suggests, creating a mismatch between summarized control/velocity statistics. Because of these inconsistencies, the true symptom (stuck vs simple goal failure vs lane invasion) and the responsible Autoware layer cannot be reliably inferred from the available evidence.","root_cause_pattern":"Conservative preservation pattern: an oracle goal-deviation case with low-speed ego motion and active perception and planning signals, where dataset labels claim stuck and lane-invasion but error_json does not, leaving the underlying module-level fault and even the primary symptom uncertain.","preservation_constraints":["The generated case should reproduce an oracle outcome indicating failure to reach the intended goal or a significant goal deviation, without confirmed collision or red-light violation in error_json.","Perception and prediction object topics should remain active with at least one detected object during the critical window.","Planning final_waypoints should remain available and nonempty throughout the critical window.","The ego vehicle should exhibit low but nonzero movement over an extended interval before termination, rather than a clear immediate halt or high-speed behavior.","Dataset-style labels or higher-level annotations should allow for possible stuck and/or lane-invasion tagging even if the runtime oracle does not confirm these events."],"uncertainty":["Dataset.xlsx labels indicate stuck and lane_invasion, but error_json reports neither; the primary symptom is ambiguous.","Vehicle_cmd remains zero while the stuck_window summary indicates nonzero throttle, brake, and ego velocity, conflicting with the trace_summary vehicle_status ranges.","No direct evidence localizes the issue to sensing, perception, planning, actuation, simulator, or map.","Lane invasion is not confirmed by any dedicated oracle event or explicit lane-boundary evidence.","The exact controller behavior and its relationship to vehicle motion cannot be reliably inferred from the conflicting control summaries."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Before declaring same-root-cause, verify post-execution that error_json reports a goal-related failure without collision, stuck, lane_invasion, red_light, or speeding.","Check that perception and prediction objects, as well as final_waypoints, remain available and populated in the critical window.","Confirm that the ego exhibits low but nonzero movement over an extended duration rather than being strictly stationary or clearly high-speed.","Do not assume lane invasion unless a dedicated oracle lane_invasion event or explicit lane-boundary evidence appears in the generated run.","Module-level attribution (e.g., to planning or control) must not be inferred solely from topic existence or zero vehicle_cmd; additional internal evidence would be required."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":46.14997863769531,"y":326.9700012207031,"z":0.29999998211860657,"pitch":0.0,"yaw":179.999755859375,"roll":0.0},"destination":{"x":60.10997772216797,"y":330.4599914550781,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":61,"rain":10,"puddle":19,"wind":27,"fog":27,"wetness":69,"angle":260,"altitude":2},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":9.1,"spawn":{"x":17.198,"y":331.0,"z":1.5,"pitch":0.0,"yaw":359.222,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":0.79,"spawn":{"x":39.707,"y":325.715,"z":1.5,"pitch":0.0,"yaw":191.333,"roll":0.0}}],"puddles":[{"index":0,"level":0.44,"location":{"x":45.122,"y":326.855,"z":0.0},"size":{"x":500.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.75,"location":{"x":45.567,"y":321.576,"z":0.0},"size":{"x":800.0,"y":800.0,"z":1000.0}}]}}