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
{"case_id":"case_118","fault_label":{"collision":1,"stuck":0,"lane_invasion":1,"red_light":1,"group":"C+L+R"},"oracle_consistency":{"status":"dataset_only","dataset_group":"C+L+R","error_json_group":"C+R","conflict_details":"lane_invasion: dataset=1, error_json=0; group: dataset=C+L+R, error_json=C+R","suggested_action":"needs_manual_review"},"scenario_config":{"map":"Town01","mission":{"start":{"sp_x":104.8687973022461,"sp_y":59.99010467529297,"sp_z":0.29999998211860657,"yaw":0.0},"goal":{"wp_x":392.4700012207031,"wp_y":105.38999938964844,"wp_z":0.29999998211860657,"wp_yaw":90.00004577636719}},"actors":"0 actor(s)","weather":{"cloud":12,"rain":24,"puddle":39,"wind":17,"fog":46,"wetness":45,"angle":269,"altitude":38},"puddles":"3 puddle region(s)"},"available_topics":["/carla/ego_vehicle/imu/imu","/image_raw","/points_raw","/detection/fusion_tools/objects","/current_pose","/prediction/motion_predictor/objects","/lane_waypoints_array","/final_waypoints","/vehicle_cmd","/carla/ego_vehicle/vehicle_status","/carla/ego_vehicle/collision","/carla/ego_vehicle/odometry","/carla/objects","/carla/traffic_lights"],"critical_window_summary":{"case_id":"case_118","dataset_group":"C+L+R","oracle_consistency_status":"dataset_only","error_json_events":{"crash":true,"stuck":false,"lane_invasion":false,"red":true,"speeding":false,"other":false,"other_error_val":0},"collision_window":{"collision_timestamp":"66.409877199","window_start":"61.409877199","window_end":"66.409877199","collision_topic_exists":true,"error_json_crash":true,"ego_speed_before_collision":{"nearest_pre_collision_velocity":5.069024085998535,"window_velocity_stats":{"min":1.536393,"max":5.109308,"mean":2.924402,"last":5.069024}},"ego_control_before_collision":{"vehicle_status_control_stats":{"throttle":{"min":0.051705,"max":0.580978,"mean":0.395641,"last":0.409256},"brake":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer":{"min":-0.311246,"max":0.414993,"mean":0.126772,"last":0.017898}},"vehicle_cmd_stats":{"accel_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"brake_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"linear_velocity_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0}}},"detected_object_count_before_collision":{"rows":26,"count_stats":{"min":1.0,"max":3.0,"mean":1.192308,"last":1.0},"labels_sample":["unknown"]},"predicted_object_count_before_collision":{"rows":26,"count_stats":{"min":1.0,"max":33.0,"mean":12.730769,"last":1.0},"labels_sample":["unknown"]},"final_waypoints_before_collision":{"rows":38,"waypoint_count_stats":{"min":101.0,"max":101.0,"mean":101.0,"last":101.0},"blocked_true_count_rows":0,"blocked_true_count_nonzero":false,"blocked_waypoint_event_total":0,"nearest_pre_collision_row":{"timestamp":66.409877199,"waypoint_count":101,"is_blocked":false,"blocked_waypoint_events":0,"closest_object_distance":0.0,"closest_object_velocity":0.0,"stop_line_ids":[4294967295]}},"closest_available_object_info":"unknown","evidence_of_braking_or_stopping":{"vehicle_status_brake_nonzero":false,"vehicle_cmd_brake_nonzero":false,"speed_decreases_within_window":false}},"red_light_window":{"red_light_violation_from_error_json":true,"red_light_violation_timestamp":"unknown","traffic_lights_topic_exists":true,"traffic_light_state_samples":[{"timestamp":"62.759877145","traffic_light_count":36,"state_histogram":{"2":12,"0":24},"sample":[{"id":16896,"state":2},{"id":16897,"state":0},{"id":16898,"state":0},{"id":16899,"state":2},{"id":16900,"state":0}]}],"route_light_relation_confirmed":"unknown","stop_line_crossing_confirmed":"unknown","nearest_final_waypoints_stop_line_ids":[4294967295],"notes":"Traffic light states may be available, but route-light relation and stop-line crossing are not confirmed by the current summaries."},"label_conflict":{"dataset_group":"C+L+R","error_json_group":"C+R","conflict_details":"lane_invasion: dataset=1, error_json=0; group: dataset=C+L+R, error_json=C+R","needs_manual_review":true,"guidance":"Use this case as uncertainty-aware Phase 1 input unless manual review resolves the conflict."}},"trace_summary_compact":{"sensing":{"image_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":600,"width":800,"encoding":"bgra8"},"time_range":["5.959876298","67.309877213"]},"points_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":1,"width":8466,"point_step":16},"time_range":["6.009876299","67.309877213"]}},"perception":{"detection_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"10.459876365","last_timestamp":"67.109877210","object_count_range":{"min":1.0,"max":2.0},"object_count_avg_sample":1.15,"labels_sample":["car","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":82}},"prediction_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"10.459876365","last_timestamp":"67.109877210","object_count_range":{"min":1.0,"max":22.0},"object_count_avg_sample":4.85,"labels_sample":["car","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":698}},"current_pose":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"9.959876358","last_timestamp":"67.309877213","start_position":{"x":104.87642669677734,"y":-59.99241638183594,"z":0.03804135322570801},"end_position_sample":{"x":113.2741928100586,"y":-59.53361129760742,"z":0.03578543663024902}}},"planning":{"final_waypoints":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"14.009876418","last_timestamp":"67.309877213","waypoint_count_range":{"min":101.0,"max":101.0},"blocked_true_count_sample":0,"null_rows_sample":0},"lane_waypoints_array":{"exists":true,"rows_sampled":1,"sample_truncated":false,"first_timestamp":"13.109876405","last_timestamp":"13.109876405","lane_count_range":{"min":1.0,"max":1.0},"primary_lane_waypoint_count_range":{"min":775.0,"max":775.0},"null_rows_sample":0}},"actuation":{"vehicle_cmd":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"11.009876374","last_timestamp":"67.309877213","steer_cmd_range":{"min":0.0,"max":0.0},"accel_cmd_range":{"min":0.0,"max":0.0},"brake_cmd_range":{"min":0.0,"max":0.0},"target_speed_range":{"min":0.0,"max":0.0}},"vehicle_status":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"5.459876291","last_timestamp":"67.309877213","velocity_range":{"min":0.0,"max":0.23826952278614044},"throttle_range":{"min":0.0,"max":0.16760265827178955},"brake_range":{"min":0.0,"max":0.0},"steer_range":{"min":-0.13832111656665802,"max":0.0}}},"oracle":{"collision":{"exists":true,"rows_sampled":15,"sample_truncated":false,"first_timestamp":"66.409877199","last_timestamp":"67.309877213","other_actor_ids_sample":["0"],"impulse_magnitude_range":{"min":60.58134594147168,"max":11424.720935236082}},"traffic_lights":{"exists":true,"rows_sampled":13,"sample_truncated":false,"first_timestamp":"4.559876278","last_timestamp":"62.759877145","traffic_light_count_range":{"min":36.0,"max":36.0},"state_sample":["0","1","2"]},"odometry":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"5.509876292","last_timestamp":"67.309877213","start_position":{"x":104.87335968017578,"y":-59.98706817626953,"z":0.030306318774819374},"end_position_sample":{"x":104.86888122558594,"y":-59.98720932006836,"z":0.035792846232652664}},"objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.559876278","last_timestamp":"67.309877213","object_count_range":{"min":1.0,"max":1.0},"object_count_avg_sample":1.0,"labels_sample":[],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":0}},"error_json_events":{"crash":true,"stuck":false,"lane_invasion":false,"red":true,"speeding":false,"other":false,"other_error_val":0}}},"known_limitations":["Dataset labels and error.json oracle events are not fully aligned for some cases.","Dataset.xlsx and error.json are inconsistent for this case; Phase 1 must explicitly mark uncertainty.","Dataset.xlsx and error.json oracle labels are compared separately; conflicts are preserved rather than resolved automatically.","Large CSV topics were summarized with bounded scans for reproducibility and memory safety.","Sensor and perception topics are summarized where available; large raw arrays are not included in prompts."],"manual_phase1_status":{"candidate_generation_status":null,"oracle_consistency_status":null,"known_limitations":[]}}