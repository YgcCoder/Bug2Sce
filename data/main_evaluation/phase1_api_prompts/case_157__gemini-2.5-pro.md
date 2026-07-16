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
- Be concise: one-sentence explanation, one-sentence root_cause_pattern, max 3 constraints.
- Keep all strings short. Do not write paragraphs.
- Output only valid JSON. Do not use markdown fences or backticks.
- Do not include trailing commas, comments, or extra keys.

Return JSON schema:
{
  "case_id": "case_XXX",
  "fault_layer": "sensing | perception | planning | actuation | simulator | map | unknown",
  "fault_component": "under 8 words or unknown",
  "causal_explanation": "one sentence under 35 words",
  "root_cause_pattern": "one sentence under 30 words or unknown",
  "preservation_constraints": ["max 3 items; each under 18 words"],
  "modifiable_factors": ["max 4 short factors"],
  "non_modifiable_conditions": ["max 3 items; each under 18 words"],
  "uncertainty": ["max 3 items; each under 18 words"],
  "evidence_support": [
    {"evidence_id": "short id", "claim": "under 18 words"}
  ],
  "confidence": "high | medium | low",
  "ready_for_phase2_generation": "yes | no | uncertain",
  "notes_for_validator": ["max 3 items; each under 18 words"]
}

Output style reference only; do not copy facts from this example into the current case:
{
  "case_id": "case_EXAMPLE",
  "fault_layer": "unknown",
  "fault_component": "unknown",
  "causal_explanation": "The oracle confirms a collision near an actor, but module-level fault attribution is not directly supported.",
  "root_cause_pattern": "Preserve a nearby actor-route interaction before the same oracle symptom.",
  "preservation_constraints": [
    "Preserve the same oracle symptom.",
    "Keep actor near ego route.",
    "Check critical-window actor proximity."
  ],
  "modifiable_factors": ["actor_position", "weather", "puddles"],
  "non_modifiable_conditions": ["same oracle symptom", "nearby actor-route interaction"],
  "uncertainty": ["Module attribution is not directly supported."],
  "evidence_support": [
    {"evidence_id": "critical_window", "claim": "Nearby actor evidence exists before failure."}
  ],
  "confidence": "low",
  "ready_for_phase2_generation": "yes",
  "notes_for_validator": ["Require same oracle and preserved interaction."]
}

