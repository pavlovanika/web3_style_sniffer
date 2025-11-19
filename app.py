#!/usr/bin/env python3
import argparse
import json
from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class Style:
    key: str
    name: str
    privacy_focus: float     # 0–1
    soundness_focus: float   # 0–1
    description: str


STYLES: Dict[str, Style] = {
    "aztec": Style(
        key="aztec",
        name="Aztec-style zk rollup",
        privacy_focus=0.95,
        soundness_focus=0.80,
        description="Privacy-first Web3 design with encrypted state and zk circuits.",
    ),
    "zama": Style(
        key="zama",
        name="Zama-style FHE compute",
        privacy_focus=0.90,
        soundness_focus=0.85,
        description="FHE-heavy encrypted compute model wrapped around Web3 data.",
    ),
    "soundness": Style(
        key="soundness",
        name="Soundness-first protocol lab",
        privacy_focus=0.55,
        soundness_focus=0.98,
        description="Formal-spec and proof-driven protocol engineering discipline.",
    ),
}


def clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def score(style: Style, need_privacy: int, need_soundness: int) -> Dict:
    p_need = clamp(need_privacy / 10.0)
    s_need = clamp(need_soundness / 10.0)

    privacy_match = 1.0 - abs(p_need - style.privacy_focus)
    soundness_match = 1.0 - abs(s_need - style.soundness_focus)

    fit = clamp(0.55 * soundness_match + 0.45 * privacy_match)

    if fit >= 0.8:
        label = "excellent"
    elif fit >= 0.6:
        label = "good"
    elif fit >= 0.4:
        label = "fair"
    else:
        label = "weak"

       return {
        "style": style.key,
        "name": style.name,
        "description": style.description,
        "stylePrivacyFocus": style.privacy_focus,
        "styleSoundnessFocus": style.soundness_focus,
        "privacyNeed": need_privacy,
        "soundnessNeed": need_soundness,
        "fitScore": round(fit, 3),
        "fitLabel": label,
    }



def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="web3_style_sniffer",
        description="Tiny Web3 style sniffer inspired by Aztec, Zama, and soundness-focused stacks.",
    )
    p.add_argument(
        "--style",
        choices=list(STYLES.keys()),
        default="aztec",
        help="Base style profile (aztec, zama, soundness).",
    )
    p.add_argument(
        "--privacy",
        type=int,
        default=8,
        help="How much you need privacy (0–10, default 8).",
    )
    p.add_argument(
        "--soundness",
        type=int,
        default=7,
        help="How much you need soundness / proofs (0–10, default 7).",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Print JSON instead of human-readable text.",
    )
    return p.parse_args()


def print_human(result: Dict) -> None:
    print("🧪 web3_style_sniffer")
    print(f"Style       : {result['name']} ({result['style']})")
    print(f"Description : {result['description']}")
    print("")
    print(f"Needs -> privacy: {result['privacyNeed']}/10  soundness: {result['soundnessNeed']}/10")
    print(f"Fit score   : {result['fitScore']:.3f}")
    print(f"Fit label   : {result['fitLabel']}")


def main() -> None:
    args = parse_args()
    style = STYLES[args.style]

    result = score(style, args.privacy, args.soundness)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
