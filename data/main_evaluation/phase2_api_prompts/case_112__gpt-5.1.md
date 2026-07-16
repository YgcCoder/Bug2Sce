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
{"case_id":"case_112","model_name":"gpt-5.1","phase1_output":{"case_id":"case_112","fault_layer":"unknown","causal_explanation":"A collision is confirmed near 24.67s while ego is moving at about 5.6 m/s with nonzero throttle and zero brake, even though vehicle_cmd reports zero accel/brake/steer and zero target speed throughout. Perception and prediction report at least one object before the collision, and the planner continuously provides a full set of unblocked final waypoints (101 points) with a closest_object_distance field equal to 0.0 at the last pre-collision row, yet there is no evidence of braking or speed reduction in the collision window. Module-level attribution is uncertain because the data only shows the symptom (collision with continued motion and no braking) plus an inconsistency between vehicle_status and vehicle_cmd, without direct internal-failure indicators for perception, planning, or control.","root_cause_pattern":"Conservative preservation pattern: ego is in motion and experiences a collision while valid final waypoints are available and no braking is applied during the critical window, with perception/prediction objects present and a mismatch between vehicle_cmd (all zeros) and vehicle_status (nonzero speed and throttle), leaving the precise failing module unknown.","preservation_constraints":["The generated candidate should preserve the same oracle symptom: a collision event in the critical window.","Ego should have nonzero speed in the seconds immediately before the collision, with no significant braking reported in vehicle_status or vehicle_cmd.","Final waypoints should be continuously available before the collision with a full set of waypoints and no blocked flags.","Perception and prediction object topics should be present in the critical window with at least one object detected/predicted near the time of collision.","A discrepancy between zeroed vehicle_cmd signals and nonzero ego motion/throttle in vehicle_status should be preserved or replaced with a similarly ambiguous actuation-command situation."],"uncertainty":["Dataset.xlsx indicates lane_invasion=1 and group=C+L, but error.json shows no lane_invasion and group=C, so lane invasion involvement is not confirmed.","The closest_available_object_info reports a closest_object_distance of 0.0 at the last pre-collision waypoint row, but the semantic meaning of this field is unclear (it may be a sentinel rather than a true distance).","Vehicle_cmd signals are all zero while vehicle_status shows nonzero throttle and ego speed; the controller behavior and responsibility are ambiguous.","Available summaries do not identify which specific module (perception, planning, or actuation) caused the collision.","Simulator-level details of the colliding actor (type, lane position, precise pose) are not fully specified in the summary."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Verify post-execution that the oracle reports at least one collision event in a late window analogous to the original critical window.","Check that ego speed is nonzero and does not significantly decrease in the few seconds before collision, and that reported brake signals (status and command) remain near zero.","Confirm that final_waypoints are available and unblocked in the seconds before collision with a consistent waypoint count similar to the original case.","Ensure that detection and prediction object topics are populated near the collision time, indicating that some perception/prediction outputs exist.","Treat any lane_invasion outcome as optional for same-root-cause grouping due to conflicting lane_invasion labels in the original evidence.","Do not infer specific module blame (e.g., perception vs. planning vs. actuation) solely from the presence of objects and waypoints; focus instead on preserving the pattern of collision with motion and lack of braking under active planning and perception topics."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":86.0,"y":145.0,"z":0.29999998211860657,"pitch":0.0,"yaw":90.0,"roll":0.0},"destination":{"x":182.91,"y":198.76,"z":0.29999998211860657,"yaw":179.999755859375}},"weather":{"cloud":94,"rain":14,"puddle":7,"wind":28,"fog":31,"wetness":23,"angle":59,"altitude":-16},"actors":[{"index":0,"type":"walker","nav_type":"autopilot","speed":2.32,"spawn":{"x":109.808,"y":152.81,"z":1.5,"pitch":0.0,"yaw":108.29,"roll":0.0}},{"index":1,"type":"vehicle","nav_type":"linear","speed":13.06,"spawn":{"x":80.262,"y":164.766,"z":1.5,"pitch":0.0,"yaw":70.365,"roll":0.0}}],"puddles":[]}}