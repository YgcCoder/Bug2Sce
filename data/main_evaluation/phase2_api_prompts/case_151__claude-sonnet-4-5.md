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
{"case_id":"case_151","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_151","fault_layer":"unknown","causal_explanation":["Dataset.xlsx labels this case as stuck+lane_invasion, but error.json reports neither stuck nor lane_invasion (only goal-distance=58.4m). Critical-window evidence shows vehicle_cmd is all zero (steer, accel, brake all..."],"root_cause_pattern":"Conservative preservation pattern: vehicle_cmd remains all zero while vehicle_status shows actuation and movement, final waypoints are available, and oracle labels conflict between dataset and error.json.","preservation_constraints":["Generated candidate should preserve vehicle_cmd all zero throughout the trace.","Vehicle_status should show non-zero actuation (throttle, brake, or steer) and non-zero movement in the final window.","Final waypoints should be present and non-blocked.","Post-execution validation must check vehicle_cmd vs vehicle_status mismatch and oracle label consistency."],"uncertainty":["Dataset.xlsx labels stuck=1 and lane_invasion=1, but error.json reports stuck=0 and lane_invasion=0; oracle consistency is dataset_only.","vehicle_cmd is all zero but vehicle_status shows non-zero throttle, brake, steer, and movement; the cause of this mismatch is not directly supported by the evidence.","No direct evidence of perception, planning, or actuation module failure; the zero vehicle_cmd may indicate a planning or actuation issue, but module-level attribution is uncertain.","Lane invasion label is present in dataset but not confirmed by error.json or lane-boundary crossing evidence."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Do not count a generated case as same-root-cause unless post-execution evidence shows vehicle_cmd all zero, vehicle_status non-zero actuation, and final wayp...","Manual review is required to resolve the oracle label conflict between dataset and error.json before confirming the root cause.","Check whether the vehicle_cmd vs vehicle_status mismatch is a simulator artifact, actuation layer issue, or planning layer issue.","Verify lane_invasion label with lane-boundary crossing evidence if available in post-execution validation."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":46.14997863769531,"y":326.9700012207031,"z":0.29999998211860657,"pitch":0.0,"yaw":179.999755859375,"roll":0.0},"destination":{"x":60.10997772216797,"y":330.4599914550781,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":61,"rain":10,"puddle":19,"wind":27,"fog":27,"wetness":69,"angle":260,"altitude":2},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":9.1,"spawn":{"x":17.198,"y":331.0,"z":1.5,"pitch":0.0,"yaw":359.222,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":0.79,"spawn":{"x":39.707,"y":325.715,"z":1.5,"pitch":0.0,"yaw":191.333,"roll":0.0}}],"puddles":[{"index":0,"level":0.44,"location":{"x":45.122,"y":326.855,"z":0.0},"size":{"x":500.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.75,"location":{"x":45.567,"y":321.576,"z":0.0},"size":{"x":800.0,"y":800.0,"z":1000.0}}]}}