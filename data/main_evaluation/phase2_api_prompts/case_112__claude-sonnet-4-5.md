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
{"case_id":"case_112","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_112","fault_layer":"unknown","causal_explanation":["The oracle confirms a collision at 24.67s. Critical-window evidence shows ego traveling at ~5.56 m/s with throttle applied and steering active. Detection and prediction topics show 1-6 objects present, with at least o..."],"root_cause_pattern":"Conservative preservation pattern: ego encounters nearby detected objects while traveling at moderate speed before collision, with vehicle_cmd showing all-zero commands despite vehicle_status showing active control, and module-level attribution remains uncertain.","preservation_constraints":["The generated candidate should preserve collision oracle symptom","Detected objects (1-6 count) should be present in the critical window before collision","Ego should be traveling at moderate speed (4-6 m/s range) before collision","Post-execution validation should check vehicle_cmd vs vehicle_status consistency and object detection presence"],"uncertainty":["Lane_invasion label conflict: dataset=1, error_json=0","vehicle_cmd all zero while vehicle_status shows active throttle and steering; cannot determine if planning, actuation, or simulator interface is at fault","Evidence shows objects detected and predicted but does not prove planning failure to avoid or actuation failure to execute","Cannot confirm whether lane invasion actually occurred"],"ready_for_phase2_generation":"yes","notes_for_validator":["Do not count a generated case as same-root-cause unless post-execution shows: (1) collision oracle, (2) detected objects in critical window, (3) moderate ego...","Check vehicle_cmd vs vehicle_status consistency in generated case; if mismatch persists, it may indicate simulator or interface issue rather than Autoware mo...","Lane_invasion label is uncertain; do not require lane_invasion=1 for preservation","Conservative pattern focuses on observable symptoms (collision, objects, speed) rather than unproven module failures"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":86.0,"y":145.0,"z":0.29999998211860657,"pitch":0.0,"yaw":90.0,"roll":0.0},"destination":{"x":182.91,"y":198.76,"z":0.29999998211860657,"yaw":179.999755859375}},"weather":{"cloud":94,"rain":14,"puddle":7,"wind":28,"fog":31,"wetness":23,"angle":59,"altitude":-16},"actors":[{"index":0,"type":"walker","nav_type":"autopilot","speed":2.32,"spawn":{"x":109.808,"y":152.81,"z":1.5,"pitch":0.0,"yaw":108.29,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":13.06,"spawn":{"x":80.262,"y":164.766,"z":1.5,"pitch":0.0,"yaw":70.365,"roll":0.0}}],"puddles":[]}}