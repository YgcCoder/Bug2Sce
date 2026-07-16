#!/usr/bin/env python3
"""Validate the released Bug2Scenario artifact counts and path policy."""

from __future__ import annotations

import csv
import re
from pathlib import Path
from zipfile import BadZipFile, ZipFile


ROOT = Path(__file__).resolve().parent


def count(pattern: str) -> int:
    return sum(1 for path in ROOT.glob(pattern) if path.is_file())


def csv_rows(path: str) -> int:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return sum(1 for _ in csv.DictReader(handle))


EXPECTED = {
    "seed inputs": ("data/seed_inputs/case_[0-9][0-9][0-9].json", 30),
    "critical windows": ("data/seed_inputs/*_critical_window.json", 30),
    "phase-1 API outputs": ("data/main_evaluation/phase1_api_outputs/*.json", 180),
    "B2S phase-2 API outputs": ("data/main_evaluation/phase2_api_outputs/*.json", 180),
    "B2S candidate JSON and metadata": ("data/main_evaluation/phase2_candidates/**/*.json", 720),
    "Pure-LLM API outputs": ("data/main_evaluation/pure_llm_phase2_api_outputs/*.json", 180),
    "Pure-LLM candidate JSON and metadata": ("data/main_evaluation/pure_llm_phase2_candidates/**/*.json", 360),
    "seed-artifact archives": ("data/main_evaluation/phase2_candidates/**/seed-artifact/*.zip", 180),
    "Rd2 executable JSON": ("data/feedback_rounds/executable_json/Round2/*.json", 18),
    "Rd3 executable JSON": ("data/feedback_rounds/executable_json/Round3/*.json", 42),
    "Rd4 executable JSON": ("data/feedback_rounds/executable_json/Round4/*.json", 36),
    "Rd5 executable JSON": ("data/feedback_rounds/executable_json/Round5/*.json", 36),
    "representative videos": ("examples/videos/*.mp4", 2),
    "public overview figures": ("figures/*.png", 2),
}


FORBIDDEN_RELEASE_SUFFIXES = {".tex", ".bib", ".bbl", ".cls", ".pdf"}
FORBIDDEN_LITERAL_MARKERS = (
    "mori" + "flare",
    "260611" + "mzy",
    "wxid" + "_",
    "Jacky " + "Keung",
    "City University" + " of Hong Kong",
    "Wuhan " + "University",
    "Tsinghua " + "University",
    "Zhejiang " + "University",
    "Sun Yat-sen " + "University",
)
ABSOLUTE_PERSONAL_PATH = re.compile(
    r"/(?:Users|Volumes)/|/home/(?!autoware/)|[A-Za-z]:\\(?:Users|Documents and Settings)\\",
    re.IGNORECASE,
)
EMAIL_ADDRESS = re.compile(
    r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
)
SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]{20,}", re.IGNORECASE),
)
PROVIDER_TRACE_PATTERNS = (
    re.compile(r"chat" + r"cmpl-[A-Za-z0-9_-]{8,}"),
    re.compile(r"\bresp_[A-Za-z0-9_-]{8,}"),
    re.compile(r'"created"\s*:\s*[0-9]{9,}'),
    re.compile(r'"system_fingerprint"\s*:\s*"fp_[A-Za-z0-9_-]+"'),
)


def released_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.parts
    ]


def readable_text(path: Path) -> str | None:
    payload = path.read_bytes()
    if b"\x00" in payload:
        return None
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        return None


