# src/retrieval/_sim_test.py

"""
Quick similarity smoke test.

Runs:
    - embeds a query
    - loads cached doc embeddings
    - computes raw cosine similarity
    - prints candidates sorted by raw_sim
"""

from src.retrieval.embedder import LocalEmbedder
from src.retrieval.similarity import build_candidates

if __name__ == "__main__":
    emb = LocalEmbedder()

    query = "long horizon drift evaluation in adaptive systems"
    q_vec = emb.embed(query, normalize=True)

    cands = build_candidates(q_vec)
    cands = sorted(cands, key=lambda x: x["raw_sim"], reverse=True)

    print("Query:", query)
    for c in cands:
        print(c)
