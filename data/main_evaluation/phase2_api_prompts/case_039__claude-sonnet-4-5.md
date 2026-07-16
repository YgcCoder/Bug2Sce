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
{"case_id":"case_039","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_039","fault_layer":"unknown","causal_explanation":["Dataset.xlsx labels this case as stuck+lane_invasion, but error.json reports neither stuck nor lane_invasion (only goal-distance=57.7m). Critical-window evidence shows ego traveled 101.96m over 60s (mean velocity 1.05..."],"root_cause_pattern":"Conservative preservation pattern: ego exhibits low-speed movement with available final waypoints and zero vehicle_cmd while vehicle_status shows actuation, in a scenario where dataset and error.json oracles disagree on stuck and lane_invasion.","preservation_constraints":["Ego should exhibit low average velocity (≈1 m/s) over a sustained window while final waypoints remain available.","Vehicle_cmd should remain zero (accel, brake, steer all 0) while vehicle_status shows non-zero throttle, brake, or steer.","Nearby actors (1-9 detected objects) should be present during the critical window.","Post-execution validation must check for oracle-label consistency and compare dataset vs error.json outcomes."],"uncertainty":["Dataset.xlsx labels stuck=1 and lane_invasion=1, but error.json reports stuck=0 and lane_invasion=0; oracle conflict requires manual review.","Vehicle_cmd all zero while vehicle_status shows throttle/brake/steer activity; unclear whether this is a controller fault, simulator artifact, or data-collection issue.","No direct evidence proving which Autoware module (perception, planning, or actuation) caused the labeled stuck or lane_invasion.","Lane_invasion label is not supported by lane-boundary crossing evidence in the provided data."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Manual review required to resolve dataset vs error.json oracle conflict before treating this as ground truth.","Do not count a generated case as same-root-cause unless post-execution confirms the vehicle_cmd=0 + vehicle_status≠0 pattern and oracle-label consistency.","Check whether the vehicle_cmd/vehicle_status mismatch is a simulator artifact or a genuine Autoware controller issue.","Verify lane_invasion claim with lane-boundary crossing evidence if available in post-execution logs."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":46.14997863769531,"y":326.9700012207031,"z":0.29999998211860657,"pitch":0.0,"yaw":179.999755859375,"roll":0.0},"destination":{"x":60.10997772216797,"y":330.4599914550781,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":18,"rain":3,"puddle":0,"wind":9,"fog":0,"wetness":2,"angle":23,"altitude":84},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":59.223,"y":331.0,"z":1.5,"pitch":0.0,"yaw":18.019,"roll":0.0}}],"puddles":[{"index":0,"level":0.71,"location":{"x":37.563,"y":312.431,"z":0.0},"size":{"x":650.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.73,"location":{"x":50.849,"y":319.366,"z":0.0},"size":{"x":250.0,"y":250.0,"z":1000.0}},{"index":2,"level":0.16,"location":{"x":74.893,"y":331.0,"z":0.0},"size":{"x":650.0,"y":650.0,"z":1000.0}}]}}