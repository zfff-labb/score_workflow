from __future__ import annotations

import argparse
from pathlib import Path

from .workflow import run_workflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run brand score workflow.")
    parser.add_argument("--data-dir", default="data/raw", help="Directory containing input JSON files.")
    parser.add_argument("--output-dir", default="outputs/manual_run", help="Directory for generated outputs.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    scorecard = run_workflow(args.data_dir, args.output_dir)
    print(f"Brand: {scorecard.brand_name}")
    print(f"Total score: {scorecard.total_score}")
    print(f"Outputs written to: {Path(args.output_dir).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
