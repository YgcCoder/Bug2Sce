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
{"case_id":"case_001","model_name":"gpt-5.1","phase1_output":{"case_id":"case_001","fault_layer":"unknown","causal_explanation":"A collision occurs around 21.599 s with a nearby actor (~4.5 m away) after the ego has moved slightly and then is effectively at rest (last pre-collision speed 0 m/s). Object detection, prediction, and final waypoints are continuously available, with one detected object and multiple predicted objects, and the planner reports an unblocked lane with 101 waypoints where the closest object to the path is at zero reported distance just before collision. Throughout the critical window, vehicle_cmd remains all zeros while vehicle_status indicates nonzero throttle earlier in the run and some braking before the crash, making the control chain behavior uncertain. Module-level responsibility (perception vs planning vs control vs simulator) for ending in a colliding pose with a nearby actor cannot be determined from the available summaries.","root_cause_pattern":"Conservative preservation pattern: ego ends up in a colliding pose with a nearby actor while perception outputs at least one object and the planner provides non-blocked final waypoints, but the available evidence does not uniquely localize the failure within the Autoware stack.","preservation_constraints":["The generated candidate should preserve the same oracle symptom: a collision event is reported for the ego vehicle.","At least one non-ego actor should be present within a few meters of the ego before the collision according to the simulator objects or collision topics.","Perception object and prediction topics should be available before the collision and report at least one object.","Planning final_waypoints should be available before the collision, with a nonzero number of waypoints and no blocked flag in the last pre-collision message.","Vehicle_cmd should remain zero (or effectively zero) over the critical window while vehicle_status indicates that the ego is not simply in an uninitialized static state."],"uncertainty":["The evidence does not show detailed planner decision logic or internal costmaps, so it is unclear why the final waypoints remain unblocked when the closest object distance is reported as zero.","Perception association quality and classification correctness for the colliding actor cannot be verified from counts and label samples alone.","Vehicle_cmd remains zero while vehicle_status shows movement and some braking, making it unclear whether the controller, interface configuration, or simulator timing caused the ultimate colliding pose.","The relative motion of the other actor (moving vs parked) is not specified in the summaries, so the interaction dynamics are unknown."],"ready_for_phase2_generation":"yes","notes_for_validator":["Post-execution logs for generated candidates should confirm that a collision event is raised for the ego with a non-ego actor present in the collision topic.","Check that detection and prediction topics report at least one object in the critical window before collision and that final_waypoints remains unblocked with nonzero waypoint count immediately before the crash.","Verify that the nearest pre-collision waypoint message still reports closest_object_distance approximately zero or otherwise indicates the planned path passes through or extremely near a non-ego actor.","Confirm that vehicle_cmd remains effectively zero (no meaningful acceleration or braking commands) while vehicle_status indicates the ego is not trivially static throughout the entire simulation.","Do not attribute the reproduced failure specifically to perception, planning, or actuation unless additional detailed logs (e.g., planner internals, control interface diagnostics) provide stronger evidence."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":104.8687973022461,"y":59.99010467529297,"z":0.29999998211860657,"pitch":0.0,"yaw":0.0,"roll":0.0},"destination":{"x":392.4700012207031,"y":105.38999938964844,"z":0.29999998211860657,"yaw":90.00004577636719}},"weather":{"cloud":25,"rain":5,"puddle":8,"wind":45,"fog":0,"wetness":15,"angle":220,"altitude":55},"actors":[{"index":0,"type":"vehicle","nav_type":"linear","speed":8.0,"spawn":{"x":116.0,"y":62.0,"z":1.5,"pitch":0.0,"yaw":0.0,"roll":0.0}}],"puddles":[{"index":0,"level":0.65,"location":{"x":111.0,"y":60.0,"z":0.0},"size":{"x":500.0,"y":500.0,"z":1000.0}}]}}