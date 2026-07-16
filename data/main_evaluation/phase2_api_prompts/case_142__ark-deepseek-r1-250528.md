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
{"case_id":"case_142","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_142","fault_layer":"unknown","causal_explanation":"Dataset labels collision, lane invasion, and red-light violation; error.json confirms collision and red-light violation but disagrees on lane invasion, creating a label conflict. A collision occurred, with ego showing non-zero throttle and movement in vehicle status before collision while all Autoware vehicle_cmd outputs were zero. No module-level failure is directly confirmed by available critical window evidence.","root_cause_pattern":"Conservative preservation pattern: Ego experiences confirmed collision and red-light violation when all Autoware vehicle_cmd actuation commands are zero, but vehicle status reports non-zero throttle and ongoing movement, with conflicting lane invasion labeling.","preservation_constraints":["Preserve confirmed oracle symptoms of collision and red-light violation","Preserve the mismatch between all-zero vehicle_cmd commands and non-zero pre-collision throttle in vehicle_status","Preserve 3 actors and 3 puddle regions on the Town01 map","Preserve the original high fog level of 92"],"uncertainty":["lane invasion label conflict between dataset (positive) and error.json (negative)","route-light relation and stop-line crossing for red-light violation are not confirmed by evidence","module-level failure attribution is not directly supported by critical window evidence","the vehicle_cmd/vehicle_status mismatch alone cannot confirm an actuation layer fault"],"ready_for_phase2_generation":"yes","notes_for_validator":["Resolve the lane invasion label conflict before validating generated cases","Verify the all-zero vehicle_cmd / non-zero throttle mismatch is preserved in the pre-collision window","Confirm that collision and red-light violation symptoms are preserved in generated cases"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":86.0,"y":145.0,"z":0.29999998211860657,"pitch":0.0,"yaw":90.0,"roll":0.0},"destination":{"x":182.91,"y":198.76,"z":0.29999998211860657,"yaw":179.999755859375}},"weather":{"cloud":55,"rain":16,"puddle":12,"wind":17,"fog":92,"wetness":42,"angle":270,"altitude":-2},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":7.62,"spawn":{"x":107.155,"y":146.063,"z":1.5,"pitch":0.0,"yaw":91.437,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":13.19,"spawn":{"x":70.537,"y":158.967,"z":1.5,"pitch":0.0,"yaw":162.536,"roll":0.0}},{"index":2,"type":"walker","nav_type":"immobile","speed":0.0,"spawn":{"x":82.335,"y":162.717,"z":1.5,"pitch":0.0,"yaw":138.045,"roll":0.0}}],"puddles":[{"index":0,"level":0.24,"location":{"x":109.756,"y":149.624,"z":0.0},"size":{"x":500.0,"y":700.0,"z":1000.0}},{"index":1,"level":0.69,"location":{"x":92.499,"y":116.39,"z":0.0},"size":{"x":300.0,"y":300.0,"z":1000.0}},{"index":2,"level":0.31,"location":{"x":87.242,"y":136.737,"z":0.0},"size":{"x":250.0,"y":250.0,"z":1000.0}}]}}