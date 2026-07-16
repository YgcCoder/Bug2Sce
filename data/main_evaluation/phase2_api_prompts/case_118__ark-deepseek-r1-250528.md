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
{"case_id":"case_118","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_118","fault_layer":"unknown","causal_explanation":"Both dataset and error.json confirm a collision and red-light violation, with a conflicting lane-invasion label. Autoware outputs all-zero vehicle control commands before collision, but vehicle_status reports non-zero throttle and ~5 m/s ego velocity with no braking. No dynamic actors are present, and no module-level failure is directly confirmed by available evidence.","root_cause_pattern":"Conservative pattern: Ego collides when Autoware outputs all-zero vehicle control commands, but ego continues moving at non-zero speed with no braking, while root-cause module attribution remains unknown.","preservation_constraints":["Preserve zero dynamic actors in the scenario","Preserve all-zero vehicle_cmd output from Autoware before collision","Preserve non-zero pre-collision ego velocity and zero braking reported by vehicle_status","Preserve confirmed collision and red-light violation outcomes","Preserve Town01 map"],"uncertainty":["lane invasion label conflict: dataset=1, error.json=0","Mismatch between all-zero vehicle_cmd and non-zero movement in vehicle_status cannot confirm actuation fault alone","No internal module failure evidence available to localize root cause","Route-light relation and stop-line crossing for red-light violation are not confirmed"],"ready_for_phase2_generation":"yes","notes_for_validator":["Check that generated case preserves all-zero vehicle_cmd and non-zero ego movement before collision","Validate oracle outcomes for all three symptoms to resolve label alignment","Do not count a generated case as matching root cause if the actuation command-movement mismatch is not preserved"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":104.8687973022461,"y":59.99010467529297,"z":0.29999998211860657,"pitch":0.0,"yaw":0.0,"roll":0.0},"destination":{"x":392.4700012207031,"y":105.38999938964844,"z":0.29999998211860657,"yaw":90.00004577636719}},"weather":{"cloud":12,"rain":24,"puddle":39,"wind":17,"fog":46,"wetness":45,"angle":269,"altitude":38},"actors":[],"puddles":[{"index":0,"level":0.16,"location":{"x":130.218,"y":66.75,"z":0.0},"size":{"x":500.0,"y":500.0,"z":1000.0}},{"index":1,"level":0.93,"location":{"x":122.54,"y":39.454,"z":0.0},"size":{"x":300.0,"y":300.0,"z":1000.0}},{"index":2,"level":0.41,"location":{"x":113.367,"y":66.085,"z":0.0},"size":{"x":500.0,"y":500.0,"z":1000.0}}]}}