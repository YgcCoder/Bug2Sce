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
{"case_id":"case_001","fault_label":{"collision":1,"stuck":0,"lane_invasion":0,"red_light":0,"group":"C"},"oracle_consistency":{"status":"consistent","dataset_group":"C","error_json_group":"C","conflict_details":"all comparable labels match","suggested_action":"no_action_needed"},"scenario_config":{"map":"Town01","mission":{"start":{"sp_x":104.8687973022461,"sp_y":59.99010467529297,"sp_z":0.29999998211860657,"yaw":0.0},"goal":{"wp_x":392.4700012207031,"wp_y":105.38999938964844,"wp_z":0.29999998211860657,"wp_yaw":90.00004577636719}},"actors":"1 actor(s)","weather":{"cloud":25,"rain":5,"puddle":8,"wind":45,"fog":0,"wetness":15,"angle":220,"altitude":55},"puddles":"1 puddle region(s)"},"available_topics":["/carla/ego_vehicle/imu/imu","/image_raw","/points_raw","/detection/fusion_tools/objects","/current_pose","/prediction/motion_predictor/objects","/lane_waypoints_array","/final_waypoints","/vehicle_cmd","/carla/ego_vehicle/vehicle_status","/carla/ego_vehicle/collision","/carla/ego_vehicle/odometry","/carla/objects","/carla/traffic_lights"],"critical_window_summary":{"case_id":"case_001","dataset_group":"C","oracle_consistency_status":"consistent","error_json_events":{"crash":true,"stuck":false,"lane_invasion":false,"red":false,"speeding":false,"other":false,"other_error_val":0},"collision_window":{"collision_timestamp":"21.599057735","window_start":"16.599057735","window_end":"21.599057735","collision_topic_exists":true,"error_json_crash":true,"ego_speed_before_collision":{"nearest_pre_collision_velocity":0.0,"window_velocity_stats":{"min":0.0,"max":1.066768,"mean":0.142226,"last":0.0}},"ego_control_before_collision":{"vehicle_status_control_stats":{"throttle":{"min":0.0,"max":0.554975,"mean":0.026413,"last":0.0},"brake":{"min":0.0,"max":0.097943,"mean":0.01551,"last":0.013015},"steer":{"min":-0.133866,"max":-0.0,"mean":-0.002677,"last":-0.0}},"vehicle_cmd_stats":{"accel_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"brake_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"linear_velocity_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0}}},"detected_object_count_before_collision":{"rows":135,"count_stats":{"min":1.0,"max":1.0,"mean":1.0,"last":1.0},"labels_sample":["car","unknown"]},"predicted_object_count_before_collision":{"rows":135,"count_stats":{"min":1.0,"max":11.0,"mean":4.851852,"last":11.0},"labels_sample":["car","unknown"]},"final_waypoints_before_collision":{"rows":35,"waypoint_count_stats":{"min":101.0,"max":101.0,"mean":101.0,"last":101.0},"blocked_true_count_rows":0,"blocked_true_count_nonzero":false,"blocked_waypoint_event_total":0,"nearest_pre_collision_row":{"timestamp":21.599057735,"waypoint_count":101,"is_blocked":false,"blocked_waypoint_events":0,"closest_object_distance":0.0,"closest_object_velocity":0.0,"stop_line_ids":[4294967295]}},"closest_available_object_info":{"object_id":6695,"classification":6,"distance_to_ego":4.516,"position":{"x":110.098,"y":-60.165,"z":0.074}},"evidence_of_braking_or_stopping":{"vehicle_status_brake_nonzero":true,"vehicle_cmd_brake_nonzero":false,"speed_decreases_within_window":true}}},"trace_summary_compact":{"sensing":{"image_raw":{"exists":true,"decode_status":"decoded 325 frame(s)","shape":{"height":600,"width":800,"encoding":"bgra8"},"time_range":["6.099057504","22.299057746"]},"points_raw":{"exists":true,"decode_status":"decoded 325 frame(s)","shape":{"height":1,"width":8270,"point_step":16},"time_range":["6.099057504","22.249057745"]}},"perception":{"detection_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"10.399057568","last_timestamp":"22.199057744","object_count_range":{"min":1.0,"max":2.0},"object_count_avg_sample":1.005,"labels_sample":["car","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":58}},"prediction_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"10.399057568","last_timestamp":"22.199057744","object_count_range":{"min":1.0,"max":11.0},"object_count_avg_sample":3.905,"labels_sample":["car","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":580}},"current_pose":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"11.049057578","last_timestamp":"22.249057745","start_position":{"x":104.87104034423828,"y":-59.98575973510742,"z":0.03771495819091797},"end_position_sample":{"x":105.58284759521484,"y":-59.98450469970703,"z":0.036203622817993164}}},"planning":{"final_waypoints":{"exists":true,"rows_sampled":64,"sample_truncated":false,"first_timestamp":"13.899057621","last_timestamp":"22.299057746","waypoint_count_range":{"min":101.0,"max":101.0},"blocked_true_count_sample":0,"null_rows_sample":0},"lane_waypoints_array":{"exists":true,"rows_sampled":1,"sample_truncated":false,"first_timestamp":"13.599057616","last_timestamp":"13.599057616","lane_count_range":{"min":1.0,"max":1.0},"primary_lane_waypoint_count_range":{"min":775.0,"max":775.0},"null_rows_sample":0}},"actuation":{"vehicle_cmd":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"12.049057593","last_timestamp":"22.299057746","steer_cmd_range":{"min":0.0,"max":0.0},"accel_cmd_range":{"min":0.0,"max":0.0},"brake_cmd_range":{"min":0.0,"max":0.0},"target_speed_range":{"min":0.0,"max":0.0}},"vehicle_status":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"6.199057506","last_timestamp":"22.299057746","velocity_range":{"min":0.0,"max":8.779693603515625},"throttle_range":{"min":0.0,"max":0.3750952184200287},"brake_range":{"min":0.0,"max":0.0},"steer_range":{"min":-0.13842788338661194,"max":0.0}}},"oracle":{"collision":{"exists":true,"rows_sampled":4,"sample_truncated":false,"first_timestamp":"21.599057735","last_timestamp":"21.749057738","other_actor_ids_sample":["6695"],"impulse_magnitude_range":{"min":0.7848722610636772,"max":1528.4274120797768}},"traffic_lights":{"exists":true,"rows_sampled":4,"sample_truncated":false,"first_timestamp":"4.599057482","last_timestamp":"17.549057675","traffic_light_count_range":{"min":36.0,"max":36.0},"state_sample":["0","1","2"]},"odometry":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"6.149057505","last_timestamp":"22.299057746","start_position":{"x":104.8687973022461,"y":-59.9901008605957,"z":0.5101177096366882},"end_position_sample":{"x":104.86888122558594,"y":-59.987205505371094,"z":0.035792846232652664}},"objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.449057480","last_timestamp":"22.299057746","object_count_range":{"min":0.0,"max":2.0},"object_count_avg_sample":1.7,"labels_sample":[],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":0}},"error_json_events":{"crash":true,"stuck":false,"lane_invasion":false,"red":false,"speeding":false,"other":false,"other_error_val":0}}},"known_limitations":["Dataset labels and error.json oracle events are compared separately; conflicts are preserved rather than resolved automatically.","Sensor and perception topics were decoded for selected cases where available; large raw arrays are not included in prompts, only summaries are used.","Large CSV topics are summarized with bounded scans or critical-window extraction for reproducibility and memory safety."],"manual_phase1_status":{"candidate_generation_status":"ready","oracle_consistency_status":"consistent","known_limitations":["Direct planner decision logs are unavailable.","The evidence does not prove whether the collision actor was correctly associated by perception.","Vehicle_cmd is all zero while vehicle_status shows movement/braking, so controller attribution is uncertain."]}}