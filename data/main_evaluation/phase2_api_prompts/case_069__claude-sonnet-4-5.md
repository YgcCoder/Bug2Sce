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
{"case_id":"case_069","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_069","fault_layer":"unknown","causal_explanation":["Dataset.xlsx labels collision=1 and lane_invasion=1, but error.json reports crash=false and lane_invasion=false. The collision topic shows impulse events starting at 28.455s with actor ID 0. Critical-window evidence s..."],"root_cause_pattern":"Conservative preservation pattern: ego encounters a nearby detected object (last count=1, classification=6, distance=11.225m) while moving at moderate speed (~5.46 m/s) before a collision event (per collision topic), with oracle label conflict (dataset vs. error.json) and vehicle_cmd-status mismatch present.","preservation_constraints":["The generated candidate should preserve a collision event detectable via the collision topic.","At least one detected object should be present near the ego route in the critical window before the collision.","Ego velocity should be non-zero (moderate speed, ~4-6 m/s) in the pre-collision window.","Post-execution validation must check for collision topic events, detected object presence, and ego speed profile.","Oracle consistency between dataset labels and error.json should be verified post-execution."],"uncertainty":["Dataset.xlsx reports collision=1 and lane_invasion=1, but error.json reports crash=false and lane_invasion=false; oracle conflict requires manual review.","vehicle_cmd is all zero while vehicle_status shows throttle and steering; command-status mismatch origin is unclear.","Evidence does not directly prove whether perception failed to track, planning failed to avoid, or actuation failed to execute commands.","Lane invasion label conflict is unresolved; no lane-boundary crossing evidence is provided.","Closest object classification=6 and actor_id=0 in collision topic; actor type and interaction geometry are not detailed."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Manual review is required to resolve the dataset vs. error.json oracle conflict before confident Phase 2 generation.","Post-execution validation must confirm collision topic impulse events, detected object presence, and ego speed profile.","Do not count a generated case as same-root-cause unless collision topic events and detected object proximity are preserved.","Investigate vehicle_cmd all-zero vs. vehicle_status activity mismatch in any reproduced scenario."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":86.0,"y":145.0,"z":0.29999998211860657,"pitch":0.0,"yaw":90.0,"roll":0.0},"destination":{"x":182.91,"y":198.76,"z":0.29999998211860657,"yaw":179.999755859375}},"weather":{"cloud":98,"rain":5,"puddle":8,"wind":25,"fog":12,"wetness":10,"angle":47,"altitude":76},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":8.76,"spawn":{"x":67.271,"y":159.74,"z":1.5,"pitch":0.0,"yaw":100.714,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":12.56,"spawn":{"x":67.068,"y":165.818,"z":1.5,"pitch":0.0,"yaw":275.254,"roll":0.0}}],"puddles":[]}}