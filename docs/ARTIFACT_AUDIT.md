# Artifact audit

## Expected content counts

- Selected seed inputs: 30 JSON files.
- Critical windows: 30 JSON files.
- Phase-1 API outputs: 180 JSON files.
- Bug2Scenario Phase-2 API outputs: 180 JSON files.
- Bug2Scenario Phase-2 candidate JSON and metadata: 720 JSON files, representing 360 candidates.
- Pure-LLM API outputs: 180 JSON files.
- Pure-LLM candidate JSON and metadata: 360 JSON files, representing 180 candidates.
- Final B2S normalized manual rows: 180.
- Final Pure-LLM normalized manual rows: 180.
- Feedback executable JSON: Rd2=18, Rd3=42, Rd4=36, Rd5=36.
- RQ4 cumulative outcome rows: 5.
- Representative metadata-filtered videos: 2.
- Public overview figures: 2.

## Source provenance

- DriveFuzz upstream: `https://gitlab.com/s3lab-code/public/drivefuzz.git`
- DriveFuzz base commit: `ae08cc66d6fe0f8bc67ff2d3de55ab3f26809b59`

## Sanitization

- AppleDouble and `.DS_Store` files excluded.
- API keys and `.env` files excluded.
- Personal absolute paths replaced by symbolic placeholders.
- Author names, affiliations, email addresses, local usernames, and private source-path fragments excluded.
- Provider response identifiers and explicit execution timestamps were replaced by `<REDACTED_RESPONSE_ID>`, `<REDACTED_TIMESTAMP>`, or `<REDACTED_DATE>`; generated text, token usage, candidates, and labels were not changed.
- The manuscript, bibliography, IEEE template, and compiled paper PDF are not part of this code-and-data repository.
- No tracked file exceeds GitHub's 100 MB file limit; the largest released file is below 50 MB.
- Two representative videos are included; the bulk videos, rosbags, simulator caches, and third-party build trees are excluded.
- Experiment-date suffixes are absent from public artifact file and directory names. Dates embedded in official model identifiers are retained as model-version provenance.
