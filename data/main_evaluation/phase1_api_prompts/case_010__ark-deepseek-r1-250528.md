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
{"case_id":"case_010","fault_label":{"collision":0,"stuck":0,"lane_invasion":1,"red_light":0,"group":"L"},"oracle_consistency":{"status":"dataset_only","dataset_group":"L","error_json_group":"none","conflict_details":"lane_invasion: dataset=1, error_json=0; group: dataset=L, error_json=none","suggested_action":"needs_manual_review"},"scenario_config":{"map":"Town01","mission":{"start":{"sp_x":110.0,"sp_y":129.0,"sp_z":1.0,"yaw":180.0},"goal":{"wp_x":113.0,"wp_y":130.0,"wp_z":0.0,"wp_yaw":0.0}},"actors":"0 actor(s)","weather":{"cloud":83,"rain":57,"puddle":74,"wind":30,"fog":3,"wetness":79,"angle":278,"altitude":7},"puddles":"3 puddle region(s)"},"available_topics":["/carla/ego_vehicle/imu/imu","/image_raw","/points_raw","/detection/fusion_tools/objects","/current_pose","/prediction/motion_predictor/objects","/lane_waypoints_array","/final_waypoints","/vehicle_cmd","/carla/ego_vehicle/vehicle_status","/carla/ego_vehicle/odometry","/carla/objects","/carla/traffic_lights"],"critical_window_summary":{"case_id":"case_010","dataset_group":"L","oracle_consistency_status":"dataset_only","error_json_events":{"crash":false,"stuck":false,"lane_invasion":false,"red":false,"speeding":false,"other":"goal","other_error_val":26.216691970825195},"label_conflict":{"dataset_group":"L","error_json_group":"none","conflict_details":"lane_invasion: dataset=1, error_json=0; group: dataset=L, error_json=none","needs_manual_review":true,"guidance":"Use this case as uncertainty-aware Phase 1 input unless manual review resolves the conflict."}},"trace_summary_compact":{"sensing":{"image_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":600,"width":800,"encoding":"bgra8"},"time_range":["6.334101168","35.984101610"]},"points_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":1,"width":8013,"point_step":16},"time_range":["6.334101168","35.984101610"]}},"perception":{"detection_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"11.934101251","last_timestamp":"35.134101597","object_count_range":{"min":1.0,"max":3.0},"object_count_avg_sample":1.365,"labels_sample":["unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":73}},"prediction_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"11.934101251","last_timestamp":"35.134101597","object_count_range":{"min":1.0,"max":23.0},"object_count_avg_sample":4.865,"labels_sample":["unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":562}},"current_pose":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"12.284101257","last_timestamp":"35.984101610","start_position":{"x":110.01091003417969,"y":-128.96424865722656,"z":0.033173561096191406},"end_position_sample":{"x":106.75629425048828,"y":-129.32994079589844,"z":0.03611302375793457}}},"planning":{"final_waypoints":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"15.534101305","last_timestamp":"35.934101609","waypoint_count_range":{"min":101.0,"max":101.0},"blocked_true_count_sample":0,"null_rows_sample":0},"lane_waypoints_array":{"exists":true,"rows_sampled":1,"sample_truncated":false,"first_timestamp":"15.134101299","last_timestamp":"15.134101299","lane_count_range":{"min":1.0,"max":1.0},"primary_lane_waypoint_count_range":{"min":406.0,"max":406.0},"null_rows_sample":0}},"actuation":{"vehicle_cmd":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"13.234101271","last_timestamp":"35.984101610","steer_cmd_range":{"min":0.0,"max":0.0},"accel_cmd_range":{"min":0.0,"max":0.0},"brake_cmd_range":{"min":0.0,"max":0.0},"target_speed_range":{"min":0.0,"max":0.0}},"vehicle_status":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"5.284101152","last_timestamp":"35.984101610","velocity_range":{"min":0.0,"max":8.891582489013672},"throttle_range":{"min":0.0,"max":0.0},"brake_range":{"min":0.0,"max":0.0},"steer_range":{"min":0.0,"max":0.0}}},"oracle":{"collision":null,"traffic_lights":{"exists":true,"rows_sampled":13,"sample_truncated":false,"first_timestamp":"5.884101161","last_timestamp":"33.184101568","traffic_light_count_range":{"min":36.0,"max":36.0},"state_sample":["0","1","2"]},"odometry":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"5.284101152","last_timestamp":"35.984101610","start_position":{"x":110.0,"y":-129.0,"z":4.184512138366699},"end_position_sample":{"x":110.00000762939453,"y":-129.00048828125,"z":0.036415405571460724}},"objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.634101143","last_timestamp":"35.984101610","object_count_range":{"min":0.0,"max":1.0},"object_count_avg_sample":0.965,"labels_sample":[],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":0}},"error_json_events":{"crash":false,"stuck":false,"lane_invasion":false,"red":false,"speeding":false,"other":"goal","other_error_val":26.216691970825195}}},"known_limitations":["Dataset labels and error.json oracle events are not fully aligned for some cases.","Dataset.xlsx and error.json are inconsistent for this case; Phase 1 must explicitly mark uncertainty.","Dataset.xlsx and error.json oracle labels are compared separately; conflicts are preserved rather than resolved automatically.","Large CSV topics were summarized with bounded scans for reproducibility and memory safety.","Sensor and perception topics are summarized where available; large raw arrays are not included in prompts."],"manual_phase1_status":{"candidate_generation_status":null,"oracle_consistency_status":null,"known_limitations":[]}}