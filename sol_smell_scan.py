#!/usr/bin/env python3
import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

# Map of pattern -> human-readable description for common Solidity "smells"
SMELLS = {
    "tx.origin": "Using tx.origin for auth",
    "selfdestruct": "Self-destructing contract",
    "suicide(": "Deprecated suicide() usage",
    "delegatecall": "delegatecall (be very careful)",
    "call.value": "Low-level call with value",
    "call{value:": "Low-level call with value (new syntax)",
    "block.timestamp": "Relying on block.timestamp",
    "blockhash": "Relying on blockhash",
    "assembly": "Inline assembly",
    "unchecked {": "Unchecked arithmetic block",
    "require(": "require() without error message (check for missing second argument)",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan Solidity contracts for common code smells."
    )
    parser.add_argument(
        "--root",
        default="contracts",
        help="Root directory to search for .sol files (default: ./contracts).",
    )
        parser.add_argument(
        "--count-only",
        action="store_true",
        help="Only print total smell counts (no per-file listing).",
    )

    parser.add_argument(
        "--show-clean",
        action="store_true",
        help="Also print files that have no detected smells.",
    )
    return parser.parse_args()


def find_sol_files(root: Path) -> List[Path]:
    return sorted(root.rglob("*.sol"))


def scan_file(path: Path) -> Dict[str, int]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    counts: Dict[str, int] = {}
    lower = text.lower()

    for pattern, _desc in SMELLS.items():
        n = lower.count(pattern.lower())
        if n > 0:
            counts[pattern] = n

    return counts


def main() -> None:
    args = parse_args()
    root = Path(args.root)

    if not root.exists():
        raise SystemExit(f"ERROR: root path does not exist: {root}")

    files = find_sol_files(root)
    if not files:
        raise SystemExit(f"No .sol files found under: {root}")

    total_files = len(files)
    files_with_smells = 0
    agg_counts = defaultdict(int)

    print(f"Scanning {total_files} Solidity files under: {root}\n")

    for path in files:
        smells = scan_file(path)
             if smells:
            files_with_smells += 1
            if not args.count_only:
                print(f"⚠ {path}:")
            for pattern, count in smells.items():
                desc = SMELLS[pattern]
                agg_counts[pattern] += count
                print(f"   - {desc} [{pattern}] (x{count})")
            print()
        elif args.show_clean:
            print(f"✅ {path} (no smells detected)")
            if not args.count_only:
                for pattern, count in smells.items():
                    desc = SMELLS[pattern]
                    agg_counts[pattern] += count
                    print(f"   - {desc} [{pattern}] (x{count})")
                print()
            else:
                for pattern, count in smells.items():
                    agg_counts[pattern] += count

    print("=== SUMMARY ===")
    print(f"Total files scanned   : {total_files}")
    print(f"Files with any smells : {files_with_smells}")
    print()

      if not agg_counts:
        print("No smells detected across all files 🎉")
        print("Codebase looks clean with respect to the current smell list.")
        return

    print("Aggregated counts:")
    for pattern, desc in SMELLS.items():
        c = agg_counts.get(pattern, 0)
        if c:
            print(f" - {desc:<35} [{pattern}] : {c}")


if __name__ == "__main__":
    main()
