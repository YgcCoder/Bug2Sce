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
{"case_id":"case_137","model_name":"gpt-5.1","phase1_output":{"case_id":"case_137","fault_layer":"unknown","causal_explanation":["The oracle reports a red-light violation, and traffic light states are available, but the summaries do not confirm whether the ego route intersected a red signal or whether any stop line was crossed. Planning and cont..."],"root_cause_pattern":"Conservative preservation pattern: a red-light violation is flagged by the oracle in a scenario where traffic light states are published and the ego vehicle is moving under an active mission, but the route–signal relation and stop-line crossing are not directly evidenced, leaving the internal cause within the Autoware stack or simulator unknown.","preservation_constraints":["The generated candidate should preserve the oracle red-light violation symptom (error_json red=true).","Traffic light state information should be available on the traffic_lights topic during the critical window.","The ego vehicle should be executing a mission and show non-zero velocity in vehicle_status or odometry before the reported violation.","The route–traffic-light relation and stop-line crossing should remain unconfirmed by high-level summaries (i.e., not explicitly established).","Final waypoints and vehicle_cmd topics should remain present throughout the critical window."],"uncertainty":["Route–traffic-light relation is marked unknown; no direct evidence that the ego path intersected a specific red signal.","Stop-line crossing is unconfirmed by the summaries; actual legality of the ego trajectory relative to the signal cannot be verified.","Module-level attribution (perception vs. planning vs. actuation vs. simulator) is not supported by the available high-level data.","Vehicle_cmd fields are all zero while vehicle_status shows motion; without lower-level details this mismatch cannot be interpreted as a controller or simulator fault."],"ready_for_phase2_generation":"yes","notes_for_validator":["Post-execution validation must confirm that error_json (or equivalent oracle) reports a red-light violation and not other primary failures (collision, stuck,...","Check that the traffic_lights topic is present with at least one red state sample before or around the violation time.","Verify that ego odometry or vehicle_status shows movement prior to the violation, confirming an active driving scenario.","Do not attempt to infer or enforce a specific route–signal or stop-line relationship in validation; it is sufficient that the oracle flags a red violation wh..."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":110.0,"y":129.0,"z":1.0,"pitch":0.0,"yaw":180.0,"roll":0.0},"destination":{"x":113.0,"y":130.0,"z":0.0,"yaw":0.0}},"weather":{"cloud":93,"rain":69,"puddle":56,"wind":23,"fog":62,"wetness":40,"angle":250,"altitude":-13},"actors":[{"index":0,"type":"walker","nav_type":"immobile","speed":0.0,"spawn":{"x":115.731,"y":96.845,"z":1.5,"pitch":0.0,"yaw":195.958,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":2.19,"spawn":{"x":89.001,"y":120.439,"z":1.5,"pitch":0.0,"yaw":205.947,"roll":0.0}},{"index":2,"type":"walker","nav_type":"immobile","speed":0.0,"spawn":{"x":134.648,"y":150.18,"z":1.5,"pitch":0.0,"yaw":321.058,"roll":0.0}}],"puddles":[{"index":0,"level":0.45,"location":{"x":103.004,"y":121.025,"z":0.0},"size":{"x":650.0,"y":700.0,"z":1000.0}}]}}