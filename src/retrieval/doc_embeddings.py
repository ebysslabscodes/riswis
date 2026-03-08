# src/retrieval/doc_embeddings.py

"""
RISWIS – Phase 2 / Phase 3 Retrieval Layer
------------------------------------------

Document embedding precompute + cache writer.

This script:
    - Loads document records from data/manifest.json
    - Resolves document text from either:
        * inline `content`
        * file-backed `path`
    - Generates embeddings for each resolved document text
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

It prepares retrieval artifacts only. Ranking policy remains elsewhere.
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

    OR (Phase 3 file-backed format):
    [
        {
            "doc_id": "doc_001",
            "tier": "T1",
            "path": "data/docs/doc_001.txt"
            ... optional fields ...
        },
        ...
    ]

    Minimal required keys:
        - doc_id
        - tier
        - one of: content OR path
    """
    with open(manifest_path, "r", encoding="utf-8") as f:
        docs = json.load(f)

    if not isinstance(docs, list) or len(docs) == 0:
        raise ValueError(f"Expected a non-empty list in {manifest_path}")

    for i, d in enumerate(docs):
        for key in ("doc_id", "tier"):
            if key not in d:
                raise ValueError(f"Missing '{key}' in doc index {i}: {d}")

        if "content" not in d and "path" not in d:
            raise ValueError(
                f"Doc index {i} must include either 'content' or 'path': {d}"
            )

    return docs


def resolve_doc_text(doc: Dict[str, Any]) -> str:
    """
    Resolve the actual text used for embedding.

    Priority:
        1. inline 'content'
        2. file-backed 'path'
    """
    if "content" in doc and doc["content"] is not None:
        text = str(doc["content"]).strip()
        if not text:
            raise ValueError(f"Doc '{doc['doc_id']}' has empty inline 'content'.")
        return text

    if "path" in doc and doc["path"] is not None:
        doc_path = ROOT / Path(doc["path"])
        if not doc_path.exists():
            raise FileNotFoundError(
                f"Doc '{doc['doc_id']}' path does not exist: {doc_path}"
            )

        text = doc_path.read_text(encoding="utf-8").strip()
        if not text:
            raise ValueError(f"Doc '{doc['doc_id']}' file is empty: {doc_path}")
        return text

    raise ValueError(
        f"Doc '{doc.get('doc_id', '<unknown>')}' must include either 'content' or 'path'."
    )


def write_embeddings_and_meta(
    docs: List[Dict[str, Any]],
    resolved_texts: List[str],
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
        for i, (d, text) in enumerate(zip(docs, resolved_texts)):
            rec = {
                "row_index": i,
                "doc_id": d["doc_id"],
                "tier": d["tier"],
                "source": d.get("source"),
                "title": d.get("title"),
                "path": d.get("path"),
                "content_hash": sha256_text(text),
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

    Scope: intentionally minimal.
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

    resolved_texts = [resolve_doc_text(d) for d in docs]

    normalized = True
    vectors = embedder.embed(
        resolved_texts, normalize=normalized
    )  # normalized vectors for cosine

    out_vec_path = DATA_DIR / EMBEDDINGS_FILENAME
    out_meta_path = DATA_DIR / META_FILENAME
    out_embed_manifest_path = DATA_DIR / EMBEDDINGS_MANIFEST_FILENAME

    write_embeddings_and_meta(
        docs, resolved_texts, vectors, out_vec_path, out_meta_path
    )

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
