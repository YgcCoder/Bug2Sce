# Bug2Scenario artifact

This repository contains the research artifact for **Bug2Scenario: Root-Cause-Preserving Test Scenario Amplification for Autonomous Driving Software**. Bug2Scenario converts a DriveFuzz-discovered failure into auditable regression scenarios while separating LLM-assisted variation from deterministic concretization and execution-based preservation assessment.

## What is included

- `code/bug2scenario/`: seed preparation, prompt construction, API execution, candidate conversion, result parsing, manual-review preparation, and feedback-memory scripts.
- `code/drivefuzz_patch/`: the minimal DriveFuzz integration used to execute full JSON scenarios. The patch is relative to upstream DriveFuzz commit `ae08cc66d6fe0f8bc67ff2d3de55ab3f26809b59`.
- `data/seed_inputs/`: the 30 selected failure seeds, matching critical windows, selection table, root-cause patterns, and model configuration.
- `data/main_evaluation/`: all six-backbone Bug2Scenario and Pure-LLM prompts, API outputs, generated candidates, metadata, and aggregate generation results used by the matched evaluation.
- `data/manual_review/`: execution summaries and the final manual labels used in the paper. Two computer-science PhD students participated in the assessment; the release does not claim independent duplicate labeling or inter-rater agreement.
- `data/feedback_rounds/`: Rd2-Rd5 prompts, API outputs, candidates, metadata, feedback memory, and the executable JSON selected for simulator runs.
- `data/rq4_analysis/`: the standardized two-candidate token audit, iteration outcomes, plotting data, and the exact plotting scripts used for the RQ4 figures.
- `figures/`: two public overview images illustrating the motivating example and the Bug2Scenario workflow.
- `examples/videos/`: a metadata-filtered, same-seed/same-model visual pair corresponding to the qualitative comparison in Fig. 1.

## Evaluation scale

- 30 selected DriveFuzz failure seeds.
- 6 LLM backbones.
- 360 Bug2Scenario candidates in the full main pool (two candidates per seed-model pair).
- A matched 180-candidate Bug2Scenario evaluation and a 180-candidate Pure-LLM comparison.
- 9 initially unsuccessful seeds entering feedback; executable selections contain 18, 42, 36, and 36 JSON scenarios for Rd2-Rd5, respectively.
- Strict preservation counts only `strictly preserved`. Inclusive preservation is the union of `strictly preserved` and `partial or boundary`.

## Quick start

Create an analysis environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Recreate the two RQ4 analysis figures:

```bash
python data/rq4_analysis/plot_rq4_iteration_trajectory.py
python data/rq4_analysis/plot_rq4_token_distribution.py
```

## DriveFuzz integration

Clone the upstream implementation, check out the recorded base commit, and apply the supplied patch:

```bash
git clone https://gitlab.com/s3lab-code/public/drivefuzz.git
cd drivefuzz
git checkout ae08cc66d6fe0f8bc67ff2d3de55ab3f26809b59
git apply ../Bug2Sce/code/drivefuzz_patch/drivefuzz_bug2sce.patch
cp ../Bug2Sce/code/drivefuzz_patch/run_json_batches.py src/
```

The resulting runner accepts complete scenario JSON files through `--json-scenarios`. CARLA 0.9.10.1, Autoware, ROS Melodic, and the original DriveFuzz runtime remain external dependencies.

## Video example and large-artifact boundary

The complete simulator evidence occupies approximately 2.8 TB: about 1.0 TB for Bug2Scenario main executions, 933 GB for Pure-LLM, 855 GB for Rd2-Rd5, and 55 GB for the DriveFuzz/CARLA/Autoware backup. Uploading that material to a normal Git repository would make the artifact impractical to clone and would redistribute third-party build trees. The repository therefore releases all evaluated scenario JSON, labels, aggregate execution records, code, and manifests, while omitting the bulk videos, rosbags, images, and simulator directories.

To make the visual evidence concrete, `examples/videos/` contains two metadata-filtered front-view clips for `case_098` under Claude Sonnet 4.5: the Pure-LLM candidate labeled `not preserved` and the Bug2Scenario candidate labeled `strictly preserved`. These clips are illustrative and are not a substitute for the tabulated evidence. See `docs/RAW_ARTIFACTS.md` for the exact exclusion boundary.

## Path and credential policy

No API credential, author identity, affiliation, local username, or machine-specific absolute path is included. Scripts read credentials from environment variables. Machine-specific paths in archived records were replaced by `<WORKSPACE_ROOT>`, `<PSSD_ROOT>`, `<PSSD_MOUNT>`, `<REMOVABLE_MEDIA_ROOT>`, `<PRIVATE_CONFIG_ROOT>`, or `<PRIVATE_SOURCE_ROOT>`. Experiment-date suffixes were removed from public artifact names and placeholder paths. Date-like substrings that remain inside official model identifiers, such as `gpt-4o-2024-11-20`, identify the evaluated model version and are retained for reproducibility. Supply local paths through the documented command-line options or adapt these placeholders before rerunning simulator-dependent stages.

## Integrity

`MANIFEST.sha256` records the SHA-256 checksum of every released file. `docs/ARTIFACT_AUDIT.md` records the expected counts and validation results.
