# RQ3 Matched Comparison Summary

Matched budget: 30 seeds x 6 models x 1 candidate = 180 candidates per method.

| Method | Generated | JSON-valid | Output dirs | Camera | Rosbag | Oracle-triggered | Root-cause review pool | Different failure | No oracle/incomplete | Invalid/crash |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Pure-LLM generation | 180 | 180 | 180 | 173 | 94 | 87 | 72 | 15 | 87 | 6 |
| Bug2Scenario matched cand_001 | 180 | 180 | 180 | 177 | 101 | 94 | 84 | 10 | 78 | 8 |

The root-cause review pool is not final same-root-cause ground truth. It includes exact/superset/partial oracle-match candidates that still require manual video/trace confirmation.
