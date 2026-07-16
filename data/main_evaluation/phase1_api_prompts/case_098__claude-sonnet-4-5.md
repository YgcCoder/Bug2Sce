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
{"case_id":"case_098","fault_label":{"collision":1,"stuck":0,"lane_invasion":0,"red_light":0,"group":"C"},"oracle_consistency":{"status":"consistent","dataset_group":"C","error_json_group":"C","conflict_details":"all comparable labels match","suggested_action":"no_action_needed"},"scenario_config":{"map":"Town01","mission":{"start":{"sp_x":339.01873779296875,"sp_y":116.54576110839844,"sp_z":0.29999998211860657,"yaw":-89.99993896484375},"goal":{"wp_x":301.3399658203125,"wp_y":330.53997802734375,"wp_z":0.29999998211860657,"wp_yaw":-9.1552734375e-05}},"actors":"2 actor(s)","weather":{"cloud":15,"rain":4,"puddle":3,"wind":13,"fog":2,"wetness":1,"angle":268,"altitude":66},"puddles":"2 puddle region(s)"},"available_topics":["/carla/ego_vehicle/imu/imu","/image_raw","/points_raw","/detection/fusion_tools/objects","/current_pose","/prediction/motion_predictor/objects","/lane_waypoints_array","/final_waypoints","/vehicle_cmd","/carla/ego_vehicle/vehicle_status","/carla/ego_vehicle/collision","/carla/ego_vehicle/odometry","/carla/objects","/carla/traffic_lights"],"critical_window_summary":{"case_id":"case_098","dataset_group":"C","oracle_consistency_status":"consistent","error_json_events":{"crash":true,"stuck":false,"lane_invasion":false,"red":false,"speeding":false,"other":false,"other_error_val":0},"collision_window":{"collision_timestamp":"29.091650286","window_start":"24.091650286","window_end":"29.091650286","collision_topic_exists":true,"error_json_crash":true,"ego_speed_before_collision":{"nearest_pre_collision_velocity":4.812376499176025,"window_velocity_stats":{"min":0.0,"max":4.926036,"mean":3.240151,"last":4.812376}},"ego_control_before_collision":{"vehicle_status_control_stats":{"throttle":{"min":0.308983,"max":0.561172,"mean":0.456852,"last":0.308983},"brake":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer":{"min":-0.049063,"max":0.014337,"mean":-0.008297,"last":5.5e-05}},"vehicle_cmd_stats":{"accel_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"brake_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"linear_velocity_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0}}},"detected_object_count_before_collision":{"rows":145,"count_stats":{"min":1.0,"max":2.0,"mean":1.634483,"last":1.0},"labels_sample":["car","person","unknown"]},"predicted_object_count_before_collision":{"rows":145,"count_stats":{"min":1.0,"max":22.0,"mean":5.082759,"last":11.0},"labels_sample":["car","person","unknown"]},"final_waypoints_before_collision":{"rows":37,"waypoint_count_stats":{"min":101.0,"max":101.0,"mean":101.0,"last":101.0},"blocked_true_count_rows":0,"blocked_true_count_nonzero":false,"blocked_waypoint_event_total":0,"nearest_pre_collision_row":{"timestamp":28.991650285,"waypoint_count":101,"is_blocked":false,"blocked_waypoint_events":0,"closest_object_distance":0.0,"closest_object_velocity":0.0,"stop_line_ids":[4294967295]}},"closest_available_object_info":{"object_id":5275,"classification":6,"distance_to_ego":4.048,"position":{"x":335.795,"y":-97.748,"z":0.074}},"evidence_of_braking_or_stopping":{"vehicle_status_brake_nonzero":false,"vehicle_cmd_brake_nonzero":false,"speed_decreases_within_window":false}}},"trace_summary_compact":{"sensing":{"image_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":600,"width":800,"encoding":"bgra8"},"time_range":["5.741649938","30.441650306"]},"points_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":1,"width":8225,"point_step":16},"time_range":["5.741649938","30.441650306"]}},"perception":{"detection_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"13.591650055","last_timestamp":"30.441650306","object_count_range":{"min":1.0,"max":3.0},"object_count_avg_sample":1.985,"labels_sample":["car","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":162}},"prediction_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"13.591650055","last_timestamp":"30.441650306","object_count_range":{"min":1.0,"max":33.0},"object_count_avg_sample":10.085,"labels_sample":["car","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":874}},"current_pose":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"12.791650043","last_timestamp":"30.441650306","start_position":{"x":339.00836181640625,"y":-116.53643035888672,"z":0.033496856689453125},"end_position_sample":{"x":339.00506591796875,"y":-116.54151153564453,"z":0.0273740291595459}}},"planning":{"final_waypoints":{"exists":true,"rows_sampled":90,"sample_truncated":false,"first_timestamp":"18.491650128","last_timestamp":"30.391650306","waypoint_count_range":{"min":101.0,"max":101.0},"blocked_true_count_sample":0,"null_rows_sample":0},"lane_waypoints_array":{"exists":true,"rows_sampled":1,"sample_truncated":false,"first_timestamp":"17.841650119","last_timestamp":"17.841650119","lane_count_range":{"min":1.0,"max":1.0},"primary_lane_waypoint_count_range":{"min":783.0,"max":783.0},"null_rows_sample":0}},"actuation":{"vehicle_cmd":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"14.791650073","last_timestamp":"30.441650306","steer_cmd_range":{"min":0.0,"max":0.0},"accel_cmd_range":{"min":0.0,"max":0.0},"brake_cmd_range":{"min":0.0,"max":0.0},"target_speed_range":{"min":0.0,"max":0.0}},"vehicle_status":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"6.491649949","last_timestamp":"30.441650306","velocity_range":{"min":0.0,"max":0.0},"throttle_range":{"min":0.0,"max":0.0},"brake_range":{"min":0.0,"max":0.0},"steer_range":{"min":0.0,"max":0.0}}},"oracle":{"collision":{"exists":true,"rows_sampled":6,"sample_truncated":false,"first_timestamp":"29.091650286","last_timestamp":"29.341650290","other_actor_ids_sample":["5275"],"impulse_magnitude_range":{"min":51.168759142207136,"max":2342.666825901773}},"traffic_lights":{"exists":true,"rows_sampled":5,"sample_truncated":false,"first_timestamp":"5.091649929","last_timestamp":"28.341650275","traffic_light_count_range":{"min":36.0,"max":36.0},"state_sample":["0","1","2"]},"odometry":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"5.791649939","last_timestamp":"30.441650306","start_position":{"x":339.0164489746094,"y":-116.5408935546875,"z":0.005649680737406015},"end_position_sample":{"x":339.01654052734375,"y":-116.5456314086914,"z":0.03669147565960884}},"objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"5.091649929","last_timestamp":"30.441650306","object_count_range":{"min":1.0,"max":3.0},"object_count_avg_sample":2.815,"labels_sample":[],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":0}},"error_json_events":{"crash":true,"stuck":false,"lane_invasion":false,"red":false,"speeding":false,"other":false,"other_error_val":0}}},"known_limitations":["Dataset labels and error.json oracle events are not fully aligned for some cases.","Dataset.xlsx and error.json oracle labels are compared separately; conflicts are preserved rather than resolved automatically.","Large CSV topics were summarized with bounded scans for reproducibility and memory safety.","Sensor and perception topics are summarized where available; large raw arrays are not included in prompts."],"manual_phase1_status":{"candidate_generation_status":null,"oracle_consistency_status":null,"known_limitations":[]}}