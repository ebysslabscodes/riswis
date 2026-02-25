# src/retrieval/doc_embeddings.py

"""
RISWIS – Phase 2 Retrieval Layer
--------------------------------

Document embedding precompute + cache writer.

This script:
    - Loads document records from data/manifest.json
    - Generates embeddings for each document's `content`
    - Writes embeddings to disk for fast, repeatable retrieval

Outputs (aligned by row_index):
    - data/doc_embeddings.npz        (numpy array "vectors" of shape: N x dim)
    - data/doc_meta.jsonl            (one JSON record per doc with row_index mapping)
    - data/embeddings_manifest.json  (minimal metadata about the embedding run)

Architectural Boundary:
    - This module does NOT rank results
    - This module does NOT apply tier multipliers
    - This module does NOT enforce top-K
    - This module does NOT implement governance logic

It prepares retrieval artifacts only. Ranking policy remains in Phase 1 code.
"""

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from src.retrieval.embedder import LocalEmbedder

ROOT = Path(__file__).resolve().parents[2]  # repo root
DATA_DIR = ROOT / "data"

MANIFEST_FILENAME = "manifest.json"
EMBEDDINGS_FILENAME = "doc_embeddings.npz"
META_FILENAME = "doc_meta.jsonl"
EMBEDDINGS_MANIFEST_FILENAME = "embeddings_manifest.json"


def sha256_text(text: str) -> str:
    """Stable hash for content identity checks and cache validation."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_manifest_json(path: Path) -> str:
    """
    Stable hash of manifest.json content.

    Canonicalizes JSON so hash doesn't change due to whitespace or key order.
    """
    obj = json.loads(path.read_text(encoding="utf-8"))
    canonical = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_manifest(manifest_path: Path) -> List[Dict[str, Any]]:
    """
    Load the document manifest.

    Expected format (top-level list):
    [
        {
            "doc_id": "doc_001",
            "tier": "T1",
            "content": "..."
            ... optional fields ...
        },
        ...
    ]

    Minimal required keys:
        - doc_id
        - tier
        - content
    """
    with open(manifest_path, "r", encoding="utf-8") as f:
        docs = json.load(f)

    if not isinstance(docs, list) or len(docs) == 0:
        raise ValueError(f"Expected a non-empty list in {manifest_path}")

    for i, d in enumerate(docs):
        for key in ("doc_id", "tier", "content"):
            if key not in d:
                raise ValueError(f"Missing '{key}' in doc index {i}: {d}")

    return docs


def write_embeddings_and_meta(
    docs: List[Dict[str, Any]],
    vectors: np.ndarray,
    out_vec_path: Path,
    out_meta_path: Path,
) -> None:
    """
    Persist embeddings + metadata to disk.

    Contract:
        - vectors[i] corresponds to docs[i]
        - meta records include row_index for deterministic alignment
    """
    # Save vectors (compressed)
    np.savez_compressed(out_vec_path, vectors=vectors.astype(np.float32))

    # Save aligned metadata as JSONL
    with open(out_meta_path, "w", encoding="utf-8") as f:
        for i, d in enumerate(docs):
            rec = {
                "row_index": i,
                "doc_id": d["doc_id"],
                "tier": d["tier"],
                "source": d.get("source"),
                "title": d.get("title"),
                "content_hash": sha256_text(d["content"]),
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def write_embedding_manifest(
    *,
    model_name: str,
    dim: int,
    normalized: bool,
    source_manifest_path: Path,
    out_path: Path,
) -> None:
    """
    Write minimal metadata describing how the current doc embeddings were produced.

    Scope: intentionally minimal (Phase 2).
    """
    source_manifest_hash = sha256_manifest_json(source_manifest_path)

    record = {
        "model_name": model_name,
        "embedding_dim": dim,
        "normalized": normalized,
        "source_manifest_hash": source_manifest_hash,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)


def main() -> None:
    manifest_path = DATA_DIR / MANIFEST_FILENAME
    docs = load_manifest(manifest_path)

    embedder = LocalEmbedder(model_name="all-MiniLM-L6-v2")

    texts = [d["content"] for d in docs]
    normalized = True
    vectors = embedder.embed(
        texts, normalize=normalized
    )  # normalized vectors for cosine

    out_vec_path = DATA_DIR / EMBEDDINGS_FILENAME
    out_meta_path = DATA_DIR / META_FILENAME
    out_embed_manifest_path = DATA_DIR / EMBEDDINGS_MANIFEST_FILENAME

    write_embeddings_and_meta(docs, vectors, out_vec_path, out_meta_path)

    write_embedding_manifest(
        model_name=embedder.model_name,
        dim=vectors.shape[1],
        normalized=normalized,
        source_manifest_path=manifest_path,
        out_path=out_embed_manifest_path,
    )

    print("Saved:", out_vec_path)
    print("Saved:", out_meta_path)
    print("Saved:", out_embed_manifest_path)
    print("Docs:", len(docs), "| Dim:", vectors.shape[1], "| Normalize:", normalized)


if __name__ == "__main__":
    # Development entrypoint: run as module from repo root:
    #   python -m src.retrieval.doc_embeddings
    main()
