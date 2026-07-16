You are the Phase 1 failure analyzer for Bug2Scenario.
Task: infer a causal explanation and a root-cause pattern from the given DriveFuzz/Autoware evidence.

Rules:
- Return exactly one JSON object. Do not use markdown fences.
- Use only the provided evidence. Do not invent sensor, perception, planning, control, map, or simulator facts.
- Do not treat topic existence as proof that a module behaved correctly.
- If Dataset.xlsx and error.json disagree, mark uncertainty and do not treat the dataset label as confirmed ground truth.
- For red-light cases, do not infer route-light relation or stop-line crossing unless evidence is provided.
- For lane invasion, do not infer lane-boundary crossing unless evidence is provided.
- For stuck cases, use last-window velocity/movement evidence if available.
- If vehicle_cmd is all zero but vehicle_status shows movement/braking, mark controller behavior as uncertain. Do not assign fault_layer=actuation from this mismatch alone.
- Preservation constraints must be semantic conditions, not exact timestamps, raw actor IDs, or message-specific identifiers.
- Root-cause patterns should describe a mechanism. Avoid label-like patterns unless independently supported by evidence.
- Do not write that a module `fails to` detect, predict, plan, stop, or avoid unless the provided evidence directly supports that internal failure.
- If the evidence only shows a symptom plus available topics, use cautious language such as `possible`, `candidate`, or `unknown`.
- Prefer fault_layer=unknown when module-level attribution is not directly supported by critical-window evidence.
- A root-cause pattern may be a conservative preservation pattern, not a confirmed module bug.
- Do not set ready_for_phase2_generation=no solely because fault_layer is unknown. Use yes when there is a checkable conservative preservation pattern; use uncertain when labels conflict or a key condition is missing.
- Be concise: prefer short strings and 3-6 constraints.

Return JSON schema:
{
  "case_id": "case_XXX",
  "fault_layer": "sensing | perception | planning | actuation | simulator | map | unknown",
  "fault_component": "string or unknown",
  "causal_explanation": "concise evidence-grounded explanation",
  "root_cause_pattern": "string or unknown",
  "preservation_constraints": ["constraint strings for same-root-cause generation"],
  "modifiable_factors": ["actor_position", "weather", "mission", "puddles", "..."],
  "non_modifiable_conditions": ["conditions that must stay true"],
  "uncertainty": ["missing or conflicting evidence"],
  "evidence_support": [
    {"evidence_id": "string", "claim": "string"}
  ],
  "confidence": "high | medium | low",
  "ready_for_phase2_generation": "yes | no | uncertain",
  "notes_for_validator": ["rules to check before or after execution"]
}

Output style reference only; do not copy facts from this example into the current case:
{
  "case_id": "case_EXAMPLE",
  "fault_layer": "unknown",
  "fault_component": "unknown",
  "causal_explanation": "The oracle confirms a collision. Critical-window evidence shows a nearby actor, available object summaries, and final waypoints before the failure, but it does not directly prove which Autoware module failed.",
  "root_cause_pattern": "Conservative preservation pattern: ego encounters a nearby actor on or near the planned route before a collision, while module-level attribution remains unknown.",
  "preservation_constraints": [
    "The generated candidate should preserve the same oracle symptom.",
    "A nearby actor should be present near the ego route before the failure.",
    "Post-execution validation should check critical-window ego speed, actor proximity, and final-waypoint availability."
  ],
  "modifiable_factors": ["actor_position", "weather", "puddles"],
  "non_modifiable_conditions": ["same oracle symptom", "nearby actor-route interaction"],
  "uncertainty": ["The provided evidence does not directly localize the failure to perception, planning, or actuation."],
  "evidence_support": [
    {"evidence_id": "critical_window_summary", "claim": "Nearby actor and final-waypoint evidence are available before the failure."}
  ],
  "confidence": "low",
  "ready_for_phase2_generation": "yes",
  "notes_for_validator": ["Do not count a generated case as same-root-cause unless post-execution evidence preserves the actor-route interaction and oracle symptom."]
}

