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
{"case_id":"case_069","model_name":"gpt-5.1","phase1_output":{"case_id":"case_069","fault_layer":"unknown","causal_explanation":"Oracle collision messages occur around 28.46s while ego speed remains about 5.2–5.5 m/s with no braking and continuous throttle, and both detection and prediction topics report multiple objects plus valid final_waypoints. However, error.json does not flag a crash or lane invasion and there is no direct lane-boundary or collision-partner geometry, so only a generic collision symptom with nearby actors can be inferred, without module-level attribution.","root_cause_pattern":"Conservative preservation pattern: the ego vehicle is moving at nonzero speed with nearby actors present and valid final_waypoints available when the collision oracle fires, while braking commands and blocked-waypoint flags remain absent and the precise internal module fault is unknown.","preservation_constraints":["The generated candidate should preserve a collision oracle event near the end of the run.","Ego should be moving at a clearly nonzero speed shortly before the collision (similar few m/s range).","Perception-level object and prediction topics should report at least one nearby actor before the collision.","Planning should publish nonempty final_waypoints without blocked-waypoint flags in the critical window.","There should be no strong evidence of ego braking or stopping in the critical window before the collision."],"uncertainty":["Dataset.xlsx labels indicate collision and lane invasion, but error.json does not flag crash or lane invasion, so the exact oracle ground truth is inconsistent.","No lane-boundary geometry or lane-invasion oracle is provided, so lane invasion cannot be confirmed.","The collision partner and exact impact configuration are not described beyond a generic collision oracle.","vehicle_cmd is all zeros while vehicle_status shows nonzero speed and throttle earlier in the run, making the controller pipeline behavior uncertain.","Module-level failure (perception vs planning vs actuation) cannot be localized from the summarized evidence."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Treat collision as the primary oracle symptom; do not assume lane invasion unless a lane-invasion oracle or geometric lane-boundary crossing is observed in the new run.","Verify that a collision oracle message is present and occurs while ego has nonzero speed similar to the original critical window.","Check that perception and prediction topics report at least one nearby actor in the seconds leading up to the collision.","Confirm that planning publishes nonempty final_waypoints without blocked flags throughout the critical window before impact.","Do not infer specific module responsibility (perception, planning, actuation) purely from these preservation constraints; classification should remain compatible with fault_layer=unknown."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":86.0,"y":145.0,"z":0.29999998211860657,"pitch":0.0,"yaw":90.0,"roll":0.0},"destination":{"x":182.91,"y":198.76,"z":0.29999998211860657,"yaw":179.999755859375}},"weather":{"cloud":98,"rain":5,"puddle":8,"wind":25,"fog":12,"wetness":10,"angle":47,"altitude":76},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":8.76,"spawn":{"x":67.271,"y":159.74,"z":1.5,"pitch":0.0,"yaw":100.714,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":12.56,"spawn":{"x":67.068,"y":165.818,"z":1.5,"pitch":0.0,"yaw":275.254,"roll":0.0}}],"puddles":[]}}