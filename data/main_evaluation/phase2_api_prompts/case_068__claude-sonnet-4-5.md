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
{"case_id":"case_068","model_name":"claude-sonnet-4-5","phase1_output":{"case_id":"case_068","fault_layer":"unknown","causal_explanation":["The oracle confirms a red-light violation. Critical-window evidence shows traffic light states are available (36 lights, states 0/1/2 sampled), final waypoints exist with stop_line_id=4294967295, and vehicle_status sh..."],"root_cause_pattern":"Conservative preservation pattern: ego proceeds through a scenario with traffic lights present while a red-light violation is recorded, but route-light relation and stop-line crossing are not confirmed by evidence.","preservation_constraints":["The generated candidate should preserve the red-light violation oracle symptom.","Traffic lights should be present in the scenario.","Ego should exhibit movement (non-zero velocity) in the critical window.","Post-execution validation should check for red-light violation, traffic light presence on route, and ego velocity profile."],"uncertainty":["Route-light relation is not confirmed; which traffic light was violated is unknown.","Stop-line crossing is not confirmed by evidence.","Module-level attribution (perception, planning, actuation) is not directly supported by critical-window evidence.","vehicle_cmd shows all-zero commands while vehicle_status shows movement, creating actuation uncertainty."],"ready_for_phase2_generation":"yes","notes_for_validator":["Do not count a generated case as same-root-cause unless post-execution confirms red-light violation and traffic light presence on ego route.","Verify that ego exhibits non-zero velocity in the critical window.","Check whether the generated scenario provides route-light relation evidence that was missing in the original case.","Do not assume planning or actuation fault without direct evidence of stop-line crossing or command failure."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":104.8687973022461,"y":59.99010467529297,"z":0.29999998211860657,"pitch":0.0,"yaw":0.0,"roll":0.0},"destination":{"x":392.4700012207031,"y":105.38999938964844,"z":0.29999998211860657,"yaw":90.00004577636719}},"weather":{"cloud":13,"rain":10,"puddle":13,"wind":71,"fog":19,"wetness":26,"angle":199,"altitude":29},"actors":[{"index":0,"type":"vehicle","nav_type":"immobile","speed":0.0,"spawn":{"x":93.216,"y":57.452,"z":1.5,"pitch":0.0,"yaw":300.718,"roll":0.0}}],"puddles":[]}}