Input evidence JSON:
{"case_id":"case_157","fault_label":{"collision":1,"stuck":0,"lane_invasion":0,"red_light":0,"group":"C"},"oracle_consistency":{"status":"consistent","dataset_group":"C","error_json_group":"C","conflict_details":"all comparable labels match","suggested_action":"no_action_needed"},"scenario_config":{"map":"Town01","mission":{"start":{"sp_x":322.09625244140625,"sp_y":129.35906982421875,"sp_z":1.5,"yaw":-179.99993896484375},"goal":{"wp_x":283.6458740234375,"wp_y":133.43006896972656,"wp_z":1.5,"wp_yaw":-179.99993896484375}},"actors":"4 actor(s)","weather":{"cloud":61,"rain":47,"puddle":40,"wind":72,"fog":45,"wetness":45,"angle":219,"altitude":40},"puddles":"0 puddle region(s)"},"available_topics":["/carla/ego_vehicle/imu/imu","/image_raw","/points_raw","/detection/fusion_tools/objects","/current_pose","/prediction/motion_predictor/objects","/lane_waypoints_array","/final_waypoints","/vehicle_cmd","/carla/ego_vehicle/vehicle_status","/carla/ego_vehicle/collision","/carla/ego_vehicle/odometry","/carla/objects","/carla/traffic_lights"],"critical_window_summary":{"case_id":"case_157","dataset_group":"C","oracle_consistency_status":"consistent","error_json_events":{"crash":true,"stuck":false,"lane_invasion":false,"red":false,"speeding":false,"other":false,"other_error_val":0},"collision_window":{"collision_timestamp":"20.381264179","window_start":"15.381264179","window_end":"20.381264179","collision_topic_exists":true,"error_json_crash":true,"ego_speed_before_collision":{"nearest_pre_collision_velocity":4.699570178985596,"window_velocity_stats":{"min":0.567901,"max":4.938245,"mean":3.399614,"last":4.69957}},"ego_control_before_collision":{"vehicle_status_control_stats":{"throttle":{"min":0.179606,"max":0.56384,"mean":0.443484,"last":0.179606},"brake":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer":{"min":-0.040739,"max":0.011063,"mean":-0.005255,"last":0.002495}},"vehicle_cmd_stats":{"accel_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"brake_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"linear_velocity_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0}}},"detected_object_count_before_collision":{"rows":130,"count_stats":{"min":1.0,"max":3.0,"mean":1.330769,"last":1.0},"labels_sample":["car","unknown"]},"predicted_object_count_before_collision":{"rows":130,"count_stats":{"min":1.0,"max":23.0,"mean":4.715385,"last":1.0},"labels_sample":["car","unknown"]},"final_waypoints_before_collision":{"rows":50,"waypoint_count_stats":{"min":101.0,"max":101.0,"mean":101.0,"last":101.0},"blocked_true_count_rows":0,"blocked_true_count_nonzero":false,"blocked_waypoint_event_total":0,"nearest_pre_collision_row":{"timestamp":20.381264179,"waypoint_count":101,"is_blocked":false,"blocked_waypoint_events":0,"closest_object_distance":0.0,"closest_object_velocity":0.0,"stop_line_ids":[4294967295]}},"closest_available_object_info":{"object_id":10283,"classification":6,"distance_to_ego":3.486,"position":{"x":303.295,"y":-126.56,"z":0.153}},"evidence_of_braking_or_stopping":{"vehicle_status_brake_nonzero":false,"vehicle_cmd_brake_nonzero":false,"speed_decreases_within_window":false}}},"trace_summary_compact":{"sensing":{"image_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":600,"width":800,"encoding":"bgra8"},"time_range":["5.181263952","21.131264190"]},"points_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":1,"width":8397,"point_step":16},"time_range":["6.181263967","21.131264190"]}},"perception":{"detection_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"9.181264012","last_timestamp":"21.131264190","object_count_range":{"min":1.0,"max":3.0},"object_count_avg_sample":1.18,"labels_sample":["car","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":38}},"prediction_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"9.181264012","last_timestamp":"21.131264190","object_count_range":{"min":1.0,"max":23.0},"object_count_avg_sample":3.08,"labels_sample":["car","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":317}},"current_pose":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"9.181264012","last_timestamp":"21.131264190","start_position":{"x":322.0932922363281,"y":-129.36697387695312,"z":0.03582906723022461},"end_position_sample":{"x":311.259033203125,"y":-129.4998016357422,"z":0.0332794189453125}}},"planning":{"final_waypoints":{"exists":true,"rows_sampled":85,"sample_truncated":false,"first_timestamp":"12.681264064","last_timestamp":"21.081264189","waypoint_count_range":{"min":101.0,"max":101.0},"blocked_true_count_sample":0,"null_rows_sample":0},"lane_waypoints_array":{"exists":true,"rows_sampled":1,"sample_truncated":false,"first_timestamp":"12.481264061","last_timestamp":"12.481264061","lane_count_range":{"min":1.0,"max":1.0},"primary_lane_waypoint_count_range":{"min":656.0,"max":656.0},"null_rows_sample":0}},"actuation":{"vehicle_cmd":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"10.231264027","last_timestamp":"21.131264190","steer_cmd_range":{"min":0.0,"max":0.0},"accel_cmd_range":{"min":0.0,"max":0.0},"brake_cmd_range":{"min":0.0,"max":0.0},"target_speed_range":{"min":0.0,"max":0.0}},"vehicle_status":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"5.631263959","last_timestamp":"21.131264190","velocity_range":{"min":0.0,"max":9.750345230102539},"throttle_range":{"min":0.0,"max":0.5529152750968933},"brake_range":{"min":0.0,"max":0.0},"steer_range":{"min":-0.04363064467906952,"max":0.0}}},"oracle":{"collision":{"exists":true,"rows_sampled":17,"sample_truncated":false,"first_timestamp":"20.381264179","last_timestamp":"21.131264190","other_actor_ids_sample":["10283"],"impulse_magnitude_range":{"min":19.495497729986404,"max":6954.573555081814}},"traffic_lights":{"exists":true,"rows_sampled":4,"sample_truncated":false,"first_timestamp":"4.781263946","last_timestamp":"17.681264138","traffic_light_count_range":{"min":36.0,"max":36.0},"state_sample":["0","1","2"]},"odometry":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"5.181263952","last_timestamp":"21.131264190","start_position":{"x":322.09625244140625,"y":-129.35906982421875,"z":4.236413955688477},"end_position_sample":{"x":322.09625244140625,"y":-129.36065673828125,"z":0.035792503505945206}},"objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.731263945","last_timestamp":"21.131264190","object_count_range":{"min":0.0,"max":5.0},"object_count_avg_sample":4.525,"labels_sample":[],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":0}},"error_json_events":{"crash":true,"stuck":false,"lane_invasion":false,"red":false,"speeding":false,"other":false,"other_error_val":0}}},"known_limitations":["Dataset labels and error.json oracle events are not fully aligned for some cases.","Dataset.xlsx and error.json oracle labels are compared separately; conflicts are preserved rather than resolved automatically.","Large CSV topics were summarized with bounded scans for reproducibility and memory safety.","Sensor and perception topics are summarized where available; large raw arrays are not included in prompts."],"manual_phase1_status":{"candidate_generation_status":null,"oracle_consistency_status":null,"known_limitations":[]}}