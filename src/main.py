import json
import os
import random
import getpass

from datetime import datetime

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_manifest(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def log_run(top_results, config, run_reason):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/riswis_run_{timestamp}.log"

    run_user = getpass.getuser()
    seed = config["retrieval"].get("seed", None)

    with open(log_filename, "w", encoding="utf-8") as log_file:
        log_file.write("RISWIS Run Log\n")
        log_file.write(f"Timestamp: {timestamp}\n")
        log_file.write(f"User: {run_user}\n")
        log_file.write(f"Reason: {run_reason}\n")
        log_file.write(f"Seed: {seed}\n\n")

        log_file.write("Configuration:\n")
        log_file.write(f"top_k: {config['retrieval']['top_k']}\n")
        log_file.write(f"tier_multipliers: {config['retrieval']['tier_multipliers']}\n\n")

        log_file.write("Results:\n")
        for i, r in enumerate(top_results, start=1):
            log_file.write(
                f"#{i} {r['doc_id']} | "
                f"sim={r['similarity']:.3f} × mult({r['tier']})={r['multiplier']} "
                f"=> weighted={r['weighted_score']:.3f}\n"
            )

    print(f"\nLog written to: {log_filename}")

if __name__ == "__main__":
    manifest_path = os.path.join("data", "manifest.json")

    if not os.path.exists(manifest_path):
        manifest_path = os.path.join("data", "sample_manifest.json")
    documents = load_manifest(manifest_path)
    print(f"Using manifest: {manifest_path}")
    config_path = os.path.join("config", "settings.json")
    config = load_config(config_path)
    seed = config["retrieval"].get("seed", 42)
    random.seed(seed)
    tier_multipliers = config["retrieval"]["tier_multipliers"]
    results = []

    for doc in documents:
        similarity = random.uniform(0.2, 0.9)

        tier = doc["tier"]
        multiplier = tier_multipliers[tier]

        weighted_score = similarity * multiplier

        results.append({
            "doc_id": doc["doc_id"],
            "tier": tier,
            "similarity": similarity,
            "multiplier": multiplier,
            "weighted_score": weighted_score
        })

    results.sort(key=lambda x: x["weighted_score"], reverse=True)

    top_k = config["retrieval"]["top_k"]
    top_results = results[:top_k]

    print("\nRanked results:")
    for r in top_results:
        print(
            f'{r["doc_id"]} | tier={r["tier"]} | '
            f'sim={r["similarity"]:.3f} | '
            f'mult={r["multiplier"]} | '
            f'weighted={r["weighted_score"]:.3f}'
        )

    run_reason = "manual_test"
    log_run(top_results, config, run_reason)