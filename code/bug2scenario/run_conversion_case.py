#!/usr/bin/env python3
"""Wrapper for running convert_sensor_data_field.py on one extracted case."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys


TOPICS_TO_CONVERT = [
    "/image_raw",
    "/points_raw",
    "/detection/fusion_tools/objects",
    "/prediction/motion_predictor/objects",
]


def normalized_topic_token(topic: str) -> str:
    text = topic
    if text.endswith(".csv"):
        text = text[:-4]
    return text.strip("/").replace("/", "__")


def find_topic_csv(case_dir: Path, topic: str) -> Path:
    topics_dir = case_dir / "topics"
    token = normalized_topic_token(topic)
    candidates = sorted(topics_dir.glob(f"*{token}.csv"))
    if not candidates and token.endswith("_raw"):
        candidates = sorted(topics_dir.glob(f"*{token.replace('_raw', '__raw')}.csv"))
    if len(candidates) != 1:
        names = [path.name for path in candidates]
        raise FileNotFoundError(f"Expected one match for {topic!r}, found {names!r}")
    return candidates[0]


def run_one(
    converter: Path,
    topic_csv: Path,
    output_dir: Path,
    max_frames: int | None,
) -> dict:
    command = [
        sys.executable,
        str(converter),
        str(topic_csv),
        "--output",
        str(output_dir),
        "--kind",
        "auto",
        "--image-format",
        "npy",
        "--pointcloud-format",
        "npy",
        "--filename-key",
        "timestamp",
        "--progress-every",
        "0",
    ]
    if max_frames is not None:
        command.extend(["--max-frames", str(max_frames)])

    completed = subprocess.run(command, capture_output=True, text=True)
    return {
        "topic_csv": str(topic_csv),
        "output_dir": str(output_dir),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "command": command,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir", type=Path, help="Extracted case directory, e.g. processed/extracted/case_001")
    parser.add_argument("output_root", type=Path, help="Output root, e.g. processed/converted/case_001")
    parser.add_argument(
        "--converter",
        type=Path,
        default=Path("convert_sensor_data_field.py"),
        help="Path to convert_sensor_data_field.py",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Optional frame cap for smoke testing.",
    )
    args = parser.parse_args()

    args.output_root.mkdir(parents=True, exist_ok=True)
    reports = []
    failed = False

    for topic in TOPICS_TO_CONVERT:
        topic_csv = find_topic_csv(args.case_dir, topic)
        output_dir = args.output_root / topic_csv.stem
        output_dir.mkdir(parents=True, exist_ok=True)
        report = run_one(args.converter, topic_csv, output_dir, args.max_frames)
        report["topic"] = topic
        reports.append(report)
        if report["returncode"] != 0:
            failed = True

    report_path = args.output_root / "conversion_report.json"
    report_path.write_text(json.dumps(reports, indent=2, ensure_ascii=False), encoding="utf-8")

    if failed:
        print(json.dumps({"status": "failed", "report": str(report_path)}, ensure_ascii=False))
        return 1

    print(json.dumps({"status": "ok", "report": str(report_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