Input evidence JSON:
{"case_id":"case_040","fault_label":{"collision":0,"stuck":0,"lane_invasion":0,"red_light":1,"group":"R"},"oracle_consistency":{"status":"consistent","dataset_group":"R","error_json_group":"R","conflict_details":"all comparable labels match","suggested_action":"no_action_needed"},"scenario_config":{"map":"Town01","mission":{"start":{"sp_x":110.0,"sp_y":129.0,"sp_z":1.0,"yaw":180.0},"goal":{"wp_x":113.0,"wp_y":130.0,"wp_z":0.0,"wp_yaw":0.0}},"actors":"2 actor(s)","weather":{"cloud":81,"rain":83,"puddle":56,"wind":45,"fog":34,"wetness":86,"angle":169,"altitude":26},"puddles":"0 puddle region(s)"},"available_topics":["/carla/ego_vehicle/imu/imu","/image_raw","/points_raw","/detection/fusion_tools/objects","/current_pose","/prediction/motion_predictor/objects","/lane_waypoints_array","/final_waypoints","/vehicle_cmd","/carla/ego_vehicle/vehicle_status","/carla/ego_vehicle/odometry","/carla/objects","/carla/traffic_lights"],"critical_window_summary":{"case_id":"case_040","dataset_group":"R","oracle_consistency_status":"consistent","error_json_events":{"crash":false,"stuck":false,"lane_invasion":false,"red":true,"speeding":false,"other":"goal","other_error_val":3.6049532890319824},"red_light_window":{"red_light_violation_from_error_json":true,"red_light_violation_timestamp":"unknown","traffic_lights_topic_exists":true,"traffic_light_state_samples":[{"timestamp":"121.337743207","traffic_light_count":36,"state_histogram":{"0":25,"1":11},"sample":[{"id":3307,"state":0},{"id":3308,"state":0},{"id":3309,"state":0},{"id":3310,"state":0},{"id":3311,"state":1}]},{"timestamp":"121.387743208","traffic_light_count":36,"state_histogram":{"0":36},"sample":[{"id":3307,"state":0},{"id":3308,"state":0},{"id":3309,"state":0},{"id":3310,"state":0},{"id":3311,"state":0}]},{"timestamp":"123.387743238","traffic_light_count":36,"state_histogram":{"0":35,"2":1},"sample":[{"id":3307,"state":0},{"id":3308,"state":0},{"id":3309,"state":2},{"id":3310,"state":0},{"id":3311,"state":0}]},{"timestamp":"123.437743239","traffic_light_count":36,"state_histogram":{"0":24,"2":12},"sample":[{"id":3307,"state":0},{"id":3308,"state":0},{"id":3309,"state":2},{"id":3310,"state":0},{"id":3311,"state":0}]}],"route_light_relation_confirmed":"unknown","stop_line_crossing_confirmed":"unknown","nearest_final_waypoints_stop_line_ids":[4294967295],"notes":"Traffic light states may be available, but route-light relation and stop-line crossing are not confirmed by the current summaries."}},"trace_summary_compact":{"sensing":{"image_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":600,"width":800,"encoding":"bgra8"},"time_range":["5.387741480","125.187743265"]},"points_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":1,"width":7904,"point_step":16},"time_range":["5.437741480","125.187743265"]}},"perception":{"detection_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"10.287741553","last_timestamp":"125.037743262","object_count_range":{"min":1.0,"max":3.0},"object_count_avg_sample":1.38,"labels_sample":["unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":77}},"prediction_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"10.287741553","last_timestamp":"125.037743262","object_count_range":{"min":1.0,"max":23.0},"object_count_avg_sample":5.03,"labels_sample":["unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":555}},"current_pose":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"10.437741555","last_timestamp":"125.187743265","start_position":{"x":110.01100158691406,"y":-128.97166442871094,"z":0.03316950798034668},"end_position_sample":{"x":99.8553237915039,"y":-129.29922485351562,"z":0.03520560264587402}}},"planning":{"final_waypoints":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"13.987741608","last_timestamp":"125.187743265","waypoint_count_range":{"min":101.0,"max":101.0},"blocked_true_count_sample":0,"null_rows_sample":0},"lane_waypoints_array":{"exists":true,"rows_sampled":1,"sample_truncated":false,"first_timestamp":"13.737741604","last_timestamp":"13.737741604","lane_count_range":{"min":1.0,"max":1.0},"primary_lane_waypoint_count_range":{"min":406.0,"max":406.0},"null_rows_sample":0}},"actuation":{"vehicle_cmd":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"11.487741570","last_timestamp":"125.187743265","steer_cmd_range":{"min":0.0,"max":0.0},"accel_cmd_range":{"min":0.0,"max":0.0},"brake_cmd_range":{"min":0.0,"max":0.0},"target_speed_range":{"min":0.0,"max":0.0}},"vehicle_status":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"5.537741482","last_timestamp":"125.187743265","velocity_range":{"min":0.0,"max":8.891582489013672},"throttle_range":{"min":0.0,"max":0.1954798847436905},"brake_range":{"min":0.0,"max":0.0},"steer_range":{"min":-0.12466338276863098,"max":0.0}}},"oracle":{"collision":null,"traffic_lights":{"exists":true,"rows_sampled":49,"sample_truncated":false,"first_timestamp":"4.837741471","last_timestamp":"123.437743239","traffic_light_count_range":{"min":36.0,"max":36.0},"state_sample":["0","1","2"]},"odometry":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"5.537741482","last_timestamp":"125.187743265","start_position":{"x":110.0,"y":-129.0,"z":0.49425017833709717},"end_position_sample":{"x":110.00000762939453,"y":-129.00048828125,"z":0.035792578011751175}},"objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.737741470","last_timestamp":"125.187743265","object_count_range":{"min":1.0,"max":3.0},"object_count_avg_sample":2.795,"labels_sample":[],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":0}},"error_json_events":{"crash":false,"stuck":false,"lane_invasion":false,"red":true,"speeding":false,"other":"goal","other_error_val":3.6049532890319824}}},"known_limitations":["Dataset labels and error.json oracle events are not fully aligned for some cases.","Dataset.xlsx and error.json oracle labels are compared separately; conflicts are preserved rather than resolved automatically.","Large CSV topics were summarized with bounded scans for reproducibility and memory safety.","Sensor and perception topics are summarized where available; large raw arrays are not included in prompts."],"manual_phase1_status":{"candidate_generation_status":null,"oracle_consistency_status":null,"known_limitations":[]}}