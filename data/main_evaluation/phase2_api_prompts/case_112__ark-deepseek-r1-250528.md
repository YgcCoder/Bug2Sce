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
{"case_id":"case_112","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_112","fault_layer":"unknown","causal_explanation":"Both dataset and error.json confirm a collision occurred, but labels conflict for lane invasion. All actuation commands in vehicle_cmd are zero in the pre-collision window, but the ego vehicle maintains ~5.5 m/s speed with non-zero throttle and no braking per vehicle_status. No blocked waypoints are reported by planning before collision, and the closest detected object is ~10m from ego. No direct evidence localizes failure to a specific module.","root_cause_pattern":"Conservative pattern: a collision occurs when all output actuation commands from the Autoware control pipeline are zero, while the ego vehicle continues moving forward with no braking before the collision, with conflicting lane invasion labels between dataset and error.json.","preservation_constraints":["Preserve the confirmed collision symptom agreed by both labels","Preserve the condition that all vehicle_cmd commands are zero in the pre-collision critical window","Preserve the condition that ego maintains positive non-decreasing speed with no braking reported by vehicle_status before collision","Preserve that planning reports no blocked waypoints before collision","Preserve the lane invasion label conflict for post-generation validation"],"uncertainty":["Label conflict between dataset and error.json for lane invasion and failure group","No direct evidence of internal module failure to localize fault to a specific layer","Mismatch between all-zero vehicle_cmd and moving ego cannot confirm actuation failure per rules","Raw sensor data was not decoded so sensing/perception internal behavior cannot be verified"],"ready_for_phase2_generation":"yes","notes_for_validator":["Verify that the generated case preserves the all-zero vehicle_cmd and non-zero moving ego condition before collision","Post-generation validation should check for lane invasion to resolve the existing label conflict"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":86.0,"y":145.0,"z":0.29999998211860657,"pitch":0.0,"yaw":90.0,"roll":0.0},"destination":{"x":182.91,"y":198.76,"z":0.29999998211860657,"yaw":179.999755859375}},"weather":{"cloud":94,"rain":14,"puddle":7,"wind":28,"fog":31,"wetness":23,"angle":59,"altitude":-16},"actors":[{"index":0,"type":"walker","nav_type":"autopilot","speed":2.32,"spawn":{"x":109.808,"y":152.81,"z":1.5,"pitch":0.0,"yaw":108.29,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":13.06,"spawn":{"x":80.262,"y":164.766,"z":1.5,"pitch":0.0,"yaw":70.365,"roll":0.0}}],"puddles":[]}}