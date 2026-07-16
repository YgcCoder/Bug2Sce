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
{"case_id":"case_118","model_name":"gpt-5.1","phase1_output":{"case_id":"case_118","fault_layer":"unknown","causal_explanation":"A collision occurs around 66.41s while the ego is moving at roughly 5 m/s, with collision oracle data confirming impact but listing only actor id 0 (ego) as sampled. Object, prediction, waypoint, and traffic-light topics are present, yet the available summaries do not reveal which entity is struck or how lane boundaries or a relevant red signal relate to the ego path. Vehicle_status shows nonzero throttle and increasing speed before impact, while vehicle_cmd remains all zeros, indicating a mismatch between high-level commands and low-level status but not clearly localizing the fault to any specific Autoware layer or to the simulator. The dataset label indicates collision + lane_invasion + red-light violation, whereas error.json reports collision + red-light only, so the lane-invasion aspect is especially uncertain.","root_cause_pattern":"Conservative preservation pattern: the ego vehicle is in motion and experiences a collision under nontrivial throttle without evidence of braking, in a scenario where traffic-light and object information are available but module-level responsibility and lane-invasion status remain unknown.","preservation_constraints":["The generated candidate should preserve a collision of the ego vehicle as the oracle symptom.","The ego should be moving (nonzero speed) shortly before the collision rather than already stopped.","Throttle or propulsion in vehicle_status should be nonzero before impact, with no clear evidence of braking in the critical window.","Perception-related topics (detected objects and prediction objects) and planning waypoints should be available before the collision.","Traffic-light topic data should be available at some point before the failure, even if the precise route-light relation is unknown."],"uncertainty":["Dataset.xlsx reports lane_invasion=1 and group=C+L+R, but error.json reports lane_invasion=false and group=C+R; the true presence of lane invasion is unclear.","The collision oracle samples only actor id 0, so the identity and position of the collision counterpart (if any) are not explicit.","The relationship between the ego route and nearby traffic lights or stop lines is not confirmed; red-light violation mechanism is unknown.","The persistent zero vehicle_cmd alongside nonzero vehicle_status throttle and motion could stem from controller, interface, or simulator behavior; the responsible layer cannot be determined.","No direct evidence ties the collision to a perception, planning, or actuation defect rather than scenario configuration or simulation artifacts."],"ready_for_phase2_generation":"yes","notes_for_validator":["Post-execution, confirm that the ego collision oracle event occurs and that ego velocity is nonzero immediately before impact.","Verify that in the critical window vehicle_status shows nonzero throttle and zero brake, without a pre-collision speed drop indicative of braking.","Check that vehicle_cmd remains zero (or effectively zero) for accel_cmd, brake_cmd, and steer_cmd in the critical window, preserving the command-status mismatch pattern.","Ensure that perception (detection and prediction objects), planning (final_waypoints), and traffic_lights topics are present and populated prior to the collision.","Do not require lane-invasion or a proven red-light mechanism for same-root-cause matching, given the current label conflict and missing route-light linkage."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":104.8687973022461,"y":59.99010467529297,"z":0.29999998211860657,"pitch":0.0,"yaw":0.0,"roll":0.0},"destination":{"x":392.4700012207031,"y":105.38999938964844,"z":0.29999998211860657,"yaw":90.00004577636719}},"weather":{"cloud":12,"rain":24,"puddle":39,"wind":17,"fog":46,"wetness":45,"angle":269,"altitude":38},"actors":[],"puddles":[{"index":0,"level":0.16,"location":{"x":130.218,"y":66.75,"z":0.0},"size":{"x":500.0,"y":500.0,"z":1000.0}},{"index":1,"level":0.93,"location":{"x":122.54,"y":39.454,"z":0.0},"size":{"x":300.0,"y":300.0,"z":1000.0}},{"index":2,"level":0.41,"location":{"x":113.367,"y":66.085,"z":0.0},"size":{"x":500.0,"y":500.0,"z":1000.0}}]}}