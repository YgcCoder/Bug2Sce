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
{"case_id":"case_137","model_name":"ark-deepseek-r1-250528","phase1_output":{"case_id":"case_137","fault_layer":"unknown","causal_explanation":"The case is consistently labeled as a red light violation by both dataset and error.json. Critical window evidence does not confirm ego stop-line crossing on red or the relation between ego's route and the relevant red traffic light, and no module-level failure is directly proven by available evidence.","root_cause_pattern":"Conservative preservation pattern: A consistently labeled red light violation scenario in Town01 map with 3 actors and 1 puddle region, with no confirmed module-level root cause from available evidence.","preservation_constraints":["Preserve consistent red light violation labeling from dataset and error.json","Preserve ego's start and goal mission in Town01 map","Preserve 3 actors and 1 puddle region in the scenario","Preserve availability of traffic light topic data"],"uncertainty":["Route-light relation and stop-line crossing are not confirmed by available evidence","No critical window evidence directly attributes failure to a specific module or component","All sampled vehicle_cmd values are zero while vehicle_status shows non-zero velocity, creating an unresolved actuation behavior mismatch"],"ready_for_phase2_generation":"yes","notes_for_validator":["Validate that stop-line crossing and route-light relation are present after generation to confirm a genuine red light violation","Check if the vehicle_cmd/vehicle_status mismatch is preserved in the generated scenario during the critical window"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":110.0,"y":129.0,"z":1.0,"pitch":0.0,"yaw":180.0,"roll":0.0},"destination":{"x":113.0,"y":130.0,"z":0.0,"yaw":0.0}},"weather":{"cloud":93,"rain":69,"puddle":56,"wind":23,"fog":62,"wetness":40,"angle":250,"altitude":-13},"actors":[{"index":0,"type":"walker","nav_type":"immobile","speed":0.0,"spawn":{"x":115.731,"y":96.845,"z":1.5,"pitch":0.0,"yaw":195.958,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":2.19,"spawn":{"x":89.001,"y":120.439,"z":1.5,"pitch":0.0,"yaw":205.947,"roll":0.0}},{"index":2,"type":"walker","nav_type":"immobile","speed":0.0,"spawn":{"x":134.648,"y":150.18,"z":1.5,"pitch":0.0,"yaw":321.058,"roll":0.0}}],"puddles":[{"index":0,"level":0.45,"location":{"x":103.004,"y":121.025,"z":0.0},"size":{"x":650.0,"y":700.0,"z":1000.0}}]}}