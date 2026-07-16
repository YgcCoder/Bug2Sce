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
{"case_id":"case_024","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_024","fault_layer":"unknown","causal_explanation":"Oracle consistently confirms both a collision and a red light event. Pre-collision, vehicle_cmd has all zero control commands while vehicle_status records non-zero brake and decreasing ego speed, with a detected object 2.45m from ego. A red traffic light state is present late in the critical window, but route-light relation and stop-line crossing are unconfirmed. No specific Autoware module failure is directly proven.","root_cause_pattern":"Conservative preservation pattern: Ego exhibits both collision and red-light oracle symptoms, with all-zero control commands in /vehicle_cmd and non-zero brake in vehicle_status pre-collision, and a close detected object near ego before impact. Module-level fault attribution remains unknown.","preservation_constraints":["Preserve both collision and red-light oracle symptoms","Preserve all-zero control command values in vehicle_cmd during the pre-collision critical window","Preserve non-zero brake value in vehicle_status during the pre-collision critical window","Preserve a detected object within 3m of ego before collision","Presence of at least one red traffic light state in the late critical window"],"uncertainty":["Red-light route relation and stop-line crossing are not confirmed by evidence","Mismatch between all-zero vehicle_cmd and non-zero vehicle_status control means actuation attribution is uncertain","No critical-window evidence directly localizes fault to a specific Autoware module","Classification of the closest pre-collision detected object is unknown"],"ready_for_phase2_generation":"yes","notes_for_validator":["Verify both collision and red-light oracle symptoms are present in generated cases","Check that pre-collision vehicle_cmd is all zero and vehicle_status has non-zero brake in generated cases","Do not confirm same-root-cause status without matching the pre-collision command mismatch condition"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":86.0,"y":145.0,"z":0.29999998211860657,"pitch":0.0,"yaw":90.0,"roll":0.0},"destination":{"x":182.91,"y":198.76,"z":0.29999998211860657,"yaw":179.999755859375}},"weather":{"cloud":100,"rain":8,"puddle":10,"wind":22,"fog":0,"wetness":3,"angle":26,"altitude":85},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":7.03,"spawn":{"x":104.973,"y":144.182,"z":1.5,"pitch":0.0,"yaw":108.846,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":3.01,"spawn":{"x":91.918,"y":129.675,"z":1.5,"pitch":0.0,"yaw":89.829,"roll":0.0}}],"puddles":[{"index":0,"level":0.54,"location":{"x":94.397,"y":120.413,"z":0.0},"size":{"x":350.0,"y":300.0,"z":1000.0}}]}}