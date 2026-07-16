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
{"case_id":"case_168","fault_label":{"collision":0,"stuck":0,"lane_invasion":1,"red_light":1,"group":"L+R"},"oracle_consistency":{"status":"dataset_only","dataset_group":"L+R","error_json_group":"R","conflict_details":"lane_invasion: dataset=1, error_json=0; group: dataset=L+R, error_json=R","suggested_action":"needs_manual_review"},"scenario_config":{"map":"Town01","mission":{"start":{"sp_x":104.8687973022461,"sp_y":59.99010467529297,"sp_z":0.29999998211860657,"yaw":0.0},"goal":{"wp_x":392.4700012207031,"wp_y":105.38999938964844,"wp_z":0.29999998211860657,"wp_yaw":90.00004577636719}},"actors":"0 actor(s)","weather":{"cloud":65,"rain":37,"puddle":36,"wind":55,"fog":52,"wetness":46,"angle":91,"altitude":17},"puddles":"2 puddle region(s)"},"available_topics":["/carla/ego_vehicle/imu/imu","/image_raw","/points_raw","/detection/fusion_tools/objects","/current_pose","/prediction/motion_predictor/objects","/lane_waypoints_array","/final_waypoints","/vehicle_cmd","/carla/ego_vehicle/vehicle_status","/carla/ego_vehicle/collision","/carla/ego_vehicle/odometry","/carla/objects","/carla/traffic_lights"],"critical_window_summary":{"case_id":"case_168","dataset_group":"L+R","oracle_consistency_status":"dataset_only","error_json_events":{"crash":false,"stuck":false,"lane_invasion":false,"red":true,"speeding":false,"other":"goal","other_error_val":3.999661684036255},"collision_window":{"collision_timestamp":"169.884490155","window_start":"164.884490155","window_end":"169.884490155","collision_topic_exists":true,"error_json_crash":false,"ego_speed_before_collision":{"nearest_pre_collision_velocity":5.249034404754639,"window_velocity_stats":{"min":2.979204,"max":5.588742,"mean":3.99872,"last":5.249034}},"ego_control_before_collision":{"vehicle_status_control_stats":{"throttle":{"min":0.0,"max":0.680404,"mean":0.332141,"last":0.399446},"brake":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer":{"min":-0.337494,"max":-0.0,"mean":-0.233256,"last":-0.254275}},"vehicle_cmd_stats":{"accel_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"brake_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"linear_velocity_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0}}},"detected_object_count_before_collision":{"rows":9,"count_stats":{"min":1.0,"max":4.0,"mean":1.777778,"last":1.0},"labels_sample":["unknown"]},"predicted_object_count_before_collision":{"rows":9,"count_stats":{"min":1.0,"max":24.0,"mean":7.333333,"last":1.0},"labels_sample":["unknown"]},"final_waypoints_before_collision":{"rows":44,"waypoint_count_stats":{"min":2.0,"max":101.0,"mean":85.477273,"last":101.0},"blocked_true_count_rows":0,"blocked_true_count_nonzero":true,"blocked_waypoint_event_total":17,"nearest_pre_collision_row":{"timestamp":169.834490154,"waypoint_count":101,"is_blocked":false,"blocked_waypoint_events":0,"closest_object_distance":0.0,"closest_object_velocity":0.0,"stop_line_ids":[4294967295]}},"closest_available_object_info":"unknown","evidence_of_braking_or_stopping":{"vehicle_status_brake_nonzero":false,"vehicle_cmd_brake_nonzero":false,"speed_decreases_within_window":true}},"red_light_window":{"red_light_violation_from_error_json":true,"red_light_violation_timestamp":"unknown","traffic_lights_topic_exists":true,"traffic_light_state_samples":[{"timestamp":"166.384490103","traffic_light_count":36,"state_histogram":{"0":26,"1":10},"sample":[{"id":18681,"state":0},{"id":18682,"state":0},{"id":18683,"state":0},{"id":18684,"state":0},{"id":18685,"state":0}]},{"timestamp":"166.434490104","traffic_light_count":36,"state_histogram":{"0":36},"sample":[{"id":18681,"state":0},{"id":18682,"state":0},{"id":18683,"state":0},{"id":18684,"state":0},{"id":18685,"state":0}]},{"timestamp":"168.434490134","traffic_light_count":36,"state_histogram":{"0":34,"2":2},"sample":[{"id":18681,"state":0},{"id":18682,"state":0},{"id":18683,"state":2},{"id":18684,"state":0},{"id":18685,"state":0}]},{"timestamp":"168.484490134","traffic_light_count":36,"state_histogram":{"0":24,"2":12},"sample":[{"id":18681,"state":0},{"id":18682,"state":0},{"id":18683,"state":2},{"id":18684,"state":0},{"id":18685,"state":0}]}],"route_light_relation_confirmed":"unknown","stop_line_crossing_confirmed":"unknown","nearest_final_waypoints_stop_line_ids":[4294967295],"notes":"Traffic light states may be available, but route-light relation and stop-line crossing are not confirmed by the current summaries."},"label_conflict":{"dataset_group":"L+R","error_json_group":"R","conflict_details":"lane_invasion: dataset=1, error_json=0; group: dataset=L+R, error_json=R","needs_manual_review":true,"guidance":"Use this case as uncertainty-aware Phase 1 input unless manual review resolves the conflict."}},"trace_summary_compact":{"sensing":{"image_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":600,"width":800,"encoding":"bgra8"},"time_range":["5.334487703","171.284490176"]},"points_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":1,"width":8377,"point_step":16},"time_range":["5.384487704","171.234490175"]}},"perception":{"detection_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"15.784487859","last_timestamp":"171.134490174","object_count_range":{"min":1.0,"max":3.0},"object_count_avg_sample":1.195,"labels_sample":["car","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":77}},"prediction_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"15.784487859","last_timestamp":"171.134490174","object_count_range":{"min":1.0,"max":22.0},"object_count_avg_sample":4.745,"labels_sample":["car","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":651}},"current_pose":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"9.334487763","last_timestamp":"171.234490175","start_position":{"x":104.86711120605469,"y":-60.000370025634766,"z":0.03951001167297363},"end_position_sample":{"x":112.84905242919922,"y":-59.53872299194336,"z":0.0362851619720459}}},"planning":{"final_waypoints":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"13.434487824","last_timestamp":"171.134490174","waypoint_count_range":{"min":101.0,"max":101.0},"blocked_true_count_sample":0,"null_rows_sample":0},"lane_waypoints_array":{"exists":true,"rows_sampled":1,"sample_truncated":false,"first_timestamp":"12.434487809","last_timestamp":"12.434487809","lane_count_range":{"min":1.0,"max":1.0},"primary_lane_waypoint_count_range":{"min":775.0,"max":775.0},"null_rows_sample":0}},"actuation":{"vehicle_cmd":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"10.384487778","last_timestamp":"171.284490176","steer_cmd_range":{"min":0.0,"max":0.0},"accel_cmd_range":{"min":0.0,"max":0.0},"brake_cmd_range":{"min":0.0,"max":0.0},"target_speed_range":{"min":0.0,"max":0.0}},"vehicle_status":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.384487689","last_timestamp":"171.284490176","velocity_range":{"min":0.0,"max":8.779693603515625},"throttle_range":{"min":0.0,"max":0.0},"brake_range":{"min":0.0,"max":0.0},"steer_range":{"min":-0.13777735829353333,"max":0.0}}},"oracle":{"collision":{"exists":true,"rows_sampled":34,"sample_truncated":false,"first_timestamp":"169.884490155","last_timestamp":"171.234490175","other_actor_ids_sample":["0"],"impulse_magnitude_range":{"min":49.1344891351581,"max":5512.534456633162}},"traffic_lights":{"exists":true,"rows_sampled":67,"sample_truncated":false,"first_timestamp":"4.334487688","last_timestamp":"168.484490134","traffic_light_count_range":{"min":36.0,"max":36.0},"state_sample":["0","1","2"]},"odometry":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.334487688","last_timestamp":"171.284490176","start_position":{"x":104.8687973022461,"y":-59.9901008605957,"z":3.484511613845825},"end_position_sample":{"x":104.86888122558594,"y":-59.98720932006836,"z":0.035760726779699326}},"objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.334487688","last_timestamp":"171.284490176","object_count_range":{"min":1.0,"max":1.0},"object_count_avg_sample":1.0,"labels_sample":[],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":0}},"error_json_events":{"crash":false,"stuck":false,"lane_invasion":false,"red":true,"speeding":false,"other":"goal","other_error_val":3.999661684036255}}},"known_limitations":["Dataset labels and error.json oracle events are not fully aligned for some cases.","Dataset.xlsx and error.json are inconsistent for this case; Phase 1 must explicitly mark uncertainty.","Dataset.xlsx and error.json oracle labels are compared separately; conflicts are preserved rather than resolved automatically.","Large CSV topics were summarized with bounded scans for reproducibility and memory safety.","Sensor and perception topics are summarized where available; large raw arrays are not included in prompts."],"manual_phase1_status":{"candidate_generation_status":null,"oracle_consistency_status":null,"known_limitations":[]}}