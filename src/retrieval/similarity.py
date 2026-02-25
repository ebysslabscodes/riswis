# src/retrieval/similarity.py

"""
RISWIS – Phase 2 Retrieval Layer
--------------------------------

Similarity computation over cached document embeddings.

This module:
    - Loads cached document vectors (data/doc_embeddings.npz)
    - Loads aligned doc metadata (data/doc_meta.jsonl)
    - Computes raw similarity scores between a query vector and doc vectors

Architectural Boundary:
    - Does NOT apply tier multipliers
    - Does NOT rank results
    - Does NOT enforce top-K
    - Does NOT implement governance logic

Output Contract:
    Produces candidates shaped like:
        {"doc_id": str, "tier": str, "raw_sim": float}

These candidates are consumed by the Phase 1 policy layer (rank_results()).
"""

import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

ROOT = Path(__file__).resolve().parents[2]  # repo root
DATA_DIR = ROOT / "data"

EMBEDDINGS_FILENAME = "doc_embeddings.npz"
META_FILENAME = "doc_meta.jsonl"


def load_doc_vectors() -> np.ndarray:
    """
    Load cached document embedding vectors.

    Returns
    -------
    np.ndarray
        Shape (N, dim) float32.
    """
    vec_path = DATA_DIR / EMBEDDINGS_FILENAME

    if not vec_path.exists():
        raise FileNotFoundError(f"Missing embeddings file: {vec_path}")

    data = np.load(vec_path)
    vectors = data["vectors"]

    return vectors.astype(np.float32)


def load_doc_meta() -> List[Dict[str, Any]]:
    """
    Load doc metadata aligned by row_index.

    Returns
    -------
    List[dict]
        Each record contains row_index, doc_id, tier, etc.
    """
    meta_path = DATA_DIR / META_FILENAME

    if not meta_path.exists():
        raise FileNotFoundError(f"Missing metadata file: {meta_path}")

    meta: List[Dict[str, Any]] = []

    with open(meta_path, "r", encoding="utf-8") as f:
        for line in f:
            meta.append(json.loads(line))

    return meta


def cosine_raw_sim(query_vec: np.ndarray, doc_vecs: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity scores.

    Assumes embeddings are normalized (unit length). Under normalization:
        cosine(q, d) = dot(q, d)

    Parameters
    ----------
    query_vec : np.ndarray
        Shape (dim,) or (1, dim)
    doc_vecs : np.ndarray
        Shape (N, dim)

    Returns
    -------
    np.ndarray
        Shape (N,) float32 similarity scores.
    """
    q = query_vec[0] if query_vec.ndim == 2 else query_vec

    if q.shape[0] != doc_vecs.shape[1]:
        raise ValueError(
            f"Dimension mismatch: query dim {q.shape[0]} "
            f"!= doc dim {doc_vecs.shape[1]}"
        )

    return (doc_vecs @ q).astype(np.float32)


def build_candidates(query_vec: np.ndarray) -> List[Dict[str, Any]]:
    """
    Build candidate list for the policy layer.

    Output records contain only:
        - doc_id
        - tier
        - raw_sim

    Parameters
    ----------
    query_vec : np.ndarray
        Query embedding vector (normalized preferred).

    Returns
    -------
    List[dict]
        Candidate list to pass into rank_results().
    """
    doc_vecs = load_doc_vectors()
    meta = load_doc_meta()

    if len(meta) != doc_vecs.shape[0]:
        raise ValueError("Metadata row count does not match embedding row count.")

    sims = cosine_raw_sim(query_vec, doc_vecs)

    candidates: List[Dict[str, Any]] = []

    for i, m in enumerate(meta):
        candidates.append(
            {
                "doc_id": m["doc_id"],
                "tier": m["tier"],
                "raw_sim": float(sims[i]),
            }
        )

    return candidates
