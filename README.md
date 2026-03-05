RISWIS

Retrieval Integrity & Structured Weighted Information System

RISWIS implements a retrieval architecture where semantic similarity and ranking governance are separated so that trust-weighting policies remain explicit, configurable, and auditable.

Many retrieval systems mix similarity scoring, heuristics, and policy decisions inside opaque ranking logic. RISWIS isolates the ranking policy layer so weighting decisions can be inspected, reproduced, and changed without modifying the similarity engine.

The system demonstrates retrieval governance, ranking transparency, and corpus integrity enforcement.

Retrieval Architecture

query
↓
embedding similarity
↓
candidate documents
↓
tier-weighted governance layer
↓
ranked output

Similarity scoring identifies candidate documents.
A deterministic governance layer applies configurable tier multipliers before final ranking.

This architecture keeps similarity modeling and trust policy independent.

Engineering Highlights

• Separation of similarity modeling and ranking governance
• Deterministic policy-based ranking layer
• Manifest-bound embedding cache integrity verification
• CLI interface with machine-readable JSON output
• Structured audit logging for reproducibility

Quick Start

Create environment

python -m venv .venv

Activate environment

Windows

.venv\Scripts\activate

Install dependencies

pip install -r requirements.txt

Generate document embeddings

python -m src.retrieval.doc_embeddings

Run retrieval

python -m src.main --query "drift evaluation"

Return JSON output

python -m src.main --query "drift evaluation" --json

Example Output

doc_001 | tier=T1 | sim=0.664 | mult=1.5 | weighted=0.996
doc_002 | tier=T3 | sim=0.495 | mult=0.7 | weighted=0.347

Retrieval Integrity

In RISWIS, retrieval integrity means ranking results are produced under conditions that are:

transparent
reproducible
resistant to silent system drift

Integrity enforcement includes:

• explicit ranking policy via configurable tier multipliers
• deterministic configuration and audit logging
• strict separation between similarity scoring and ranking governance
• verification that cached embeddings match the document manifest

If the corpus changes while cached embeddings remain stale, RISWIS aborts retrieval rather than producing potentially corrupted rankings.

System Phases

RISWIS development progressed in two implementation phases.

Phase 1 — Governance Isolation

Tag: phase1-stable

Phase 1 implemented the deterministic ranking framework without real embeddings.

Features

deterministic ranking skeleton
configuration-driven tier multipliers
strict tier validation
Top-K enforcement
seed-controlled reproducibility
structured audit logging

Similarity scores were simulated to validate ranking behavior independently of embedding models.

Run Phase 1

git checkout phase1-stable
python -m src.main

Phase 2 — Semantic Retrieval + Integrity Verification

Phase 2 integrates real semantic retrieval while preserving the deterministic governance layer.

Enhancements include

sentence-transformer embeddings (all-MiniLM-L6-v2)
cached document embeddings (doc_embeddings.npz)
cosine similarity candidate retrieval
CLI query interface
JSON output mode
manifest-bound embedding cache
fail-fast corpus integrity verification

Example run

python -m src.main --query "drift evaluation"

Logging

Each execution produces an audit log containing:

query
configuration
tier multipliers
embedding metadata
ranked results

Logs are written to

logs/

Corpus Integrity Enforcement

RISWIS binds cached embeddings to the document manifest used to generate them.

If the manifest changes without regenerating embeddings, the system aborts before retrieval.

RuntimeError: Embeddings/manifest mismatch.
Fix: re-run python -m src.retrieval.doc_embeddings

This prevents silent corruption caused by stale embeddings.

Validation artifacts are stored in

Validation/

Tier Weighting (Policy Layer)

RISWIS exposes ranking governance through configurable tier multipliers.

Example configuration

T1 = 1.5
T2 = 1.0
T3 = 0.7

The tier layer remains configurable so ranking policy can evolve without modifying the similarity engine.

Design considerations include

how credibility tiers are assigned
who controls tier definitions
how tier policies evolve over time
whether tier weighting introduces systemic bias

RISWIS treats ranking policy as an explicit system component rather than hidden heuristics.

Repository Structure

config/ — configuration files
data/ — document manifest and cached embeddings
src/ — retrieval and ranking implementation
logs/ — runtime audit logs
Validation/ — curated validation runs and reproducibility artifacts

System Scope

RISWIS focuses on retrieval infrastructure and governance rather than model benchmarking.

The project demonstrates

retrieval governance transparency
deterministic ranking behavior
embedding cache integrity enforcement
structured weighting policies
reproducible retrieval runs

Reproducibility and Validation

RISWIS separates runtime telemetry from curated validation artifacts.

Runtime Logs (logs/)

Every retrieval run produces an immutable log containing

query
ranking configuration
similarity scores
weighted ranking results
execution metadata

Validation Runs (Validation/runs)

Curated validation runs document controlled experiments including

drift-related queries
unrelated query handling
tier weighting behavior
integrity violation scenarios
manifest mutation detection
embedding regeneration recovery

These artifacts demonstrate deterministic behavior and system safeguards.

Author

Ronald Reed
Independent Engineer
Ebysslabs