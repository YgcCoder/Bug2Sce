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
{"case_id":"case_104","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_104","fault_layer":"unknown","causal_explanation":"Dataset labels this case as a red-light violation, but error_json detects no red-light violation. Available evidence does not confirm stop-line crossing or relation between ego's route and a red traffic light. Ego has all-zero actuation commands and near-zero velocity in the critical window, with no other failures detected.","root_cause_pattern":"Conflicting oracle labels for red-light violation exist, with no confirmed module-level failure, and ego is stationary with zero actuation commands in the critical window.","preservation_constraints":["Preserve conflicting red-light violation status between dataset and error_json","Preserve zero actuation commands and near-zero ego velocity in the critical window","Preserve no dynamic actors in the scenario","Preserve 36 total traffic lights available in the map during the critical window"],"uncertainty":["Dataset and error.json disagree on red-light violation status","Stop-line crossing is not confirmed by available evidence","Route-light relation is not confirmed by available evidence","No module failure is directly proven by critical window evidence"],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Manual review is required to resolve the conflicting red-light labels before same-root-cause classification","Generated cases must be validated for confirmed stop-line crossing and red-light violation before any module attribution"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"pitch":0.0,"yaw":-89.99993896484375,"roll":0.0},"destination":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":63,"rain":10,"puddle":2,"wind":18,"fog":82,"wetness":50,"angle":315,"altitude":3},"actors":[],"puddles":[{"index":0,"level":0.64,"location":{"x":314.031,"y":100.78,"z":0.0},"size":{"x":500.0,"y":700.0,"z":1000.0}}]}}