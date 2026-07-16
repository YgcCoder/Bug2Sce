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
{"case_id":"case_024","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_024","fault_layer":"unknown","causal_explanation":"The oracle consistently confirms both a collision and a red-light event. In the pre-collision critical window, all vehicle_cmd output is zero while vehicle_status records non-zero braking, a nearby object 2.45m from ego is detected, and a red traffic light state is present. No specific module failure is directly proven by available evidence.","root_cause_pattern":"Conservative candidate mechanism: Ego experiences a collision when all actuation commands from the pipeline are zero in the pre-collision window, with a nearby actor and a red traffic light present in the scenario.","preservation_constraints":["Preserve the consistent oracle label of collision plus red-light event","All vehicle_cmd output must be zero in the pre-collision critical window","A nearby actor must be present within 3 meters of ego before collision","At least one red traffic light state must exist in the critical window"],"uncertainty":["Mismatch between all-zero vehicle_cmd and non-zero brake in vehicle_status makes actuation controller behavior uncertain","Route-light relation and stop-line crossing for red-light violation are unconfirmed","No direct evidence localizes failure to a specific Autoware module","Red-light violation timestamp is unknown"],"ready_for_phase2_generation":"yes","notes_for_validator":["Verify zero vehicle_cmd output in the pre-collision window of generated cases","Confirm both collision and red-light events are present in oracle output","Check that the core mismatch between vehicle_cmd and vehicle_status braking is preserved"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":86.0,"y":145.0,"z":0.29999998211860657,"pitch":0.0,"yaw":90.0,"roll":0.0},"destination":{"x":182.91,"y":198.76,"z":0.29999998211860657,"yaw":179.999755859375}},"weather":{"cloud":100,"rain":8,"puddle":10,"wind":22,"fog":0,"wetness":3,"angle":26,"altitude":85},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":7.03,"spawn":{"x":104.973,"y":144.182,"z":1.5,"pitch":0.0,"yaw":108.846,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":3.01,"spawn":{"x":91.918,"y":129.675,"z":1.5,"pitch":0.0,"yaw":89.829,"roll":0.0}}],"puddles":[{"index":0,"level":0.54,"location":{"x":94.397,"y":120.413,"z":0.0},"size":{"x":350.0,"y":300.0,"z":1000.0}}]}}