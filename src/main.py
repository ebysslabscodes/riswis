import argparse
import getpass
import hashlib
import json
import os
import sys
from datetime import datetime
from typing import List, Optional

from src.retrieval.embedder import LocalEmbedder
from src.retrieval.similarity import build_candidates


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def rank_results(results: List[dict]) -> List[dict]:
    return sorted(results, key=lambda x: x["weighted_score"], reverse=True)


def load_embeddings_manifest(path: str) -> dict:
    """
    Load minimal embedding metadata produced by Phase 2 doc embedding precompute.
    Expected file: data/embeddings_manifest.json
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_manifest_docs(manifest_path: str) -> List[dict]:
    """
    Supports BOTH manifest formats:

    Format A (current): top-level list
      [
        {"doc_id": "...", "tier": "...", "content": "...", ...},
        ...
      ]

    Format B (optional future): object with "documents"
      {
        "documents": [
          {"doc_id": "...", "tier": "...", "content": "...", ...}
        ]
      }
    """
    with open(manifest_path, "r", encoding="utf-8") as f:
        obj = json.load(f)

    if isinstance(obj, list):
        docs = obj
    elif isinstance(obj, dict):
        docs = obj.get("documents", [])
        if not isinstance(docs, list):
            raise ValueError("manifest.json 'documents' must be a list.")
    else:
        raise ValueError(
            "manifest.json must be a list or an object containing 'documents'."
        )

    # Minimal validation
    for d in docs:
        if "doc_id" not in d or "tier" not in d:
            raise ValueError("Each manifest doc must include 'doc_id' and 'tier'.")

    return docs


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


def validate_manifest_tiers(docs: List[dict], tier_multipliers: dict) -> None:
    """
    Fail fast if manifest contains tiers not present in config.
    """
    manifest_tiers = {d["tier"] for d in docs}
    config_tiers = set(tier_multipliers.keys())

    unknown = manifest_tiers - config_tiers
    if unknown:
        raise ValueError(
            f"Manifest contains unknown tiers not in config: {sorted(unknown)}"
        )


def log_run(
    top_results: List[dict],
    config: dict,
    run_reason: str,
    query: str,
    top_k: int,
    embedding_info: Optional[dict] = None,
) -> None:
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

        log_file.write(f"Query: {query}\n\n")

        log_file.write("Configuration:\n")
        log_file.write(f"top_k: {top_k}\n")
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


def main() -> int:
    manifest_path = os.path.join("data", "manifest.json")
    if not os.path.exists(manifest_path):
        manifest_path = os.path.join("data", "sample_manifest.json")

    print(f"Using manifest: {manifest_path}")

    config_path = os.path.join("config", "settings.json")
    config = load_config(config_path)
    tier_multipliers = config["retrieval"]["tier_multipliers"]

    parser = argparse.ArgumentParser(description="RISWIS retrieval system")
    parser.add_argument("--query", type=str, default=None, help="Search query text")
    parser.add_argument(
        "--topk",
        type=int,
        default=config["retrieval"]["top_k"],
        help="Number of top results to return",
    )
    parser.add_argument(
        "--reason",
        type=str,
        default="manual_test",
        help="Reason for run (logged for audit)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print results as JSON to stdout (machine-readable)",
    )
    parser.add_argument(
        "--list-docs",
        action="store_true",
        help="List documents in the manifest and exit",
    )

    args = parser.parse_args()

    # Load docs once (used by list-docs and tier validation)
    docs = load_manifest_docs(manifest_path)

    # Utility: list docs and exit (NO embedding work, NO tier validation)
    if args.list_docs:
        print("\nDocuments in corpus:\n")
        for d in docs:
            extra = []
            if d.get("title"):
                extra.append(d["title"])
            if d.get("source"):
                extra.append(f"source={d['source']}")
            extra_str = f" | {' | '.join(extra)}" if extra else ""
            print(f'{d["doc_id"]} | tier={d["tier"]}{extra_str}')
        print(f"\nTotal documents: {len(docs)}")
        return 0

    # Normal retrieval requires query
    if args.query is None:
        parser.error(
            'Missing --query (unless --list-docs is used). Example: --query "drift evaluation"'
        )

    query = args.query.strip()
    if not query:
        parser.error("Query cannot be empty.")

    # Validate tiers only for retrieval (fail fast before embedding work)
    validate_manifest_tiers(docs, tier_multipliers)

    top_k = args.topk
    run_reason = args.reason

    # Fail-fast integrity check BEFORE doing retrieval work
    embedding_manifest_path = os.path.join("data", "embeddings_manifest.json")
    embedding_info = None
    if os.path.exists(embedding_manifest_path):
        embedding_info = load_embeddings_manifest(embedding_manifest_path)
        verify_embeddings_match_manifest(manifest_path, embedding_info)

    # Phase 2 retrieval: embed query -> raw cosine similarities
    embedder = LocalEmbedder(model_name="all-MiniLM-L6-v2")
    q_vec = embedder.embed(query, normalize=True)

    candidates = build_candidates(q_vec)

    results: List[dict] = []
    for c in candidates:
        doc_id = c["doc_id"]
        tier = c["tier"]
        similarity = c["raw_sim"]

        # Tier already validated against config, but keep guard anyway
        if tier not in tier_multipliers:
            raise ValueError(f"Unknown tier '{tier}' in manifest/config.")

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
    top_results = results[:top_k]

    if args.json:
        payload = {
            "query": query,
            "reason": run_reason,
            "top_k": top_k,
            "results": [
                {
                    "doc_id": r["doc_id"],
                    "tier": r["tier"],
                    "similarity": round(float(r["similarity"]), 6),
                    "multiplier": r["multiplier"],
                    "weighted_score": round(float(r["weighted_score"]), 6),
                }
                for r in top_results
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("\nRanked results:")
        for r in top_results:
            print(
                f'{r["doc_id"]} | tier={r["tier"]} | '
                f'sim={r["similarity"]:.3f} | '
                f'mult={r["multiplier"]} | '
                f'weighted={r["weighted_score"]:.3f}'
            )

    log_run(
        top_results, config, run_reason, query, top_k, embedding_info=embedding_info
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
