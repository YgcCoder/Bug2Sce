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
{"case_id":"case_004","fault_label":{"collision":0,"stuck":0,"lane_invasion":1,"red_light":1,"group":"L+R"},"oracle_consistency":{"status":"dataset_only","dataset_group":"L+R","error_json_group":"R","conflict_details":"lane_invasion: dataset=1, error_json=0; group: dataset=L+R, error_json=R","suggested_action":"needs_manual_review"},"scenario_config":{"map":"Town01","mission":{"start":{"sp_x":322.09625244140625,"sp_y":129.35906982421875,"sp_z":1.5,"yaw":-179.99993896484375},"goal":{"wp_x":283.6458740234375,"wp_y":133.43006896972656,"wp_z":1.5,"wp_yaw":-179.99993896484375}},"actors":"0 actor(s)","weather":{"cloud":24,"rain":7,"puddle":9,"wind":93,"fog":19,"wetness":29,"angle":105,"altitude":71},"puddles":"1 puddle region(s)"},"available_topics":["/carla/ego_vehicle/imu/imu","/image_raw","/points_raw","/detection/fusion_tools/objects","/current_pose","/prediction/motion_predictor/objects","/lane_waypoints_array","/final_waypoints","/vehicle_cmd","/carla/ego_vehicle/vehicle_status","/carla/ego_vehicle/odometry","/carla/objects","/carla/traffic_lights"],"critical_window_summary":{"case_id":"case_004","dataset_group":"L+R","oracle_consistency_status":"dataset_only","error_json_events":{"crash":false,"stuck":false,"lane_invasion":false,"red":true,"speeding":false,"other":"goal","other_error_val":70.26366424560547},"red_light_window":{"red_light_violation_from_error_json":true,"red_light_violation_timestamp":"unknown","traffic_lights_topic_exists":true,"traffic_light_state_samples":[{"timestamp":"123.213355574","traffic_light_count":36,"state_histogram":{"0":24,"2":12},"sample":[{"id":11691,"state":0},{"id":11692,"state":0},{"id":11693,"state":2},{"id":11694,"state":0},{"id":11695,"state":0}]}],"route_light_relation_confirmed":"unknown","stop_line_crossing_confirmed":"unknown","nearest_final_waypoints_stop_line_ids":[4294967295],"notes":"Traffic light states may be available, but route-light relation and stop-line crossing are not confirmed by the current summaries."},"label_conflict":{"dataset_group":"L+R","error_json_group":"R","conflict_details":"lane_invasion: dataset=1, error_json=0; group: dataset=L+R, error_json=R","needs_manual_review":true,"guidance":"Use this case as uncertainty-aware Phase 1 input unless manual review resolves the conflict."}},"trace_summary_compact":{"sensing":{"image_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":600,"width":800,"encoding":"bgra8"},"time_range":["4.813353810","126.663355626"]},"points_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":1,"width":8023,"point_step":16},"time_range":["4.813353810","126.663355626"]}},"perception":{"detection_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"8.963353872","last_timestamp":"126.563355624","object_count_range":{"min":1.0,"max":3.0},"object_count_avg_sample":1.21,"labels_sample":["bus","person","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":157}},"prediction_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"8.963353872","last_timestamp":"126.563355624","object_count_range":{"min":1.0,"max":23.0},"object_count_avg_sample":8.76,"labels_sample":["bus","person","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":1348}},"current_pose":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"8.763353869","last_timestamp":"126.663355626","start_position":{"x":322.09136962890625,"y":-129.3650360107422,"z":0.03236865997314453},"end_position_sample":{"x":313.8123474121094,"y":-129.4969940185547,"z":0.030717849731445312}}},"planning":{"final_waypoints":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"12.863353930","last_timestamp":"126.563355624","waypoint_count_range":{"min":101.0,"max":101.0},"blocked_true_count_sample":0,"null_rows_sample":0},"lane_waypoints_array":{"exists":true,"rows_sampled":1,"sample_truncated":false,"first_timestamp":"12.213353920","last_timestamp":"12.213353920","lane_count_range":{"min":1.0,"max":1.0},"primary_lane_waypoint_count_range":{"min":656.0,"max":656.0},"null_rows_sample":0}},"actuation":{"vehicle_cmd":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"9.863353885","last_timestamp":"126.663355626","steer_cmd_range":{"min":0.0,"max":0.0},"accel_cmd_range":{"min":0.0,"max":0.0},"brake_cmd_range":{"min":0.0,"max":0.0},"target_speed_range":{"min":0.0,"max":0.0}},"vehicle_status":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"5.413353819","last_timestamp":"126.663355626","velocity_range":{"min":0.0,"max":0.03804008290171623},"throttle_range":{"min":0.0,"max":0.4937359094619751},"brake_range":{"min":0.0,"max":0.0},"steer_range":{"min":-0.04207170009613037,"max":0.0}}},"oracle":{"collision":null,"traffic_lights":{"exists":true,"rows_sampled":25,"sample_truncated":false,"first_timestamp":"4.113353800","last_timestamp":"123.213355574","traffic_light_count_range":{"min":36.0,"max":36.0},"state_sample":["0","1","2"]},"odometry":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.963353812","last_timestamp":"126.663355626","start_position":{"x":322.09625244140625,"y":-129.3590545654297,"z":0.06012042984366417},"end_position_sample":{"x":322.0962219238281,"y":-129.35940551757812,"z":0.035792578011751175}},"objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.163353800","last_timestamp":"126.663355626","object_count_range":{"min":1.0,"max":1.0},"object_count_avg_sample":1.0,"labels_sample":[],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":0}},"error_json_events":{"crash":false,"stuck":false,"lane_invasion":false,"red":true,"speeding":false,"other":"goal","other_error_val":70.26366424560547}}},"known_limitations":["Dataset labels and error.json oracle events are not fully aligned for some cases.","Dataset.xlsx and error.json are inconsistent for this case; Phase 1 must explicitly mark uncertainty.","Dataset.xlsx and error.json oracle labels are compared separately; conflicts are preserved rather than resolved automatically.","Large CSV topics were summarized with bounded scans for reproducibility and memory safety.","Sensor and perception topics are summarized where available; large raw arrays are not included in prompts."],"manual_phase1_status":{"candidate_generation_status":null,"oracle_consistency_status":null,"known_limitations":[]}}