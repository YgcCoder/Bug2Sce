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
{"case_id":"case_039","fault_label":{"collision":0,"stuck":1,"lane_invasion":1,"red_light":0,"group":"S+L"},"oracle_consistency":{"status":"dataset_only","dataset_group":"S+L","error_json_group":"none","conflict_details":"stuck: dataset=1, error_json=0; lane_invasion: dataset=1, error_json=0; group: dataset=S+L, error_json=none","suggested_action":"needs_manual_review"},"scenario_config":{"map":"Town01","mission":{"start":{"sp_x":46.14997863769531,"sp_y":326.9700012207031,"sp_z":0.29999998211860657,"yaw":179.999755859375},"goal":{"wp_x":60.10997772216797,"wp_y":330.4599914550781,"wp_z":0.29999998211860657,"wp_yaw":-9.1552734375e-05}},"actors":"1 actor(s)","weather":{"cloud":18,"rain":3,"puddle":0,"wind":9,"fog":0,"wetness":2,"angle":23,"altitude":84},"puddles":"3 puddle region(s)"},"available_topics":["/carla/ego_vehicle/imu/imu","/image_raw","/points_raw","/detection/fusion_tools/objects","/current_pose","/prediction/motion_predictor/objects","/lane_waypoints_array","/final_waypoints","/vehicle_cmd","/carla/ego_vehicle/vehicle_status","/carla/ego_vehicle/odometry","/carla/objects","/carla/traffic_lights"],"critical_window_summary":{"case_id":"case_039","dataset_group":"S+L","oracle_consistency_status":"dataset_only","error_json_events":{"crash":false,"stuck":false,"lane_invasion":false,"red":false,"speeding":false,"other":"goal","other_error_val":57.70211410522461},"stuck_window":{"stuck_from_error_json":false,"total_duration_sec":61.55,"last_60_seconds_window":{"start_timestamp":"20.795496855","end_timestamp":"80.795496855","ego_movement_distance":101.955,"ego_start_to_end_displacement":42.074,"velocity_stats":{"min":0.0,"max":5.548506,"mean":1.050776,"last":4.172131},"vehicle_status_control_stats":{"throttle":{"min":0.0,"max":0.569038,"mean":0.11733,"last":0.19023},"brake":{"min":0.0,"max":0.248097,"mean":0.004723,"last":0.0},"steer":{"min":-0.735017,"max":0.563481,"mean":0.286583,"last":-0.0}},"vehicle_cmd_stats":{"accel_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"brake_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0}},"final_waypoints_present":true,"final_waypoint_count_stats":{"min":101,"max":101,"mean":101.0,"last":101}},"collision_or_red_light_interference":{"error_json_collision":false,"error_json_red":false,"collision_topic_exists":false}},"label_conflict":{"dataset_group":"S+L","error_json_group":"none","conflict_details":"stuck: dataset=1, error_json=0; lane_invasion: dataset=1, error_json=0; group: dataset=S+L, error_json=none","needs_manual_review":true,"guidance":"Use this case as uncertainty-aware Phase 1 input unless manual review resolves the conflict."}},"trace_summary_compact":{"sensing":{"image_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":600,"width":800,"encoding":"bgra8"},"time_range":["5.845495739","80.795496855"]},"points_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":1,"width":8043,"point_step":16},"time_range":["5.895495739","80.745496855"]}},"perception":{"detection_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"13.345495850","last_timestamp":"79.195496832","object_count_range":{"min":1.0,"max":9.0},"object_count_avg_sample":2.74,"labels_sample":["unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":111}},"prediction_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"13.345495850","last_timestamp":"79.195496832","object_count_range":{"min":1.0,"max":29.0},"object_count_avg_sample":8.29,"labels_sample":["unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":988}},"current_pose":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"12.845495843","last_timestamp":"80.795496855","start_position":{"x":46.16083908081055,"y":-326.9770202636719,"z":0.03302717208862305},"end_position_sample":{"x":38.20570373535156,"y":-326.5902099609375,"z":0.03291583061218262}}},"planning":{"final_waypoints":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"16.945495904","last_timestamp":"80.745496855","waypoint_count_range":{"min":101.0,"max":101.0},"blocked_true_count_sample":0,"null_rows_sample":0},"lane_waypoints_array":{"exists":true,"rows_sampled":1,"sample_truncated":false,"first_timestamp":"15.945495889","last_timestamp":"15.945495889","lane_count_range":{"min":1.0,"max":1.0},"primary_lane_waypoint_count_range":{"min":1152.0,"max":1152.0},"null_rows_sample":0}},"actuation":{"vehicle_cmd":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"14.795495872","last_timestamp":"80.795496855","steer_cmd_range":{"min":0.0,"max":0.0},"accel_cmd_range":{"min":0.0,"max":0.0},"brake_cmd_range":{"min":0.0,"max":0.0},"target_speed_range":{"min":0.0,"max":0.0}},"vehicle_status":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.845495724","last_timestamp":"80.795496855","velocity_range":{"min":0.0,"max":9.750345230102539},"throttle_range":{"min":0.0,"max":0.0},"brake_range":{"min":0.0,"max":0.0},"steer_range":{"min":0.0,"max":0.0}}},"oracle":{"collision":null,"traffic_lights":{"exists":true,"rows_sampled":16,"sample_truncated":false,"first_timestamp":"4.295495715","last_timestamp":"77.895496812","traffic_light_count_range":{"min":36.0,"max":36.0},"state_sample":["0","1","2"]},"odometry":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.845495724","last_timestamp":"80.795496855","start_position":{"x":46.14997863769531,"y":-326.9700012207031,"z":2.181494951248169},"end_position_sample":{"x":46.149940490722656,"y":-326.9721984863281,"z":0.03581890091300011}},"objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.345495716","last_timestamp":"80.795496855","object_count_range":{"min":1.0,"max":2.0},"object_count_avg_sample":1.88,"labels_sample":[],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":0}},"error_json_events":{"crash":false,"stuck":false,"lane_invasion":false,"red":false,"speeding":false,"other":"goal","other_error_val":57.70211410522461}}},"known_limitations":["Dataset labels and error.json oracle events are not fully aligned for some cases.","Dataset.xlsx and error.json are inconsistent for this case; Phase 1 must explicitly mark uncertainty.","Dataset.xlsx and error.json oracle labels are compared separately; conflicts are preserved rather than resolved automatically.","Large CSV topics were summarized with bounded scans for reproducibility and memory safety.","Sensor and perception topics are summarized where available; large raw arrays are not included in prompts."],"manual_phase1_status":{"candidate_generation_status":null,"oracle_consistency_status":null,"known_limitations":[]}}