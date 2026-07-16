# Representative video pair

This directory provides a compact visual example corresponding to the qualitative comparison in Fig. 1 of the paper. The two clips hold the seed and model fixed (`case_098`, Claude Sonnet 4.5) while comparing the generation method:

| File | Method | Final manual outcome |
|---|---|---|
| `case_098_pure_llm_not_preserved_front.mp4` | Pure-LLM | not preserved |
| `case_098_bug2scenario_strict_front.mp4` | Bug2Scenario | strictly preserved |

Both files are metadata-filtered 640x480 front-view transcodes. They are illustrative examples, not a cherry-picked quantitative subset: the repository includes the complete candidate JSON and final label tables used for all reported rates. The full videos, rosbags, images, and simulator directories occupy approximately 2.8 TB and are excluded from normal Git distribution as documented in `docs/RAW_ARTIFACTS.md`.
