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
{"case_id":"case_156","fault_label":{"collision":0,"stuck":1,"lane_invasion":0,"red_light":0,"group":"S"},"oracle_consistency":{"status":"consistent","dataset_group":"S","error_json_group":"S","conflict_details":"all comparable labels match","suggested_action":"no_action_needed"},"scenario_config":{"map":"Town01","mission":{"start":{"sp_x":301.3399658203125,"sp_y":330.53997802734375,"sp_z":0.29999998211860657,"yaw":-9.1552734375e-05},"goal":{"wp_x":339.01873779296875,"wp_y":116.54576110839844,"wp_z":0.29999998211860657,"wp_yaw":-89.99993896484375}},"actors":"1 actor(s)","weather":{"cloud":48,"rain":15,"puddle":18,"wind":74,"fog":2,"wetness":7,"angle":77,"altitude":32},"puddles":"3 puddle region(s)"},"available_topics":["/carla/ego_vehicle/imu/imu","/image_raw","/points_raw","/detection/fusion_tools/objects","/current_pose","/prediction/motion_predictor/objects","/lane_waypoints_array","/final_waypoints","/vehicle_cmd","/carla/ego_vehicle/vehicle_status","/carla/ego_vehicle/odometry","/carla/objects","/carla/traffic_lights"],"critical_window_summary":{"case_id":"case_156","dataset_group":"S","oracle_consistency_status":"consistent","error_json_events":{"crash":false,"stuck":true,"lane_invasion":false,"red":false,"speeding":false,"other":false,"other_error_val":0},"stuck_window":{"stuck_from_error_json":true,"total_duration_sec":237.15,"last_60_seconds_window":{"start_timestamp":"197.242886875","end_timestamp":"257.242886875","ego_movement_distance":11.834,"ego_start_to_end_displacement":0.01,"velocity_stats":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"vehicle_status_control_stats":{"throttle":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"brake":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0}},"vehicle_cmd_stats":{"accel_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"brake_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0}},"final_waypoints_present":true,"final_waypoint_count_stats":{"min":101,"max":101,"mean":101.0,"last":101}},"collision_or_red_light_interference":{"error_json_collision":false,"error_json_red":false,"collision_topic_exists":false}}},"trace_summary_compact":{"sensing":{"image_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":600,"width":800,"encoding":"bgra8"},"time_range":["5.642883126","257.192886875"]},"points_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":1,"width":8132,"point_step":16},"time_range":["4.642883111","257.192886875"]}},"perception":{"detection_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"12.692883231","last_timestamp":"257.242886875","object_count_range":{"min":1.0,"max":3.0},"object_count_avg_sample":1.995,"labels_sample":["car","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":138}},"prediction_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"12.692883231","last_timestamp":"257.242886875","object_count_range":{"min":1.0,"max":33.0},"object_count_avg_sample":8.895,"labels_sample":["car","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":690}},"current_pose":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"12.642883230","last_timestamp":"257.192886875","start_position":{"x":301.33599853515625,"y":-330.51983642578125,"z":0.033040523529052734},"end_position_sample":{"x":301.3434143066406,"y":-330.509033203125,"z":0.03161931037902832}}},"planning":{"final_waypoints":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"17.392883301","last_timestamp":"257.192886875","waypoint_count_range":{"min":101.0,"max":101.0},"blocked_true_count_sample":0,"null_rows_sample":0},"lane_waypoints_array":{"exists":true,"rows_sampled":1,"sample_truncated":false,"first_timestamp":"16.942883295","last_timestamp":"16.942883295","lane_count_range":{"min":1.0,"max":1.0},"primary_lane_waypoint_count_range":{"min":592.0,"max":592.0},"null_rows_sample":0}},"actuation":{"vehicle_cmd":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"15.692883276","last_timestamp":"257.242886875","steer_cmd_range":{"min":0.0,"max":0.0},"accel_cmd_range":{"min":0.0,"max":0.0},"brake_cmd_range":{"min":0.0,"max":0.0},"target_speed_range":{"min":0.0,"max":0.0}},"vehicle_status":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"5.342883122","last_timestamp":"257.242886875","velocity_range":{"min":0.0,"max":0.010814417153596878},"throttle_range":{"min":0.0,"max":0.0},"brake_range":{"min":0.0,"max":0.0},"steer_range":{"min":0.0,"max":0.0}}},"oracle":{"collision":null,"traffic_lights":{"exists":true,"rows_sampled":51,"sample_truncated":false,"first_timestamp":"4.042883102","last_timestamp":"256.692886867","traffic_light_count_range":{"min":36.0,"max":36.0},"state_sample":["0","1","2"]},"odometry":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.742883113","last_timestamp":"257.242886875","start_position":{"x":301.3399658203125,"y":-330.5399475097656,"z":-0.037394940853118896},"end_position_sample":{"x":301.3399353027344,"y":-330.5376892089844,"z":0.03580161929130554}},"objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"3.942883101","last_timestamp":"257.242886875","object_count_range":{"min":0.0,"max":2.0},"object_count_avg_sample":1.865,"labels_sample":[],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":0}},"error_json_events":{"crash":false,"stuck":true,"lane_invasion":false,"red":false,"speeding":false,"other":false,"other_error_val":0}}},"known_limitations":["Dataset labels and error.json oracle events are not fully aligned for some cases.","Dataset.xlsx and error.json oracle labels are compared separately; conflicts are preserved rather than resolved automatically.","Large CSV topics were summarized with bounded scans for reproducibility and memory safety.","Sensor and perception topics are summarized where available; large raw arrays are not included in prompts."],"manual_phase1_status":{"candidate_generation_status":null,"oracle_consistency_status":null,"known_limitations":[]}}