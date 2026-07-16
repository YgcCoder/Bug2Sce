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
{"case_id":"case_068","fault_label":{"collision":0,"stuck":0,"lane_invasion":0,"red_light":1,"group":"R"},"oracle_consistency":{"status":"consistent","dataset_group":"R","error_json_group":"R","conflict_details":"all comparable labels match","suggested_action":"no_action_needed"},"scenario_config":{"map":"Town01","mission":{"start":{"sp_x":104.8687973022461,"sp_y":59.99010467529297,"sp_z":0.29999998211860657,"yaw":0.0},"goal":{"wp_x":392.4700012207031,"wp_y":105.38999938964844,"wp_z":0.29999998211860657,"wp_yaw":90.00004577636719}},"actors":"1 actor(s)","weather":{"cloud":13,"rain":10,"puddle":13,"wind":71,"fog":19,"wetness":26,"angle":199,"altitude":29},"puddles":"0 puddle region(s)"},"available_topics":["/carla/ego_vehicle/imu/imu","/image_raw","/points_raw","/detection/fusion_tools/objects","/current_pose","/prediction/motion_predictor/objects","/lane_waypoints_array","/final_waypoints","/vehicle_cmd","/carla/ego_vehicle/vehicle_status","/carla/ego_vehicle/odometry","/carla/objects","/carla/traffic_lights"],"critical_window_summary":{"case_id":"case_068","dataset_group":"R","oracle_consistency_status":"consistent","error_json_events":{"crash":false,"stuck":false,"lane_invasion":false,"red":true,"speeding":false,"other":"goal","other_error_val":4.082779884338379},"red_light_window":{"red_light_violation_from_error_json":true,"red_light_violation_timestamp":"unknown","traffic_lights_topic_exists":true,"traffic_light_state_samples":[{"timestamp":"163.272704372","traffic_light_count":36,"state_histogram":{"0":24,"1":12},"sample":[{"id":801,"state":0},{"id":802,"state":1},{"id":803,"state":0},{"id":804,"state":0},{"id":805,"state":1}]},{"timestamp":"166.322704417","traffic_light_count":36,"state_histogram":{"0":36},"sample":[{"id":801,"state":0},{"id":802,"state":0},{"id":803,"state":0},{"id":804,"state":0},{"id":805,"state":0}]}],"route_light_relation_confirmed":"unknown","stop_line_crossing_confirmed":"unknown","nearest_final_waypoints_stop_line_ids":[4294967295],"notes":"Traffic light states may be available, but route-light relation and stop-line crossing are not confirmed by the current summaries."}},"trace_summary_compact":{"sensing":{"image_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":600,"width":800,"encoding":"bgra8"},"time_range":["4.572702007","167.522704435"]},"points_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":1,"width":8325,"point_step":16},"time_range":["4.572702007","167.522704435"]}},"perception":{"detection_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"9.772702084","last_timestamp":"164.672704393","object_count_range":{"min":1.0,"max":4.0},"object_count_avg_sample":1.32,"labels_sample":["car","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":149}},"prediction_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"9.772702084","last_timestamp":"164.672704393","object_count_range":{"min":1.0,"max":24.0},"object_count_avg_sample":8.77,"labels_sample":["car","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":1272}},"current_pose":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"9.522702081","last_timestamp":"167.522704435","start_position":{"x":104.86756896972656,"y":-59.99612808227539,"z":0.03567838668823242},"end_position_sample":{"x":113.2129135131836,"y":-59.534889221191406,"z":0.03435325622558594}}},"planning":{"final_waypoints":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"13.522702140","last_timestamp":"167.522704435","waypoint_count_range":{"min":101.0,"max":101.0},"blocked_true_count_sample":0,"null_rows_sample":0},"lane_waypoints_array":{"exists":true,"rows_sampled":1,"sample_truncated":false,"first_timestamp":"12.772702129","last_timestamp":"12.772702129","lane_count_range":{"min":1.0,"max":1.0},"primary_lane_waypoint_count_range":{"min":775.0,"max":775.0},"null_rows_sample":0}},"actuation":{"vehicle_cmd":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"10.572702096","last_timestamp":"167.522704435","steer_cmd_range":{"min":0.0,"max":0.0},"accel_cmd_range":{"min":0.0,"max":0.0},"brake_cmd_range":{"min":0.0,"max":0.0},"target_speed_range":{"min":0.0,"max":0.0}},"vehicle_status":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.622702008","last_timestamp":"167.522704435","velocity_range":{"min":0.0,"max":5.731531143188477},"throttle_range":{"min":0.0,"max":0.045950960367918015},"brake_range":{"min":0.0,"max":0.0},"steer_range":{"min":-0.13801032304763794,"max":0.0}}},"oracle":{"collision":null,"traffic_lights":{"exists":true,"rows_sampled":33,"sample_truncated":false,"first_timestamp":"3.972701998","last_timestamp":"166.322704417","traffic_light_count_range":{"min":36.0,"max":36.0},"state_sample":["0","1","2"]},"odometry":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.622702008","last_timestamp":"167.522704435","start_position":{"x":104.8687973022461,"y":-59.9901008605957,"z":-0.037394940853118896},"end_position_sample":{"x":104.86883544921875,"y":-59.98789596557617,"z":0.03579036518931389}},"objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"3.972701998","last_timestamp":"167.522704435","object_count_range":{"min":1.0,"max":2.0},"object_count_avg_sample":1.92,"labels_sample":[],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":0}},"error_json_events":{"crash":false,"stuck":false,"lane_invasion":false,"red":true,"speeding":false,"other":"goal","other_error_val":4.082779884338379}}},"known_limitations":["Dataset labels and error.json oracle events are not fully aligned for some cases.","Dataset.xlsx and error.json oracle labels are compared separately; conflicts are preserved rather than resolved automatically.","Large CSV topics were summarized with bounded scans for reproducibility and memory safety.","Sensor and perception topics are summarized where available; large raw arrays are not included in prompts."],"manual_phase1_status":{"candidate_generation_status":null,"oracle_consistency_status":null,"known_limitations":[]}}