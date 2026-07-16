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
{"case_id":"case_069","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_069","fault_layer":"unknown","causal_explanation":"Dataset labels this case as collision + lane invasion, but error.json does not record either event, only noting speeding. All actuation commands in the vehicle_cmd topic are zero before the reported collision timestamp, but vehicle_status reports non-zero throttle and sustained positive ego speed. No module-level failure is directly confirmed due to label conflict and command-status mismatch.","root_cause_pattern":"Conservative pattern: Ego vehicle exhibits a mismatch between all-zero commanded actuation values in the vehicle_cmd topic and non-zero actual throttle/velocity reported in vehicle_status, with conflicting oracle labels for collision and lane invasion.","preservation_constraints":["Preserve the conflict between dataset labels and error.json events for collision and lane invasion","Preserve the mismatch between all-zero vehicle_cmd commands and non-zero reported ego velocity/throttle in the critical window","Preserve 2 actors in the scenario","Preserve the base map and mission route"],"uncertainty":["Conflict between dataset labels (collision=1, lane_invasion=1) and error.json (collision=0, lane_invasion=0)","Mismatch between all-zero vehicle_cmd commands and non-zero actual throttle/velocity means actuation fault cannot be confirmed","No direct evidence of internal module failure in sensing, perception, or planning"],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Manual review of raw oracle data is required to confirm the presence of collision and lane invasion","Check for the vehicle_cmd/vehicle_status mismatch in generated cases to confirm preservation of the observed behavior"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":86.0,"y":145.0,"z":0.29999998211860657,"pitch":0.0,"yaw":90.0,"roll":0.0},"destination":{"x":182.91,"y":198.76,"z":0.29999998211860657,"yaw":179.999755859375}},"weather":{"cloud":98,"rain":5,"puddle":8,"wind":25,"fog":12,"wetness":10,"angle":47,"altitude":76},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":8.76,"spawn":{"x":67.271,"y":159.74,"z":1.5,"pitch":0.0,"yaw":100.714,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":12.56,"spawn":{"x":67.068,"y":165.818,"z":1.5,"pitch":0.0,"yaw":275.254,"roll":0.0}}],"puddles":[]}}