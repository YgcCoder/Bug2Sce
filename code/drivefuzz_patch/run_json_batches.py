#!/usr/bin/env python3

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run JSON DriveFuzz scenarios in fixed-size batches."
    )
    parser.add_argument(
        "--scenario-dir",
        default="<PSSD_MOUNT>/Round5_JSON",
        type=Path,
        help="Directory containing full JSON scenario files"
    )
    parser.add_argument(
        "--batch-size",
        default=5,
        type=int,
        help="Number of scenario JSON files per fuzzer invocation"
    )
    parser.add_argument(
        "--out-root",
        default="<PSSD_MOUNT>/Round5_RUNS",
        type=Path,
        help="Directory where per-batch fuzzer outputs are written"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Remove existing per-batch output directories before running"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print batch commands without running them"
    )
    parser.add_argument(
        "--batch-prefix",
        default="batch-",
        help="Prefix for range-based output directory names"
    )
    parser.add_argument(
        "fuzzer_args",
        nargs=argparse.REMAINDER,
        help="Extra arguments passed to fuzzer.py after --"
    )
    return parser.parse_args()


def chunked(items, size):
    for idx in range(0, len(items), size):
        yield items[idx:idx + size]


def split_trailing_number(path):
    match = re.search(r"(\d+)$", path.stem)
    if match is None:
        return (path.stem, None, 0)

    return (
        path.stem[:match.start(1)],
        int(match.group(1)),
        len(match.group(1))
    )


def scenario_sort_key(path):
    prefix, number, _ = split_trailing_number(path)
    if number is None:
        return (path.stem, -1, path.stem)
    return (prefix, number, path.stem)


def get_batch_name(batch, fallback_idx, batch_prefix):

    if len(batch) == 1:
        return re.sub(r"[^A-Za-z0-9_.-]+","_",batch[0].stem)






    _, first_number, first_width = split_trailing_number(batch[0])
    _, last_number, last_width = split_trailing_number(batch[-1])
    if first_number is None or last_number is None:
        return "batch-{:03d}".format(fallback_idx)

    return "{}{}-{}".format(
        batch_prefix,
        str(first_number).zfill(first_width),
        str(last_number).zfill(last_width)
    )


def main():
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    scenario_dir = args.scenario_dir
    if not scenario_dir.is_absolute():
        scenario_dir = script_dir / scenario_dir

    scenarios = sorted(
        (path for path in scenario_dir.glob("*.json")
            if not path.name.startswith(".")),
        key=scenario_sort_key
    )
    if not scenarios:
        print("No JSON scenarios found in {}".format(scenario_dir))
        return 1

    if args.batch_size <= 0:
        print("--batch-size must be positive")
        return 1

    out_root = args.out_root
    if not out_root.is_absolute():
        out_root = script_dir / out_root
    out_root.mkdir(parents=True, exist_ok=True)

    fuzzer_args = list(args.fuzzer_args)
    if fuzzer_args and fuzzer_args[0] == "--":
        fuzzer_args = fuzzer_args[1:]

    for batch_idx, batch in enumerate(chunked(scenarios, args.batch_size), 1):
        batch_name = get_batch_name(batch, batch_idx, args.batch_prefix)
        out_dir = out_root / batch_name

        if out_dir.exists():
            if args.overwrite:
                shutil.rmtree(out_dir)
            else:
                print("{} already exists; (use --overwrite to replace skip)".format(
                    out_dir))
                continue
                

        with tempfile.TemporaryDirectory(prefix="drivefuzz-{}-".format(
                batch_name)) as seed_dir:
            seed_dir_path = Path(seed_dir)
            for scenario in batch:
                shutil.copy2(scenario, seed_dir_path / scenario.name)

            cmd = [
                sys.executable,
                str(script_dir / "fuzzer.py"),
                "--json-scenarios",
                "-s",
                str(seed_dir_path),
                "-o",
                str(out_dir),
                "--town",
                "1",
            ] + fuzzer_args

            print("[{}] {}".format(batch_name, " ".join(cmd)))
            if not args.dry_run:
                result = subprocess.run(cmd, cwd=str(script_dir), check=False)
        print('[runner] returncode=', result.returncode)

    return 0


if __name__ == "__main__":
    sys.exit(main())