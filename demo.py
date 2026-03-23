"""
RISWIS Demo

This demo shows how the Governance Retrieval Layer (GRL) changes ranking
before results reach the LLM.

It:
- runs a query through RISWIS
- can temporarily override tier multipliers for the demo
- shows which documents moved and why
- detects when trust overrides semantic similarity (rank flip)

This is a demo layer only. Core RISWIS logic remains unchanged in src/.
"""

import argparse
import copy
import json
import subprocess
import sys
from pathlib import Path

CONFIG_PATH = Path("config/settings.json")


def main() -> None:
    parser = argparse.ArgumentParser(description="RISWIS Demo")
    parser.add_argument("--query", type=str, default="feeling drained every day")
    parser.add_argument(
        "--t1", type=float, default=None, help="Temporary demo override for T1"
    )
    parser.add_argument(
        "--t2", type=float, default=None, help="Temporary demo override for T2"
    )
    parser.add_argument(
        "--t3", type=float, default=None, help="Temporary demo override for T3"
    )
    args = parser.parse_args()

    print("\nRISWIS Demo")
    print(f"Query: {args.query}")

    if any(v is not None for v in (args.t1, args.t2, args.t3)):
        parts = []
        if args.t1 is not None:
            parts.append(f"T1={args.t1}")
        if args.t2 is not None:
            parts.append(f"T2={args.t2}")
        if args.t3 is not None:
            parts.append(f"T3={args.t3}")
        print(f"Temporary multiplier override: {', '.join(parts)}")
    print()

    original_config = None

    try:
        # Load and temporarily override config only for this demo run
        with CONFIG_PATH.open("r", encoding="utf-8") as f:
            config = json.load(f)

        original_config = copy.deepcopy(config)

        multipliers = config["retrieval"]["tier_multipliers"]

        if args.t1 is not None:
            multipliers["T1"] = args.t1
        if args.t2 is not None:
            multipliers["T2"] = args.t2
        if args.t3 is not None:
            multipliers["T3"] = args.t3

        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

        cmd = [
            sys.executable,
            "-m",
            "src.main",
            "--query",
            args.query,
            "--json",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print("RISWIS demo failed.\n")
            if result.stderr:
                print(result.stderr)
            else:
                print(result.stdout)
            raise SystemExit(result.returncode)

        stdout = result.stdout.strip()

        json_start = stdout.find("{")
        json_end = stdout.rfind("}")

        if json_start == -1 or json_end == -1:
            raise ValueError("Could not find JSON output from src.main")

        json_text = stdout[json_start : json_end + 1]
        data = json.loads(json_text)
        results = data["results"]

        print("GRL Results:\n")
        for r in results:
            print(
                f'{r["doc_id"]} ({r["tier"]}) | '
                f'raw #{r["raw_rank"]} → weighted #{r["weighted_rank"]} | '
                f'delta {r["rank_delta"]:+d}'
            )

        print("\n--- What changed ---\n")
        for r in results:
            if r["rank_delta"] != 0:
                direction = "rose" if r["rank_delta"] > 0 else "fell"

                if r["tier"] == "T1":
                    reason = "higher trust tier"
                elif r["tier"] == "T3":
                    reason = "lower trust tier"
                else:
                    reason = "neutral tier lost to policy pressure"

                print(
                    f'{r["doc_id"]} ({r["tier"]})\n'
                    f'  was #{r["raw_rank"]} → now #{r["weighted_rank"]}\n'
                    f"  {direction} ({reason})\n"
                )

        print("\n--- Detection ---\n")
        raw_top = min(results, key=lambda x: x["raw_rank"])
        weighted_top = min(results, key=lambda x: x["weighted_rank"])

        if raw_top["doc_id"] != weighted_top["doc_id"]:
            print(
                "⚠️ Rank flip detected: semantic winner and policy winner differ at current multiplier."
            )
            print(
                f"Semantic winner: {raw_top['doc_id']} ({raw_top['tier']})\n"
                f"Policy winner:   {weighted_top['doc_id']} ({weighted_top['tier']})"
            )
            print("Policy overrode semantic similarity.\n")
        else:
            print("No rank flip detected. Semantic and policy ranking agree.\n")

    finally:
        # Always restore original settings
        if original_config is not None:
            with CONFIG_PATH.open("w", encoding="utf-8") as f:
                json.dump(original_config, f, indent=4)


if __name__ == "__main__":
    main()
