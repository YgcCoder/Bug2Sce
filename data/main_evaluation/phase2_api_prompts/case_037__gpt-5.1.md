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
{"case_id":"case_037","model_name":"gpt-5.1","phase1_output":{"case_id":"case_037","fault_layer":"unknown","causal_explanation":"Oracle collision messages occur around the dataset collision timestamp while error.json reports only a red-light violation. The ego shows essentially zero motion over the drive and planning consistently publishes full waypoint sets with no blocked flags. A nearby object is reported very close to the ego at the collision time, but there is no direct evidence of how the ego and actor paths interacted, whether any lane boundary was crossed, or whether the ego actually crossed a red-light stop line. Autoware command topics are all zero while simulator vehicle_status reports small nonzero velocities in the collision window, making controller and actuation behavior uncertain.","root_cause_pattern":"Conservative preservation pattern: a red-light oracle violation is recorded while a close-proximity collision oracle event with a nearby actor occurs under heavy-rain conditions, with Autoware planning publishing non-blocked waypoints and actuation command topics remaining at zero, but the precise fault layer behind the collision, lane invasion, and red-light behaviors remains unknown.","preservation_constraints":["The generated candidate should preserve an oracle red-light violation event in error.json.","A collision oracle topic should report at least one impulse event near the end of the run, even if error_json does not flag a crash.","At least one non-ego actor should be present and come within a few meters of the ego near the failure time.","Final waypoints should remain available and not be marked blocked in the critical window before the failure.","vehicle_cmd messages should remain near-zero for acceleration, brake, steer, and target speed over the run."],"uncertainty":["Dataset.xlsx reports collision and lane_invasion while error.json does not, so collision and lane-invasion labels are not confirmed ground truth.","Route-to-traffic-light relation and stop-line crossing for the red-light violation are unknown from the summaries.","The precise interaction geometry between ego and the nearby actor at collision time is not available.","Autoware module-level responsibility (perception vs planning vs actuation) cannot be localized from the available topics.","vehicle_status shows nonzero motion and braking within the collision window while vehicle_cmd remains zero, making controller and actuation behavior uncertain."],"ready_for_phase2_generation":"uncertain","notes_for_validator":["Treat collision and lane_invasion as uncertain due to disagreement between Dataset.xlsx and error.json; only the red-light error_json event is confirmed.","Post-execution validation should check that error.json still flags a red-light violation while the collision oracle topic records at least one impulse event, even if error_json does not mark a crash.","Verify that final_waypoints remain present and not blocked in the critical window prior to the oracle collision time.","Confirm that vehicle_cmd remains effectively zero for accel, brake, steer, and target speed, while vehicle_status (or odometry) indicates at most slight motion.","Do not attribute the root cause to a specific Autoware module unless additional evidence (e.g., detailed logs or manual inspection) becomes available."]},"seed_scenario":{"mission":{"map":"Town01","spawn":{"x":301.3399658203125,"y":330.53997802734375,"z":0.29999998211860657,"pitch":0.0,"yaw":-9.1552734375e-05,"roll":0.0},"destination":{"x":339.01873779296875,"y":116.54576110839844,"z":0.29999998211860657,"yaw":-89.99993896484375}},"weather":{"cloud":76,"rain":93,"puddle":42,"wind":54,"fog":4,"wetness":81,"angle":178,"altitude":16},"actors":[{"index":0,"type":"vehicle","nav_type":"autopilot","speed":15.22,"spawn":{"x":280.971,"y":331.0,"z":1.5,"pitch":0.0,"yaw":216.15,"roll":0.0}},{"index":1,"type":"walker","nav_type":"linear","speed":0.53,"spawn":{"x":286.686,"y":331.0,"z":1.5,"pitch":0.0,"yaw":31.215,"roll":0.0}}],"puddles":[]}}