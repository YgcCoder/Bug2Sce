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
{"case_id":"case_147","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_147","fault_layer":"unknown","causal_explanation":"Both dataset and error.json confirm a collision occurred, but disagree on the presence of lane invasion. All vehicle_cmd control commands are zero in the pre-collision window, while vehicle_status shows non-zero throttle and ego maintains ~3.45 m/s forward speed with no braking. No direct evidence localizes the failure to a specific Autoware module.","root_cause_pattern":"Conservative pattern: Ego vehicle experiences a collision with a nearby actor when all issued vehicle_cmd control outputs are zero, while ego maintains non-zero forward speed and no braking command is issued before collision.","preservation_constraints":["Preserve the confirmed collision oracle symptom","All vehicle_cmd control commands (accel, brake, steer) are zero in the pre-collision critical window","Ego maintains non-zero forward speed in the pre-collision critical window","No non-zero brake command is issued before collision","At least one actor is present within 4 meters of ego before collision"],"uncertainty":["Dataset and error.json conflict on lane invasion label: dataset=1, error_json=0","All vehicle_cmd are zero but vehicle_status shows non-zero throttle and movement, so controller behavior cannot be confirmed","No direct critical-window evidence supports module-level failure attribution"],"ready_for_phase2_generation":"yes","notes_for_validator":["Resolve lane invasion label conflict manually before classifying generated cases","Verify pre-collision zero vehicle_cmd and non-zero ego velocity to confirm same-root-cause match"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":46.14997863769531,"y":326.9700012207031,"z":0.29999998211860657,"pitch":0.0,"yaw":179.999755859375,"roll":0.0},"destination":{"x":60.10997772216797,"y":330.4599914550781,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":69,"rain":0,"puddle":19,"wind":17,"fog":70,"wetness":26,"angle":92,"altitude":2},"actors":[{"index":0,"type":"walker","nav_type":"linear","speed":2.84,"spawn":{"x":61.23,"y":331.0,"z":1.5,"pitch":0.0,"yaw":303.518,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":1.53,"spawn":{"x":39.117,"y":331.0,"z":1.5,"pitch":0.0,"yaw":5.655,"roll":0.0}}],"puddles":[]}}