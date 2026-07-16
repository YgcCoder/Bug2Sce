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
{"case_id":"case_001","model_name":"gemini-2.5-pro","phase1_output":{"case_id":"case_001","fault_layer":"unknown","causal_explanation":["The ego vehicle collides with a detected actor while the planner sends no commands, but the vehicle's status shows independent movement and braking."],"root_cause_pattern":"Planner sends zero-value commands despite a nearby detected object, preceding a collision.","preservation_constraints":["Planner must publish zero-value vehicle commands.","Perception must detect at least one object.","A collision with an actor must occur."],"uncertainty":["The discrepancy between zero vehicle_cmd and non-zero vehicle_status makes fault attribution uncertain.","It is unknown why the planner sent zero commands."],"ready_for_phase2_generation":"yes","notes_for_validator":["Key anomaly: vehicle_cmd is all zeros.","vehicle_status shows movement/braking, creating a conflict.","Fault attribution is uncertain due to this conflict."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":104.8687973022461,"y":59.99010467529297,"z":0.29999998211860657,"pitch":0.0,"yaw":0.0,"roll":0.0},"destination":{"x":392.4700012207031,"y":105.38999938964844,"z":0.29999998211860657,"yaw":90.00004577636719}},"weather":{"cloud":25,"rain":5,"puddle":8,"wind":45,"fog":0,"wetness":15,"angle":220,"altitude":55},"actors":[{"index":0,"type":"vehicle","nav_type":"linear","speed":8.0,"spawn":{"x":116.0,"y":62.0,"z":1.5,"pitch":0.0,"yaw":0.0,"roll":0.0}}],"puddles":[{"index":0,"level":0.65,"location":{"x":111.0,"y":60.0,"z":0.0},"size":{"x":500.0,"y":500.0,"z":1000.0}}]}}