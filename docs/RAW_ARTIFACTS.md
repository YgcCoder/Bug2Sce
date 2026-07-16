# Raw artifacts excluded from Git

The following simulator artifacts were retained on the experiment disk but intentionally excluded from the Git repository. Together they occupy approximately 2.8 TB:

| Artifact class | Local size at packaging | Reason excluded |
|---|---:|---|
| Bug2Scenario main executions | about 1.0 TB | rosbags, videos, CARLA outputs |
| Pure-LLM executions | about 933 GB | rosbags, videos, CARLA outputs |
| Rd2 executions | about 100 GB | simulator run directories |
| Rd3 executions | about 283 GB | simulator run directories |
| Rd4 executions | about 247 GB | simulator run directories |
| Rd5 executions | about 225 GB | simulator run directories |
| DriveFuzz/CARLA/Autoware backup | about 55 GB | third-party source, builds, images, caches |

The repository instead releases every evaluated executable scenario JSON, candidate metadata, aggregate execution table, final manual label, and the exact DriveFuzz patch. This boundary preserves the evidence needed to audit the paper while avoiding a multi-terabyte clone and redistribution of third-party build trees.

## Representative video pair

Two metadata-filtered front-view clips are included under `examples/videos/`. Both use `case_098` and Claude Sonnet 4.5, matching the qualitative comparison in Fig. 1:

- `case_098_pure_llm_not_preserved_front.mp4`: Pure-LLM; final manual label `not preserved`.
- `case_098_bug2scenario_strict_front.mp4`: Bug2Scenario; final manual label `strictly preserved`.

The clips were transcoded to a common 640x480 presentation format with metadata filtering enabled. They are supplied for visual inspection only; quantitative results are computed from the released normalized tables rather than from these two examples.
