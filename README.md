RISWIS

Retrieval Integrity & Structured Weighted Information System

RISWIS is an experimental retrieval framework that separates semantic similarity from ranking governance, allowing trust weighting and ranking behavior to remain explicit, configurable, and auditable.

Many retrieval systems mix similarity scoring, heuristics, and policy decisions inside opaque ranking logic.

RISWIS explores a simpler structure:

query
↓
embedding similarity
↓
candidate documents
↓
tier-weighted governance layer
↓
ranked output

The goal is not to eliminate bias, but to make ranking policy visible, reproducible, and inspectable.

Retrieval Integrity

In RISWIS, retrieval integrity means that ranking results are produced under conditions that are transparent, reproducible, and resistant to silent system drift.

Integrity in this framework requires:

explicit ranking policy (tier multipliers are configurable)

deterministic configuration and logging

separation between similarity scoring and ranking governance

validation that cached embeddings match the document manifest

If the corpus changes while cached embeddings remain stale, RISWIS aborts retrieval rather than producing potentially corrupted rankings.

Project Status

RISWIS currently contains two completed phases.

Phase 1 — Governance Isolation

Tag: phase1-stable

Phase 1 isolates the ranking policy layer from similarity scoring.

Features:

deterministic ranking skeleton

config-driven tier multipliers

strict tier validation

Top-K enforcement

seed-controlled reproducibility

structured audit logging

Similarity scores are simulated in this phase to validate ranking behavior independently of embedding models.

Run Phase 1:

git checkout phase1-stable
python -m src.main
Phase 2 — Semantic Retrieval + Integrity Verification

Phase 2 introduces real semantic similarity while preserving the deterministic governance layer.

Enhancements include:

sentence-transformer embeddings (all-MiniLM-L6-v2)

cached document vectors (doc_embeddings.npz)

cosine similarity retrieval

CLI query input

manifest-bound embedding cache

fail-fast corpus integrity verification

Example run:

python -m src.main "drift evaluation"

Example output:

doc_001 | tier=T1 | sim=0.664 | mult=1.5 | weighted=0.996
doc_002 | tier=T3 | sim=0.495 | mult=0.7 | weighted=0.347

Each run produces an audit log containing:

query

configuration

tier multipliers

embedding metadata

ranked results

Logs are written to:

logs/
Integrity Enforcement

RISWIS binds cached embeddings to the manifest used to generate them.

If the document manifest changes without regenerating embeddings, the system aborts before retrieval:

RuntimeError: Embeddings/manifest mismatch.
Fix: re-run `python -m src.retrieval.doc_embeddings`

This prevents silent corruption of retrieval results due to stale embeddings.

Validation artifacts are stored in:

Validation/
Tier Weighting (Open Design Surface)

RISWIS exposes ranking governance through configurable tier multipliers.

Example configuration:

T1 = 1.5
T2 = 1.0
T3 = 0.7

This layer intentionally remains an open design surface.

Questions the framework explores include:

how credibility tiers should be defined

who assigns tier levels

how tier systems evolve over time

whether tier weighting introduces systematic bias

RISWIS treats tier governance as an explicit and inspectable ranking policy rather than hidden ranking logic.

Repository Structure
config/        configuration files
data/          document manifest and cached embeddings
src/           retrieval and ranking implementation
logs/          run audit logs
Validation/    reproducibility tests and validation artifacts
Current Scope

RISWIS is not a benchmark system and makes no performance claims.

The project focuses on:

retrieval governance transparency

deterministic ranking behavior

embedding integrity verification

structured weighting experiments

Author

Ronald Reed
Independent Researcher
Ebysslabs