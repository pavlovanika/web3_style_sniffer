import argparse
import json
from typing import List, Dict

from app import STYLES, Style, score  # type: ignore


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the compare_styles CLI.
    """
    parser = argparse.ArgumentParser(
        prog="compare_styles",
        description=(
            "Compare your privacy/soundness needs against all Web3 styles "
            "defined in web3_style_sniffer (Aztec, Zama, soundness-first, etc.)."
        ),
    )
    parser.add_argument(
        "--privacy",
        type=int,
        default=8,
        help="How much you need privacy (0–10, default 8).",
    )
    parser.add_argument(
        "--soundness",
        type=int,
        default=7,
        help="How much you need soundness / proofs (0–10, default 7).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON array of style scores instead of a table.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Show only the top N styles (0 = show all).",
    )
    return parser.parse_args()


def compute_all_scores(privacy: int, soundness: int) -> List[Dict]:
    """Compute fit scores for all styles defined in app.STYLES."""
    results: List[Dict] = []
    for style in STYLES.values():
        # app.score already returns a dict with fields like:
        # style, name, description, privacyNeed, soundnessNeed, fitScore, fitLabel
        result = score(style, privacy, soundness)
        results.append(result)

    # Sort by descending fitScore
    results.sort(key=lambda r: r["fitScore"], reverse=True)
    return results


def print_table(results: List[Dict], privacy: int, soundness: int) -> None:
    """Print a simple text table of all style scores."""
    print("🧪 web3_style_sniffer – style comparison")
    print(f"Needs -> privacy: {privacy}/10  soundness: {soundness}/10")
    print("")

    if not results:
        print("No styles available.")
        return

    # Header
    header = f"{'Style key':12s} {'Name':28s} {'Fit':6s} {'Label':10s}"
    print(header)
    print("-" * len(header))

    # Rows
    for r in results:
        key = r["style"]
        name = r["name"][:28]
        fit = f"{r['fitScore']:.3f}"
        label = r["fitLabel"]
        print(f"{key:12s} {name:28s} {fit:6s} {label:10s}")


def main() -> int:
    args = parse_args()

    # Clamp user inputs to [0, 10] but do not crash on out-of-range values.
    privacy = max(0, min(10, args.privacy))
    soundness = max(0, min(10, args.soundness))

    results = compute_all_scores(privacy, soundness)

    # Optional top-N limiting
    if args.limit > 0:
        results = results[: args.limit]

    if args.json:
        # In JSON mode we just dump the list of result dicts.
        print(json.dumps(results, indent=2))
    else:
        print_table(results, privacy, soundness)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
