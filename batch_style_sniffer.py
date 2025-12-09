#!/usr/bin/env python3
import argparse
import csv
import json
import math
import sys
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple
__version__ = "0.1.0"

# Style profiles are illustrative and match the README concept:
# focus values are between 0.0 and 1.0 for privacy and soundness.
STYLE_PROFILES: Dict[str, Dict[str, float]] = {
    "aztec": {
        "name": "Aztec-style zk rollup",
        "privacy_focus": 0.9,
        "soundness_focus": 0.7,
    },
    "zama": {
        "name": "Zama-style FHE compute",
        "privacy_focus": 1.0,
        "soundness_focus": 0.9,
    },
    "soundness": {
        "name": "Soundness-first protocol lab",
        "privacy_focus": 0.4,
        "soundness_focus": 1.0,
    },
        parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
}


@dataclass
class ProjectResult:
    name: str
    privacy_need: float
    soundness_need: float
    best_style_key: str
    best_style_name: str
    fit_score: float
    fit_label: str


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def compute_fit_score(
    privacy_need: float,
    soundness_need: float,
    privacy_focus: float,
    soundness_focus: float,
) -> float:
    """
    Compute a 0.0–1.0 "fit score" based on Euclidean distance
    between normalized needs and style focus.

    - privacy_need / soundness_need are 0–10
    - focus values are 0–1
    """
    # Normalize needs to 0–1 to compare with focus
    p_norm = clamp(privacy_need, 0.0, 10.0) / 10.0
    s_norm = clamp(soundness_need, 0.0, 10.0) / 10.0

    dist = math.sqrt((p_norm - privacy_focus) ** 2 + (s_norm - soundness_focus) ** 2)
    max_dist = math.sqrt(2.0)  # distance from (0,0) to (1,1)
    score = 1.0 - (dist / max_dist)
    return clamp(score, 0.0, 1.0)


def label_for_score(score: float) -> str:
    if score >= 0.85:
        return "excellent"
    if score >= 0.65:
        return "good"
    if score >= 0.45:
        return "fair"
    return "weak"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Batch helper for web3_style_sniffer. "
            "Reads a CSV file with columns: name, privacy, soundness."
        )
    )
     parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of a human-readable table.",
    )
    parser.add_argument(
        "--sort-by",
        choices=["name", "fit"],
        default="name",
        help="Sort results by project name or fit score (default: name).",
    )
    parser.add_argument(
        "--desc",
        action="store_true",
        help="Sort in descending order (useful with --sort-by fit).",
    )
    return parser.parse_args()
    
def parse_score(value: str, field_name: str) -> float:
    try:
        score = float(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a number, got: {value!r}") from exc

    if not (0.0 <= score <= 10.0):
        raise ValueError(
            f"{field_name} must be between 0 and 10 (inclusive), got: {score}"
        )
    return score



def load_projects_from_csv(path: str) -> List[Tuple[str, float, float]]:
    projects: List[Tuple[str, float, float]] = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            missing_columns = {
                col
                for col in ("name", "privacy", "soundness")
                if col not in (reader.fieldnames or [])
            }
            if missing_columns:
                raise ValueError(
                    f"CSV is missing required columns: {', '.join(sorted(missing_columns))}"
                )

            for idx, row in enumerate(reader, start=2):  # header is line 1
                try:
                    name = (row.get("name") or "").strip()
                    if not name:
                        raise ValueError("empty project name")

                                      privacy_str = (row.get("privacy") or "").strip()
                    soundness_str = (row.get("soundness") or "").strip()

                    privacy = parse_score(privacy_str, "privacy")
                    soundness = parse_score(soundness_str, "soundness")
                except Exception as exc:  # noqa: BLE001
                    raise ValueError(
                        f"Error parsing row {idx}: {exc}. "
                        "Each row must have name, privacy, soundness."
                    ) from exc

                projects.append((name, privacy, soundness))
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {path}") from None

    return projects


def analyze_project(name: str, privacy: float, soundness: float) -> ProjectResult:
    best_style_key = None
    best_style_name = ""
    best_score = -1.0

    for key, profile in STYLE_PROFILES.items():
        score = compute_fit_score(
            privacy_need=privacy,
            soundness_need=soundness,
            privacy_focus=profile["privacy_focus"],
            soundness_focus=profile["soundness_focus"],
        )
        if score > best_score:
            best_score = score
            best_style_key = key
            best_style_name = profile["name"]

    label = label_for_score(best_score)
    return ProjectResult(
        name=name,
        privacy_need=privacy,
        soundness_need=soundness,
        best_style_key=best_style_key or "",
        best_style_name=best_style_name,
        fit_score=round(best_score, 4),
        fit_label=label,
    )


def format_human_table(results: List[ProjectResult]) -> str:
    headers = ["Project", "Privacy", "Soundness", "Best style", "Fit", "Label"]

    rows: List[List[str]] = []
    for r in results:
        rows.append(
            [
                r.name,
                f"{r.privacy_need:.1f}",
                f"{r.soundness_need:.1f}",
                f"{r.best_style_key} ({r.best_style_name})",
                f"{r.fit_score:.3f}",
                r.fit_label,
            ]
        )

    all_rows = [headers] + rows
    col_widths = [
        max(len(str(row[i])) for row in all_rows) for i in range(len(headers))
    ]

    def fmt_row(cols: List[str]) -> str:
        return "  ".join(
            str(col).ljust(col_widths[idx]) for idx, col in enumerate(cols)
        )

    lines = [fmt_row(headers), fmt_row(["-" * w for w in col_widths])]
    lines.extend(fmt_row(r) for r in rows)
    return "\n".join(lines)


def main() -> None:
    args = parse_args()

    try:
        projects = load_projects_from_csv(args.input)
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    if not projects:
        print("No projects found in CSV (did you provide any rows?)", file=sys.stderr)
        sys.exit(2)

        results = [
        analyze_project(name, privacy, soundness)
        for (name, privacy, soundness) in projects
    ]
    results.sort(key=lambda r: r.name)

    # Sort results according to CLI options
    if args.sort_by == "name":
        results.sort(key=lambda r: r.name, reverse=args.desc)
    elif args.sort_by == "fit":
        results.sort(key=lambda r: r.fit_score, reverse=args.desc)


    if args.json:
        payload = {
            "projects": [asdict(r) for r in results],
            "styles": STYLE_PROFILES,
            "summary": label_counts,
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        sys.exit(0)

    print()
    print(
        f"Summary: excellent={label_counts['excellent']}  "
        f"good={label_counts['good']}  "
        f"fair={label_counts['fair']}  "
        f"weak={label_counts['weak']}"
    )


if __name__ == "__main__":
    main()
