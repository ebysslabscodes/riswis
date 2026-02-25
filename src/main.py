import json
import os
import getpass
import hashlib
import sys

from src.retrieval.embedder import LocalEmbedder
from src.retrieval.similarity import build_candidates
from datetime import datetime


def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def rank_results(results):
    return sorted(results, key=lambda x: x["weighted_score"], reverse=True)


def load_embeddings_manifest(path):
    """
    Load minimal embedding metadata produced by Phase 2 doc embedding precompute.

    Expected file: data/embeddings_manifest.json
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def sha256_manifest_json(path: str) -> str:
    """
    Stable hash of manifest.json content.

    We canonicalize JSON (sort_keys=True) so hash does not change
    due to whitespace or key order differences.
    """
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)

    canonical = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def verify_embeddings_match_manifest(manifest_path: str, embedding_info: dict) -> None:
    """
    Fail fast if the current manifest.json does not match the manifest used
    to generate doc embeddings.
    """
    expected = embedding_info.get("source_manifest_hash")
    if not expected:
        raise ValueError("Embedding manifest missing 'source_manifest_hash'.")

    current = sha256_manifest_json(manifest_path)

    if current != expected:
        raise RuntimeError(
            "Embeddings/manifest mismatch.\n"
            f"- embeddings_manifest.source_manifest_hash: {expected}\n"
            f"- current manifest.json hash:              {current}\n\n"
            "Fix: re-run `python -m src.retrieval.doc_embeddings` to regenerate cached embeddings."
        )


def log_run(top_results, config, run_reason, embedding_info=None):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/riswis_run_{timestamp}.log"

    os.makedirs("logs", exist_ok=True)

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
        log_file.write(
            f"tier_multipliers: {config['retrieval']['tier_multipliers']}\n\n"
        )

        if embedding_info:
            log_file.write("Embedding Context:\n")
            log_file.write(f"model_name: {embedding_info.get('model_name')}\n")
            log_file.write(f"embedding_dim: {embedding_info.get('embedding_dim')}\n")
            log_file.write(f"normalized: {embedding_info.get('normalized')}\n")
            log_file.write(
                f"source_manifest_hash: {embedding_info.get('source_manifest_hash')}\n"
            )
            log_file.write(
                f"created_at_utc: {embedding_info.get('created_at_utc')}\n\n"
            )

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

    print(f"Using manifest: {manifest_path}")

    config_path = os.path.join("config", "settings.json")
    config = load_config(config_path)

    tier_multipliers = config["retrieval"]["tier_multipliers"]
    results = []

    # Phase 2 retrieval: embed query -> raw cosine similarities
    embedder = LocalEmbedder(model_name="all-MiniLM-L6-v2")

    # Query input (CLI > fallback default)
    if len(sys.argv) > 1:
        query = sys.argv[1].strip()
    else:
        query = "long horizon drift evaluation in adaptive systems"

    if not query:
        raise ValueError("Query cannot be empty.")

    q_vec = embedder.embed(query, normalize=True)

    candidates = build_candidates(q_vec)

    for c in candidates:
        doc_id = c["doc_id"]
        tier = c["tier"]
        similarity = c["raw_sim"]

        if tier not in tier_multipliers:
            raise ValueError(f"Unknown tier '{tier}' in manifest.")

        multiplier = tier_multipliers[tier]
        weighted_score = similarity * multiplier

        results.append(
            {
                "doc_id": doc_id,
                "tier": tier,
                "similarity": similarity,
                "multiplier": multiplier,
                "weighted_score": weighted_score,
            }
        )

    results = rank_results(results)

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

    embedding_manifest_path = os.path.join("data", "embeddings_manifest.json")
    embedding_info = None
    if os.path.exists(embedding_manifest_path):
        embedding_info = load_embeddings_manifest(embedding_manifest_path)
        verify_embeddings_match_manifest(manifest_path, embedding_info)
    log_run(top_results, config, run_reason, embedding_info=embedding_info)
