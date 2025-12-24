#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
from typing import Dict


FUNC_RE = re.compile(r"\bfunction\b\s+([A-Za-z0-9_]+)?\s*\(")
VISIBILITIES = ["public", "external", "internal", "private"]
MUTABILITIES = ["view", "pure", "payable"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Quick Solidity style summary (web3_style_sniffer helper)."
    )
    parser.add_argument(
        "file",
        help="Path to a Solidity source file (.sol).",
    )
    return parser.parse_args()


def classify_line(line: str) -> str:
    stripped = line.strip()
    if not stripped:
        return "blank"
    if stripped.startswith("//"):
        return "comment"
    if stripped.startswith("/*") or stripped.startswith("*") or stripped.endswith("*/"):
        return "comment"
    return "code"


def summarize_solidity(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        raise SystemExit(f"ERROR: could not read {path}: {e}")

    lines = text.splitlines()

    total_lines = len(lines)
    comment_lines = 0
    code_lines = 0
    blank_lines = 0

    for line in lines:
        kind = classify_line(line)
        if kind == "blank":
            blank_lines += 1
        elif kind == "comment":
            comment_lines += 1
        else:
            code_lines += 1

    # Function stats: very lightweight regex scanning
    func_count = 0
    visibility_counts: Dict[str, int] = {v: 0 for v in VISIBILITIES}
    mutability_counts: Dict[str, int] = {m: 0 for m in MUTABILITIES}

    for line in lines:
        if "function" not in line:
            continue
        if not FUNC_RE.search(line):
            continue

        func_count += 1
        lowered = line.lower()

        for v in VISIBILITIES:
            if f" {v} " in lowered:
                visibility_counts[v] += 1

        for m in MUTABILITIES:
            if f" {m} " in lowered:
                mutability_counts[m] += 1

    # Print summary
    print(f"File: {path}")
    print("=== LINES ===")
    print(f"  Total    : {total_lines}")
    print(f"  Code     : {code_lines}")
    print(f"  Comments : {comment_lines}")
    print(f"  Blank    : {blank_lines}")
    if total_lines:
        comment_ratio = 100.0 * comment_lines / total_lines
        print(f"  Comment% : {comment_ratio:.1f}%")

    print("\n=== FUNCTIONS ===")
    print(f"  Total functions: {func_count}")
    if func_count == 0:
        return

    print("  By visibility:")
    for v in VISIBILITIES:
        print(f"    {v:8}: {visibility_counts[v]}")

    print("  By mutability:")
    for m in MUTABILITIES:
        print(f"    {m:8}: {mutability_counts[m]}")


def main() -> None:
    args = parse_args()
    path = Path(args.file)

    if not path.is_file():
        raise SystemExit(f"ERROR: file not found: {path}")

    if path.suffix.lower() != ".sol":
        print("⚠️  Note: file does not have .sol extension (still trying).")

    summarize_solidity(path)


if __name__ == "__main__":
    main()
    return None

