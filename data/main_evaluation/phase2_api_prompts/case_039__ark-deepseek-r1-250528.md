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
{"case_id":"case_039","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_039","fault_layer":"unknown","causal_explanation":"Dataset labels this case as combined stuck and lane invasion failure, but error.json does not detect either failure, creating label conflict. Critical window evidence shows all vehicle_cmd are zero, but ego continues moving with non-zero velocity and throttle reported in vehicle_status. Final waypoints remain available throughout the critical window, no collision is detected.","root_cause_pattern":"Conservative preservation pattern: A mismatch between all-zero vehicle control commands and ongoing non-zero ego movement occurs, with unconfirmed conflicting failure labels, and no module-level fault can be confirmed from available evidence.","preservation_constraints":["Preserve the mismatch between all-zero vehicle_cmd and non-zero ego movement in the critical window","Preserve the conflicting failure labels between dataset and error.json","Preserve presence of final_waypoints throughout the critical window","Preserve 1 actor and 3 puddle regions on the map"],"uncertainty":["Dataset labels stuck=1 and lane_invasion=1 that are not confirmed by error.json","Mismatch between zero vehicle_cmd and non-zero vehicle status cannot confirm actuation failure per rules","No direct evidence localizes fault to a specific Autoware module"],"ready_for_phase2_generation":"yes","notes_for_validator":["Manual review is required to confirm the original failure labels after candidate generation","Generated cases must preserve the vehicle_cmd and ego movement mismatch to be considered same-root-cause","Validate whether the generated case reproduces the dataset-labeled stuck and lane invasion symptoms"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":46.14997863769531,"y":326.9700012207031,"z":0.29999998211860657,"pitch":0.0,"yaw":179.999755859375,"roll":0.0},"destination":{"x":60.10997772216797,"y":330.4599914550781,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":18,"rain":3,"puddle":0,"wind":9,"fog":0,"wetness":2,"angle":23,"altitude":84},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":59.223,"y":331.0,"z":1.5,"pitch":0.0,"yaw":18.019,"roll":0.0}}],"puddles":[{"index":0,"level":0.71,"location":{"x":37.563,"y":312.431,"z":0.0},"size":{"x":650.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.73,"location":{"x":50.849,"y":319.366,"z":0.0},"size":{"x":250.0,"y":250.0,"z":1000.0}},{"index":2,"level":0.16,"location":{"x":74.893,"y":331.0,"z":0.0},"size":{"x":650.0,"y":650.0,"z":1000.0}}]}}