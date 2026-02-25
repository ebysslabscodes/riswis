RISWIS

Retrieval Integrity & Structured Weighted Information System

Why This Exists

Modern LLM-adjacent retrieval systems frequently combine similarity scoring, heuristic adjustments, and trust weighting in ways that are implicit, undocumented, or difficult to reproduce.

When ranking logic is opaque, systems risk amplifying “junk in, junk out” dynamics through hidden policy decisions.

RISWIS isolates the retrieval policy layer and makes weighting behavior explicit, configurable, and auditable.

The goal is not to eliminate bias, but to expose and structure it so that ranking decisions can be inspected, reproduced, and revised.

Project Status

RISWIS has completed two foundational phases:

Phase 1 — Governance Isolation (tag: phase1-stable)

Phase 2 — Local Embeddings + Integrity Verification (current main branch)

Phase 1 established deterministic policy isolation.
Phase 2 introduces real semantic retrieval while preserving policy transparency and auditability.

Phase 1 — Deterministic Ranking Skeleton

Phase 1 establishes the structural foundation for retrieval governance:

Config-driven tier multipliers

Deterministic scoring (seed-controlled)

Top-K enforcement

Strict tier validation (unknown tiers raise explicit errors)

Isolated ranking policy via rank_results()

Reproducible audit logging

Who / Why / Seed trace metadata

Runnable sample manifest

Similarity scores are simulated to validate ranking logic and audit structure independently of embedding variability.

This phase prioritizes:

Separation of configuration and logic

Deterministic reproducibility

Explicit policy weighting

Structured trust and traceability

Layered system development

To reproduce Phase 1 exactly:

git checkout phase1-stable
python -m src.main
Phase 2 — Local Embeddings + Integrity Verification

Phase 2 integrates semantic similarity while preserving the deterministic policy layer established in Phase 1.

Enhancements include:

Sentence-transformer embeddings (all-MiniLM-L6-v2)

Cached document vectors (doc_embeddings.npz)

Cosine similarity scoring

Canonical manifest hashing (prevents stale embedding misuse)

CLI query input

Policy layer unchanged

Phase 2 tests whether deterministic governance remains stable when real embedding-based similarity is introduced.

Tier Weighting: Open Design Surface

The tier-weighting multiplier system remains the most structurally significant and currently unvalidated component of RISWIS.

Open questions include:

How are credibility tiers defined?

Who assigns tier levels?

What criteria determine tier placement?

How should tier definitions evolve over time?

Do tier assignments introduce systematic bias?

RISWIS does not treat tiering as a solved problem.

Instead, the framework:

Makes tier definitions explicit

Separates tier assignment from similarity scoring

Applies transparent, configurable multipliers

Logs tier influence per run

Because tier weighting directly influences ranking order, its design must remain inspectable and versioned.