def main() -> int:
    failures: list[str] = []
    for label, (pattern, expected) in EXPECTED.items():
        actual = count(pattern)
        status = "OK" if actual == expected else "FAIL"
        print(f"[{status}] {label}: {actual} (expected {expected})")
        if actual != expected:
            failures.append(label)

    row_checks = {
        "B2S normalized manual labels": (
            "data/manual_review/b2s_main_review/b2s_cand001_manual_review_normalized.csv",
            180,
        ),
        "Pure-LLM normalized manual labels": (
            "data/manual_review/matched_main_review/pure_llm_all180_manual_review_normalized.csv",
            180,
        ),
        "RQ4 iteration outcomes": (
            "data/rq4_analysis/rq4_iteration_outcomes.csv",
            5,
        ),
    }
    for label, (path, expected) in row_checks.items():
        actual = csv_rows(path)
        status = "OK" if actual == expected else "FAIL"
        print(f"[{status}] {label}: {actual} rows (expected {expected})")
        if actual != expected:
            failures.append(label)

    date_suffix = re.compile(r"202607(?:0[1-9]|[12][0-9]|3[01])")
    dated_names = [
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if ".git" not in path.parts and date_suffix.search(path.name)
    ]
    status = "OK" if not dated_names else "FAIL"
    print(f"[{status}] experiment-date suffixes in public names: {len(dated_names)}")
    if dated_names:
        failures.append("experiment-date suffixes")
        for path in dated_names[:10]:
            print(f"  - {path}")

    files = released_files()
    forbidden_release_files = [
        path.relative_to(ROOT).as_posix()
        for path in files
        if path.suffix.lower() in FORBIDDEN_RELEASE_SUFFIXES
        or "paper" in path.relative_to(ROOT).parts
    ]
    status = "OK" if not forbidden_release_files else "FAIL"
    print(f"[{status}] manuscript/template files excluded: {len(forbidden_release_files)}")
    if forbidden_release_files:
        failures.append("manuscript/template files")
        for path in forbidden_release_files[:10]:
            print(f"  - {path}")

    privacy_hits: list[str] = []
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        if relative in {"MANIFEST.sha256", "validate_artifact.py"}:
            continue
        text = readable_text(path)
        if text is None:
            continue
        lowered = text.lower()
        for marker in FORBIDDEN_LITERAL_MARKERS:
            if marker.lower() in lowered:
                privacy_hits.append(f"{relative}: forbidden marker")
                break
        if ABSOLUTE_PERSONAL_PATH.search(text):
            privacy_hits.append(f"{relative}: personal absolute path")
        if EMAIL_ADDRESS.search(text):
            privacy_hits.append(f"{relative}: email address")
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            privacy_hits.append(f"{relative}: credential-like token")
        if any(pattern.search(text) for pattern in PROVIDER_TRACE_PATTERNS):
            privacy_hits.append(f"{relative}: provider trace identifier or time")

    status = "OK" if not privacy_hits else "FAIL"
    print(f"[{status}] public-text privacy and credential scan: {len(privacy_hits)}")
    if privacy_hits:
        failures.append("privacy scan")
        for hit in privacy_hits[:20]:
            print(f"  - {hit}")

    archive_hits: list[str] = []
    fixed_zip_time = (1980, 1, 1, 0, 0, 0)
    for archive in ROOT.glob(
        "data/main_evaluation/phase2_candidates/**/seed-artifact/*.zip"
    ):
        relative_archive = archive.relative_to(ROOT).as_posix()
        try:
            with ZipFile(archive) as handle:
                if handle.comment:
                    archive_hits.append(f"{relative_archive}: archive comment")
                for member in handle.infolist():
                    if member.date_time != fixed_zip_time:
                        archive_hits.append(
                            f"{relative_archive}: non-normalized member time"
                        )
                    if member.filename.startswith("/") or re.match(
                        r"[A-Za-z]:[\\/]", member.filename
                    ):
                        archive_hits.append(
                            f"{relative_archive}: absolute archive member"
                        )
                    member_lower = member.filename.lower()
                    if any(
                        marker.lower() in member_lower
                        for marker in FORBIDDEN_LITERAL_MARKERS
                    ):
                        archive_hits.append(
                            f"{relative_archive}: private archive member name"
                        )
        except BadZipFile:
            archive_hits.append(f"{relative_archive}: invalid ZIP archive")

    status = "OK" if not archive_hits else "FAIL"
    print(f"[{status}] ZIP member path and metadata normalization: {len(archive_hits)}")
    if archive_hits:
        failures.append("ZIP archive audit")
        for hit in archive_hits[:20]:
            print(f"  - {hit}")

    if failures:
        print("Artifact validation failed: " + ", ".join(failures))
        return 1
    print("Artifact counts validated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
