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
- Keep every string short. Do not write explanatory paragraphs.
- Each validation/uncertainty array must contain at most 3 short strings.
- Use plain ASCII quotes and valid JSON syntax only.
- Do not include trailing commas, comments, markdown, or extra keys.

Return JSON schema:
{
  "case_id": "case_XXX",
  "candidate_specs": [
    {
      "candidate_id": "cand_001",
      "high_level_variant": "under 20 words",
      "mutation_intent": "under 30 words",
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
      "pre_execution_validation_rules": ["under 18 words"],
      "post_execution_validation_rules": ["under 18 words"],
      "uncertainty": ["under 18 words"]
    }
  ]
}

Input JSON:
{"case_id":"case_103","model_name":"gpt-5.1","phase1_output":{"case_id":"case_103","fault_layer":"unknown","causal_explanation":["The oracle error_json reports a red-light violation but no lane invasion, while the dataset label reports both lane invasion and red-light violation. Traffic-light states and planning waypoints are available, and ego..."],"root_cause_pattern":"Conservative preservation pattern: a red-light violation is reported by the oracle in a scenario where traffic-light state data and ego pose/odometry are available, but route–light association, stop-line crossing, and lane-boundary crossing are not confirmed, leaving the precise module-level root cause unknown.","preservation_constraints":["The generated candidate should preserve an oracle-reported red_light violation (error_json red=true).","Traffic-light topic data should be available with multiple lights and varying states before the violation.","Ego pose and odometry streams should be available throughout the critical window.","Planning outputs (e.g., final_waypoints) should be present during the run.","Lane_invasion should not be required as a confirmed oracle symptom for same-root-cause matching."],"uncertainty":["Dataset.xlsx reports lane_invasion=1 and group=L+R, while error_json reports lane_invasion=false and group=R.","Route–traffic-light relation is marked unknown; no direct evidence of which light governs the ego route.","Stop-line crossing is not confirmed by the summaries.","Ego lane-boundary crossing is not directly evidenced despite the dataset lane_invasion label.","Module-level (perception vs planning vs actuation vs simulator) attribution cannot be resolved from the available summaries."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Treat the error_json red-light violation as the primary oracle symptom; do not require lane_invasion for same-root-cause matching due to dataset/error_json c...","Post-execution validation should confirm that error_json again reports a red_light violation and that traffic-light messages are available near the violation...","Do not infer or require a specific route–light pairing or confirmed stop-line crossing for matching; only the oracle red flag and traffic-light data availabi...","Module-level root cause should remain unspecified unless additional execution logs clearly localize the failure beyond the current summaries."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":322.09625244140625,"y":129.35906982421875,"z":1.5,"pitch":0.0,"yaw":-179.99993896484375,"roll":0.0},"destination":{"x":283.6458740234375,"y":133.43006896972656,"z":1.5,"yaw":-179.99993896484375}},"weather":{"cloud":74,"rain":96,"puddle":72,"wind":56,"fog":26,"wetness":69,"angle":135,"altitude":9},"actors":[{"index":0,"type":"vehicle","nav_type":"linear","speed":3.55,"spawn":{"x":331.013,"y":149.095,"z":1.5,"pitch":0.0,"yaw":68.769,"roll":0.0}}],"puddles":[{"index":0,"level":0.26,"location":{"x":339.0,"y":129.159,"z":0.0},"size":{"x":350.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.24,"location":{"x":313.918,"y":140.757,"z":0.0},"size":{"x":800.0,"y":800.0,"z":1000.0}}]}}