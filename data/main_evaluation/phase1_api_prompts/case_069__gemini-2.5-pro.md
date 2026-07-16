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
{"case_id":"case_069","fault_label":{"collision":1,"stuck":0,"lane_invasion":1,"red_light":0,"group":"C+L"},"oracle_consistency":{"status":"dataset_only","dataset_group":"C+L","error_json_group":"none","conflict_details":"collision: dataset=1, error_json=0; lane_invasion: dataset=1, error_json=0; group: dataset=C+L, error_json=none","suggested_action":"needs_manual_review"},"scenario_config":{"map":"Town01","mission":{"start":{"sp_x":86.0,"sp_y":145.0,"sp_z":0.29999998211860657,"yaw":90.0},"goal":{"wp_x":182.91,"wp_y":198.76,"wp_z":0.29999998211860657,"wp_yaw":179.999755859375}},"actors":"2 actor(s)","weather":{"cloud":98,"rain":5,"puddle":8,"wind":25,"fog":12,"wetness":10,"angle":47,"altitude":76},"puddles":"0 puddle region(s)"},"available_topics":["/carla/ego_vehicle/imu/imu","/image_raw","/points_raw","/detection/fusion_tools/objects","/current_pose","/prediction/motion_predictor/objects","/lane_waypoints_array","/final_waypoints","/vehicle_cmd","/carla/ego_vehicle/vehicle_status","/carla/ego_vehicle/collision","/carla/ego_vehicle/odometry","/carla/objects","/carla/traffic_lights"],"critical_window_summary":{"case_id":"case_069","dataset_group":"C+L","oracle_consistency_status":"dataset_only","error_json_events":{"crash":false,"stuck":false,"lane_invasion":false,"red":false,"speeding":true,"other":false,"other_error_val":0},"collision_window":{"collision_timestamp":"28.455423457","window_start":"23.455423457","window_end":"28.455423457","collision_topic_exists":true,"error_json_crash":false,"ego_speed_before_collision":{"nearest_pre_collision_velocity":5.459115982055664,"window_velocity_stats":{"min":4.359742,"max":6.04616,"mean":5.187746,"last":5.459116}},"ego_control_before_collision":{"vehicle_status_control_stats":{"throttle":{"min":0.227795,"max":1.0,"mean":0.495115,"last":0.446853},"brake":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer":{"min":-0.3306,"max":0.594047,"mean":0.140597,"last":0.053626}},"vehicle_cmd_stats":{"accel_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"brake_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"linear_velocity_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0}}},"detected_object_count_before_collision":{"rows":86,"count_stats":{"min":1.0,"max":11.0,"mean":2.802326,"last":1.0},"labels_sample":["car","person","unknown"]},"predicted_object_count_before_collision":{"rows":86,"count_stats":{"min":1.0,"max":21.0,"mean":3.5,"last":1.0},"labels_sample":["car","person","unknown"]},"final_waypoints_before_collision":{"rows":41,"waypoint_count_stats":{"min":101.0,"max":101.0,"mean":101.0,"last":101.0},"blocked_true_count_rows":0,"blocked_true_count_nonzero":false,"blocked_waypoint_event_total":0,"nearest_pre_collision_row":{"timestamp":28.405423456,"waypoint_count":101,"is_blocked":false,"blocked_waypoint_events":0,"closest_object_distance":0.0,"closest_object_velocity":0.0,"stop_line_ids":[4294967295]}},"closest_available_object_info":{"object_id":2042,"classification":6,"distance_to_ego":11.225,"position":{"x":80.592,"y":-181.285,"z":0.033}},"evidence_of_braking_or_stopping":{"vehicle_status_brake_nonzero":false,"vehicle_cmd_brake_nonzero":false,"speed_decreases_within_window":false}},"label_conflict":{"dataset_group":"C+L","error_json_group":"none","conflict_details":"collision: dataset=1, error_json=0; lane_invasion: dataset=1, error_json=0; group: dataset=C+L, error_json=none","needs_manual_review":true,"guidance":"Use this case as uncertainty-aware Phase 1 input unless manual review resolves the conflict."}},"trace_summary_compact":{"sensing":{"image_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":600,"width":800,"encoding":"bgra8"},"time_range":["5.105423109","30.605423489"]},"points_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":1,"width":8095,"point_step":16},"time_range":["5.255423111","30.605423489"]}},"perception":{"detection_objects":{"exists":true,"rows_sampled":113,"sample_truncated":false,"first_timestamp":"19.455423323","last_timestamp":"29.455423472","object_count_range":{"min":1.0,"max":11.0},"object_count_avg_sample":2.611,"labels_sample":["car","person","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":17}},"prediction_objects":{"exists":true,"rows_sampled":113,"sample_truncated":false,"first_timestamp":"19.455423323","last_timestamp":"29.455423472","object_count_range":{"min":1.0,"max":21.0},"object_count_avg_sample":4.204,"labels_sample":["car","person","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":134}},"current_pose":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"11.105423199","last_timestamp":"30.555423488","start_position":{"x":85.9916000366211,"y":-144.99085998535156,"z":0.0866851806640625},"end_position_sample":{"x":88.27176666259766,"y":-150.19683837890625,"z":0.03519606590270996}}},"planning":{"final_waypoints":{"exists":true,"rows_sampled":118,"sample_truncated":false,"first_timestamp":"15.655423266","last_timestamp":"30.555423488","waypoint_count_range":{"min":92.0,"max":101.0},"blocked_true_count_sample":0,"null_rows_sample":0},"lane_waypoints_array":{"exists":true,"rows_sampled":1,"sample_truncated":false,"first_timestamp":"15.405423263","last_timestamp":"15.405423263","lane_count_range":{"min":1.0,"max":1.0},"primary_lane_waypoint_count_range":{"min":152.0,"max":152.0},"null_rows_sample":0}},"actuation":{"vehicle_cmd":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"12.155423214","last_timestamp":"30.605423489","steer_cmd_range":{"min":0.0,"max":0.0},"accel_cmd_range":{"min":0.0,"max":0.0},"brake_cmd_range":{"min":0.0,"max":0.0},"target_speed_range":{"min":0.0,"max":0.0}},"vehicle_status":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.205423096","last_timestamp":"30.605423489","velocity_range":{"min":0.0,"max":8.2940034866333},"throttle_range":{"min":0.0,"max":0.0},"brake_range":{"min":0.0,"max":0.0},"steer_range":{"min":0.0,"max":0.0}}},"oracle":{"collision":{"exists":true,"rows_sampled":6,"sample_truncated":false,"first_timestamp":"28.455423457","last_timestamp":"30.355423485","other_actor_ids_sample":["0"],"impulse_magnitude_range":{"min":258.34357613653657,"max":18076.437182658574}},"traffic_lights":{"exists":true,"rows_sampled":6,"sample_truncated":false,"first_timestamp":"4.655423102","last_timestamp":"29.955423479","traffic_light_count_range":{"min":36.0,"max":36.0},"state_sample":["0","1","2"]},"odometry":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.205423096","last_timestamp":"30.605423489","start_position":{"x":86.0,"y":-145.0,"z":3.2726552486419678},"end_position_sample":{"x":85.99044799804688,"y":-145.0,"z":0.08852683752775192}},"objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"3.655423087","last_timestamp":"30.555423488","object_count_range":{"min":0.0,"max":3.0},"object_count_avg_sample":2.73,"labels_sample":[],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":0}},"error_json_events":{"crash":false,"stuck":false,"lane_invasion":false,"red":false,"speeding":true,"other":false,"other_error_val":0}}},"known_limitations":["Dataset labels and error.json oracle events are not fully aligned for some cases.","Dataset.xlsx and error.json are inconsistent for this case; Phase 1 must explicitly mark uncertainty.","Dataset.xlsx and error.json oracle labels are compared separately; conflicts are preserved rather than resolved automatically.","Large CSV topics were summarized with bounded scans for reproducibility and memory safety.","Sensor and perception topics are summarized where available; large raw arrays are not included in prompts."],"manual_phase1_status":{"candidate_generation_status":null,"oracle_consistency_status":null,"known_limitations":[]}}