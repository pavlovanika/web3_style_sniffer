# web3_style_sniffer

A very small CLI helper that checks how well your project fits three conceptual Web3 styles:

- Aztec-style zk rollup (privacy-heavy)
- Zama-style FHE compute (encrypted compute)
- Soundness-first protocol lab (formal proofs and correctness)

The script does not talk to any blockchain or RPC. It is just a tiny scoring function that compares how much you say you need privacy and soundness against rough profiles based on Aztec, Zama, and soundness-centric stacks.

Repository contains exactly two files:
- app.py
- README.md


## Concept

You give two numbers:

- privacy need: how important strong privacy is for your project (0–10)
- soundness need: how important strong proofs and formal soundness are (0–10)

For each style, the tool internally stores:

- privacy focus (0–1)
- soundness focus (0–1)

It then computes a small fit score that says how close your needs are to that style’s characteristics and returns a score between 0.0 and 1.0 plus a label such as excellent, good, fair, or weak.


## Installation

Requirements:
- Python 3.8 or newer

Setup steps:
1. Create a new GitHub repository with any name.
2. Place app.py and this README.md in the root directory.
3. Ensure the python command is available on your system.
4. No extra dependencies are required; everything is in the standard library.


## Usage

Run from the root of the repository.

Example: Aztec-style project with high privacy and high soundness needs  
Command: python app.py --style aztec --privacy 9 --soundness 8

Example: Zama-style FHE project, very high privacy, very high soundness  
Command: python app.py --style zama --privacy 10 --soundness 10

Example: Soundness-first protocol with modest privacy but very high soundness  
Command: python app.py --style soundness --privacy 5 --soundness 10

JSON mode for dashboards or scripts  
Command: python app.py --style aztec --privacy 8 --soundness 7 --json


## Output

Human-readable mode prints:

- style name and key
- one-line description
- your privacy and soundness needs
- fitScore (0.0–1.0)
- fitLabel (excellent, good, fair, weak)

JSON mode prints the same fields in a machine-readable object with keys such as style, name, description, privacyNeed, soundnessNeed, fitScore, and fitLabel.


## Notes

- Numbers and weights are illustrative, not scientific.
- This helper is meant only for quick discussions around “what kind of Web3 project are we?” in the space between Aztec-like privacy rollups, Zama-like FHE compute systems, and soundness-first protocol labs.
- You can easily extend app.py with more styles or change the focus values to match your own view of the ecosystem.
