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
{"case_id":"case_112","fault_label":{"collision":1,"stuck":0,"lane_invasion":1,"red_light":0,"group":"C+L"},"oracle_consistency":{"status":"dataset_only","dataset_group":"C+L","error_json_group":"C","conflict_details":"lane_invasion: dataset=1, error_json=0; group: dataset=C+L, error_json=C","suggested_action":"needs_manual_review"},"scenario_config":{"map":"Town01","mission":{"start":{"sp_x":86.0,"sp_y":145.0,"sp_z":0.29999998211860657,"yaw":90.0},"goal":{"wp_x":182.91,"wp_y":198.76,"wp_z":0.29999998211860657,"wp_yaw":179.999755859375}},"actors":"2 actor(s)","weather":{"cloud":94,"rain":14,"puddle":7,"wind":28,"fog":31,"wetness":23,"angle":59,"altitude":-16},"puddles":"0 puddle region(s)"},"available_topics":["/carla/ego_vehicle/imu/imu","/image_raw","/points_raw","/detection/fusion_tools/objects","/current_pose","/prediction/motion_predictor/objects","/lane_waypoints_array","/final_waypoints","/vehicle_cmd","/carla/ego_vehicle/vehicle_status","/carla/ego_vehicle/collision","/carla/ego_vehicle/odometry","/carla/objects","/carla/traffic_lights"],"critical_window_summary":{"case_id":"case_112","dataset_group":"C+L","oracle_consistency_status":"dataset_only","error_json_events":{"crash":true,"stuck":false,"lane_invasion":false,"red":false,"speeding":false,"other":false,"other_error_val":0},"collision_window":{"collision_timestamp":"24.67003608","window_start":"19.67003608","window_end":"24.67003608","collision_topic_exists":true,"error_json_crash":true,"ego_speed_before_collision":{"nearest_pre_collision_velocity":5.560643196105957,"window_velocity_stats":{"min":4.647369,"max":5.964613,"mean":5.253699,"last":5.560643}},"ego_control_before_collision":{"vehicle_status_control_stats":{"throttle":{"min":0.307787,"max":0.558865,"mean":0.441221,"last":0.307787},"brake":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer":{"min":-0.337494,"max":0.337494,"mean":0.020167,"last":-0.259458}},"vehicle_cmd_stats":{"accel_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"brake_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"linear_velocity_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0}}},"detected_object_count_before_collision":{"rows":81,"count_stats":{"min":1.0,"max":6.0,"mean":2.135802,"last":1.0},"labels_sample":["car","person","unknown"]},"predicted_object_count_before_collision":{"rows":81,"count_stats":{"min":1.0,"max":13.0,"mean":2.753086,"last":1.0},"labels_sample":["car","person","unknown"]},"final_waypoints_before_collision":{"rows":42,"waypoint_count_stats":{"min":101.0,"max":101.0,"mean":101.0,"last":101.0},"blocked_true_count_rows":0,"blocked_true_count_nonzero":false,"blocked_waypoint_event_total":0,"nearest_pre_collision_row":{"timestamp":24.67003608,"waypoint_count":101,"is_blocked":false,"blocked_waypoint_events":0,"closest_object_distance":0.0,"closest_object_velocity":0.0,"stop_line_ids":[4294967295]}},"closest_available_object_info":{"object_id":10992,"classification":6,"distance_to_ego":10.166,"position":{"x":87.092,"y":-176.039,"z":-6.295}},"evidence_of_braking_or_stopping":{"vehicle_status_brake_nonzero":false,"vehicle_cmd_brake_nonzero":false,"speed_decreases_within_window":false}},"label_conflict":{"dataset_group":"C+L","error_json_group":"C","conflict_details":"lane_invasion: dataset=1, error_json=0; group: dataset=C+L, error_json=C","needs_manual_review":true,"guidance":"Use this case as uncertainty-aware Phase 1 input unless manual review resolves the conflict."}},"trace_summary_compact":{"sensing":{"image_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":600,"width":800,"encoding":"bgra8"},"time_range":["3.820035769","25.170036087"]},"points_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":1,"width":8201,"point_step":16},"time_range":["3.820035769","25.170036087"]}},"perception":{"detection_objects":{"exists":true,"rows_sampled":99,"sample_truncated":false,"first_timestamp":"16.920035964","last_timestamp":"25.170036087","object_count_range":{"min":1.0,"max":6.0},"object_count_avg_sample":2.192,"labels_sample":["car","person","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":14}},"prediction_objects":{"exists":true,"rows_sampled":99,"sample_truncated":false,"first_timestamp":"16.920035964","last_timestamp":"25.170036087","object_count_range":{"min":1.0,"max":22.0},"object_count_avg_sample":3.606,"labels_sample":["car","person","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":124}},"current_pose":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"6.820035814","last_timestamp":"25.170036087","start_position":{"x":85.99884796142578,"y":-144.99374389648438,"z":0.08651208877563477},"end_position_sample":{"x":87.91543579101562,"y":-149.0763702392578,"z":0.0359501838684082}}},"planning":{"final_waypoints":{"exists":true,"rows_sampled":107,"sample_truncated":false,"first_timestamp":"11.670035886","last_timestamp":"25.170036087","waypoint_count_range":{"min":101.0,"max":101.0},"blocked_true_count_sample":0,"null_rows_sample":0},"lane_waypoints_array":{"exists":true,"rows_sampled":1,"sample_truncated":false,"first_timestamp":"11.270035880","last_timestamp":"11.270035880","lane_count_range":{"min":1.0,"max":1.0},"primary_lane_waypoint_count_range":{"min":152.0,"max":152.0},"null_rows_sample":0}},"actuation":{"vehicle_cmd":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"7.870035829","last_timestamp":"25.170036087","steer_cmd_range":{"min":0.0,"max":0.0},"accel_cmd_range":{"min":0.0,"max":0.0},"brake_cmd_range":{"min":0.0,"max":0.0},"target_speed_range":{"min":0.0,"max":0.0}},"vehicle_status":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.170035774","last_timestamp":"25.170036087","velocity_range":{"min":0.0,"max":0.10752424597740173},"throttle_range":{"min":0.0,"max":0.4333864450454712},"brake_range":{"min":0.0,"max":0.0},"steer_range":{"min":-0.5583345890045166,"max":0.0}}},"oracle":{"collision":{"exists":true,"rows_sampled":7,"sample_truncated":false,"first_timestamp":"24.670036080","last_timestamp":"25.170036087","other_actor_ids_sample":["0"],"impulse_magnitude_range":{"min":70.7926865258664,"max":12078.384243018123}},"traffic_lights":{"exists":true,"rows_sampled":4,"sample_truncated":false,"first_timestamp":"3.020035757","last_timestamp":"17.020035966","traffic_light_count_range":{"min":36.0,"max":36.0},"state_sample":["0","1","2"]},"odometry":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"3.820035769","last_timestamp":"25.170036087","start_position":{"x":85.99675750732422,"y":-145.00033569335938,"z":0.07243335247039795},"end_position_sample":{"x":85.9970703125,"y":-144.9999237060547,"z":0.08773574978113174}},"objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"3.020035757","last_timestamp":"25.170036087","object_count_range":{"min":0.0,"max":3.0},"object_count_avg_sample":2.81,"labels_sample":[],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":0}},"error_json_events":{"crash":true,"stuck":false,"lane_invasion":false,"red":false,"speeding":false,"other":false,"other_error_val":0}}},"known_limitations":["Dataset labels and error.json oracle events are not fully aligned for some cases.","Dataset.xlsx and error.json are inconsistent for this case; Phase 1 must explicitly mark uncertainty.","Dataset.xlsx and error.json oracle labels are compared separately; conflicts are preserved rather than resolved automatically.","Large CSV topics were summarized with bounded scans for reproducibility and memory safety.","Sensor and perception topics are summarized where available; large raw arrays are not included in prompts."],"manual_phase1_status":{"candidate_generation_status":null,"oracle_consistency_status":null,"known_limitations":[]}}