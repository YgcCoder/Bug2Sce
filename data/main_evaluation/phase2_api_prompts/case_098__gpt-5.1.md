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
{"case_id":"case_098","model_name":"gpt-5.1","phase1_output":{"case_id":"case_098","fault_layer":"unknown","causal_explanation":"The oracle reports a collision with another actor at ~29.09 s. In the preceding 5 s window, Autoware has active sensing, detection, prediction, lane and final waypoints, and a nearby object (~4 m) is available. Planning reports 101 final waypoints with no blocked flags and closest_object_distance=0.0 at the last pre-collision row, while vehicle_cmd remains zero throughout the run, yet a separate collision_window summary reports nonzero throttle and ego speed before collision. This conflicting actuation/kinematics information prevents clear localization of the failure mechanism; the available evidence only confirms that the ego and a close actor come into contact without clear braking or a validated control command history.","root_cause_pattern":"Conservative preservation pattern: a collision occurs while a nearby actor is present within a few meters of the ego and planning outputs non-blocked final waypoints up to the critical window, under uncertain and internally inconsistent actuation/vehicle-status evidence.","preservation_constraints":["The generated case should preserve a collision oracle event between the ego and at least one other actor.","At least one non-ego actor should be present within a short distance (on the order of a few meters) of the ego shortly before the collision.","Final waypoints should be available and non-null in the critical window leading up to the collision.","Perception object and prediction topics should contain at least one object in the critical window before the collision.","Actuation or vehicle-status evidence may remain internally inconsistent (e.g., zero commands with nonzero reported motion) so that module attribution stays uncertain."],"uncertainty":["Trace_summary_compact vehicle_status statistics show zero velocity and zero throttle over the sampled interval, while the collision_window summary reports nonzero ego speed and throttle before collision, making the actual ego motion and control history unclear.","The mechanism by which the ego and the nearby actor come into contact (e.g., which moved into whom, or whether the ego was nominally stopped) is not observable from the summarized evidence.","The planning closest_object_distance and closest_object_velocity being zero in the last pre-collision waypoint row may reflect missing or default values rather than a confirmed perceived collision course.","The available topics confirm presence of detection and prediction outputs, but do not prove whether the colliding actor was correctly perceived or predicted.","No explicit stop-line or traffic-rule context is provided for this collision, limiting interpretation of the scenario semantics."],"ready_for_phase2_generation":"yes","notes_for_validator":["Post-execution, verify that the oracle logs a collision event involving the ego and a non-ego actor, not just minor contacts or near-misses.","Check that at least one non-ego actor is within a few meters of the ego shortly before collision using /carla/objects or equivalent ground-truth topics.","Confirm that final_waypoints remain available and structurally valid (non-empty, similar count) up to the critical window preceding the collision.","Verify that perception and prediction topics contain at least one object in the critical window; do not require that the specific colliding actor be conclusively matched to these topics, as that is not guaranteed by the pattern.","Do not attribute the reproduced failure to a specific Autoware layer unless additional run-specific evidence clarifies the control and motion inconsistencies observed here."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"pitch":0.0,"yaw":-89.99993896484375,"roll":0.0},"destination":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"yaw":-9.1552734375e-05}},"weather":{"cloud":15,"rain":4,"puddle":3,"wind":13,"fog":2,"wetness":1,"angle":268,"altitude":66},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":13.58,"spawn":{"x":339.675,"y":97.818,"z":1.5,"pitch":0.0,"yaw":1.063,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":3.78,"spawn":{"x":339.455,"y":109.061,"z":1.5,"pitch":0.0,"yaw":352.555,"roll":0.0}}],"puddles":[{"index":0,"level":0.05,"location":{"x":336.857,"y":124.696,"z":0.0},"size":{"x":500.0,"y":300.0,"z":1000.0}},{"index":1,"level":0.55,"location":{"x":328.699,"y":118.075,"z":0.0},"size":{"x":300.0,"y":300.0,"z":1000.0}}]}}