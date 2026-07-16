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
{"case_id":"case_001","model_name":"ark-doubao-seed-2.0-lite-260215","phase1_output":{"case_id":"case_001","fault_layer":"unknown","causal_explanation":"A confirmed collision occurred. Ego speed decreased to zero immediately before collision, perception detected at least one actor, planning reported no blocked final waypoints, but available evidence cannot confirm which Autoware module caused the failure.","root_cause_pattern":"Conservative preservation pattern: Ego collides with a detected actor when all final waypoints are marked as unblocked before collision, while module-level fault attribution remains unconfirmed.","preservation_constraints":["Collision with one other actor is the required oracle outcome","The collision actor is detected by perception in the pre-collision critical window","No final waypoints are marked as blocked by planning before collision","All vehicle command values are zero in the final pre-collision window"],"uncertainty":["Direct planner decision logs are not available to confirm planning fault","No evidence proves the collision actor was correctly associated by perception","Mismatch between all-zero vehicle_cmd and non-zero vehicle_status brake leaves controller behavior uncertain"],"ready_for_phase2_generation":"yes","notes_for_validator":["Confirm the collision actor is detected by perception pre-collision for a valid same-root-cause case","Check that planning reports no blocked waypoints before collision to meet preservation constraints"]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":104.8687973022461,"y":59.99010467529297,"z":0.29999998211860657,"pitch":0.0,"yaw":0.0,"roll":0.0},"destination":{"x":392.4700012207031,"y":105.38999938964844,"z":0.29999998211860657,"yaw":90.00004577636719}},"weather":{"cloud":25,"rain":5,"puddle":8,"wind":45,"fog":0,"wetness":15,"angle":220,"altitude":55},"actors":[{"index":0,"type":"vehicle","nav_type":"linear","speed":8.0,"spawn":{"x":116.0,"y":62.0,"z":1.5,"pitch":0.0,"yaw":0.0,"roll":0.0}}],"puddles":[{"index":0,"level":0.65,"location":{"x":111.0,"y":60.0,"z":0.0},"size":{"x":500.0,"y":500.0,"z":1000.0}}]}}