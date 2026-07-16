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
{"case_id":"case_151","fault_label":{"collision":0,"stuck":1,"lane_invasion":1,"red_light":0,"group":"S+L"},"oracle_consistency":{"status":"dataset_only","dataset_group":"S+L","error_json_group":"none","conflict_details":"stuck: dataset=1, error_json=0; lane_invasion: dataset=1, error_json=0; group: dataset=S+L, error_json=none","suggested_action":"needs_manual_review"},"scenario_config":{"map":"Town01","mission":{"start":{"sp_x":46.14997863769531,"sp_y":326.9700012207031,"sp_z":0.29999998211860657,"yaw":179.999755859375},"goal":{"wp_x":60.10997772216797,"wp_y":330.4599914550781,"wp_z":0.29999998211860657,"wp_yaw":-9.1552734375e-05}},"actors":"2 actor(s)","weather":{"cloud":61,"rain":10,"puddle":19,"wind":27,"fog":27,"wetness":69,"angle":260,"altitude":2},"puddles":"2 puddle region(s)"},"available_topics":["/carla/ego_vehicle/imu/imu","/image_raw","/points_raw","/detection/fusion_tools/objects","/current_pose","/prediction/motion_predictor/objects","/lane_waypoints_array","/final_waypoints","/vehicle_cmd","/carla/ego_vehicle/vehicle_status","/carla/ego_vehicle/odometry","/carla/objects","/carla/traffic_lights"],"critical_window_summary":{"case_id":"case_151","dataset_group":"S+L","oracle_consistency_status":"dataset_only","error_json_events":{"crash":false,"stuck":false,"lane_invasion":false,"red":false,"speeding":false,"other":"goal","other_error_val":58.39779281616211},"stuck_window":{"stuck_from_error_json":false,"total_duration_sec":154.05,"last_60_seconds_window":{"start_timestamp":"114.684093207","end_timestamp":"174.684093207","ego_movement_distance":56.113,"ego_start_to_end_displacement":7.574,"velocity_stats":{"min":0.0,"max":2.790019,"mean":0.131645,"last":0.44327},"vehicle_status_control_stats":{"throttle":{"min":0.0,"max":0.461745,"mean":0.028061,"last":0.041529},"brake":{"min":0.0,"max":0.871963,"mean":0.074331,"last":0.0},"steer":{"min":-0.762768,"max":0.581766,"mean":0.295497,"last":-0.762768}},"vehicle_cmd_stats":{"accel_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"brake_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0},"steer_cmd":{"min":0.0,"max":0.0,"mean":0.0,"last":0.0}},"final_waypoints_present":true,"final_waypoint_count_stats":{"min":101,"max":101,"mean":101.0,"last":101}},"collision_or_red_light_interference":{"error_json_collision":false,"error_json_red":false,"collision_topic_exists":false}},"label_conflict":{"dataset_group":"S+L","error_json_group":"none","conflict_details":"stuck: dataset=1, error_json=0; lane_invasion: dataset=1, error_json=0; group: dataset=S+L, error_json=none","needs_manual_review":true,"guidance":"Use this case as uncertainty-aware Phase 1 input unless manual review resolves the conflict."}},"trace_summary_compact":{"sensing":{"image_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":600,"width":800,"encoding":"bgra8"},"time_range":["5.934090692","174.684093207"]},"points_raw":{"exists":true,"decode_status":"not_attempted","shape":{"height":1,"width":8180,"point_step":16},"time_range":["5.884090691","174.684093207"]}},"perception":{"detection_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"13.884090811","last_timestamp":"174.684093207","object_count_range":{"min":1.0,"max":2.0},"object_count_avg_sample":1.99,"labels_sample":["car","person","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":67}},"prediction_objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"13.884090811","last_timestamp":"174.684093207","object_count_range":{"min":1.0,"max":12.0},"object_count_avg_sample":5.34,"labels_sample":["car","person","unknown"],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":604}},"current_pose":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"13.834090810","last_timestamp":"174.684093207","start_position":{"x":46.15689468383789,"y":-326.97998046875,"z":0.03189992904663086},"end_position_sample":{"x":46.15875244140625,"y":-326.974853515625,"z":0.03190970420837402}}},"planning":{"final_waypoints":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"18.084090873","last_timestamp":"174.684093207","waypoint_count_range":{"min":101.0,"max":101.0},"blocked_true_count_sample":0,"null_rows_sample":0},"lane_waypoints_array":{"exists":true,"rows_sampled":1,"sample_truncated":false,"first_timestamp":"17.384090863","last_timestamp":"17.384090863","lane_count_range":{"min":1.0,"max":1.0},"primary_lane_waypoint_count_range":{"min":1152.0,"max":1152.0},"null_rows_sample":0}},"actuation":{"vehicle_cmd":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"15.784090839","last_timestamp":"174.684093207","steer_cmd_range":{"min":0.0,"max":0.0},"accel_cmd_range":{"min":0.0,"max":0.0},"brake_cmd_range":{"min":0.0,"max":0.0},"target_speed_range":{"min":0.0,"max":0.0}},"vehicle_status":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"6.734090704","last_timestamp":"174.684093207","velocity_range":{"min":0.0,"max":0.0},"throttle_range":{"min":0.0,"max":0.0},"brake_range":{"min":0.0,"max":0.0},"steer_range":{"min":0.0,"max":0.0}}},"oracle":{"collision":null,"traffic_lights":{"exists":true,"rows_sampled":67,"sample_truncated":false,"first_timestamp":"4.434090670","last_timestamp":"168.534093115","traffic_light_count_range":{"min":36.0,"max":36.0},"state_sample":["0","1","2"]},"odometry":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"5.934090692","last_timestamp":"174.684093207","start_position":{"x":46.14717483520508,"y":-326.9722595214844,"z":0.03155948594212532},"end_position_sample":{"x":46.149940490722656,"y":-326.9721984863281,"z":0.03581890091300011}},"objects":{"exists":true,"rows_sampled":200,"sample_truncated":true,"first_timestamp":"4.334090668","last_timestamp":"174.684093207","object_count_range":{"min":0.0,"max":3.0},"object_count_avg_sample":2.61,"labels_sample":[],"embedded_payload_presence_sample":{"roi_image":0,"pointcloud":0}},"error_json_events":{"crash":false,"stuck":false,"lane_invasion":false,"red":false,"speeding":false,"other":"goal","other_error_val":58.39779281616211}}},"known_limitations":["Dataset labels and error.json oracle events are not fully aligned for some cases.","Dataset.xlsx and error.json are inconsistent for this case; Phase 1 must explicitly mark uncertainty.","Dataset.xlsx and error.json oracle labels are compared separately; conflicts are preserved rather than resolved automatically.","Large CSV topics were summarized with bounded scans for reproducibility and memory safety.","Sensor and perception topics are summarized where available; large raw arrays are not included in prompts."],"manual_phase1_status":{"candidate_generation_status":null,"oracle_consistency_status":null,"known_limitations":[]}}