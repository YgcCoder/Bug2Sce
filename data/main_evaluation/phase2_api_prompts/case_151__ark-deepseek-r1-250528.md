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
{"case_id":"case_151","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_151","fault_layer":"unknown","causal_explanation":"Dataset labels this case as stuck and lane invasion, but error.json detects neither failure. Critical window evidence shows all zero vehicle control commands and zero ego velocity, while final waypoints remain continuously available. No direct evidence confirms which Autoware module caused the reported symptoms.","root_cause_pattern":"Conservative pattern: Ego vehicle receives all-zero control commands while final waypoints remain available, with conflicting symptom labels between dataset annotation and error.json oracle.","preservation_constraints":["Preserve conflicting symptom labels between dataset annotation and error.json oracle","Preserve continuously available final waypoints during the critical window","Preserve all-zero accel, brake, and steer vehicle commands during the critical window","Preserve zero ego velocity during the critical window"],"uncertainty":["Dataset and error.json have conflicting labels for stuck and lane invasion","No critical window evidence directly localizes the root cause to a specific module","No evidence of lane boundary crossing is provided to confirm the lane invasion symptom"],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Resolve label conflict between dataset and error.json before confirming a generated case matches this root cause","Check for explicit lane boundary crossing evidence to confirm the lane invasion symptom after execution","Verify that final waypoints remain available while all vehicle control commands are zero in generated candidates"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":46.14997863769531,"y":326.9700012207031,"z":0.29999998211860657,"pitch":0.0,"yaw":179.999755859375,"roll":0.0},"destination":{"x":60.10997772216797,"y":330.4599914550781,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":61,"rain":10,"puddle":19,"wind":27,"fog":27,"wetness":69,"angle":260,"altitude":2},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":9.1,"spawn":{"x":17.198,"y":331.0,"z":1.5,"pitch":0.0,"yaw":359.222,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":0.79,"spawn":{"x":39.707,"y":325.715,"z":1.5,"pitch":0.0,"yaw":191.333,"roll":0.0}}],"puddles":[{"index":0,"level":0.44,"location":{"x":45.122,"y":326.855,"z":0.0},"size":{"x":500.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.75,"location":{"x":45.567,"y":321.576,"z":0.0},"size":{"x":800.0,"y":800.0,"z":1000.0}}]}}