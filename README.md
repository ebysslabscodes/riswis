RISWIS

Retrieval Integrity & Structured Weighted Information System

A governance-first retrieval prototype: separate similarity scoring from ranking policy (tier weighting) with fail-fast corpus/embedding integrity and audit logs.

python -m src.main --query "drift evaluation" --topk 5 --json
Why RISWIS?

Most retrieval systems mix similarity scoring, ranking heuristics, and trust policy inside a single scoring path.

When ranking policy changes (for example, prioritizing verified sources over low-trust content), developers often must modify retrieval logic directly.

RISWIS separates similarity from governance so ranking policy can be inspected, changed, validated, and audited independently of the embedding model.

RISWIS implements a retrieval architecture where semantic similarity and ranking governance remain explicit, configurable, and reproducible.

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

Separation of similarity modeling and ranking governance

Deterministic policy-based ranking layer

Manifest-bound embedding cache integrity verification

CLI interface with machine-readable JSON output

Structured audit logging for reproducibility

Quick Start
Create environment
python -m venv .venv
Activate environment
Windows
.\.venv\Scripts\Activate.ps1
Install dependencies
pip install -r requirements.txt
Generate document embeddings
python -m src.retrieval.doc_embeddings
Run retrieval
python -m src.main --query "drift evaluation"
Return JSON output
python -m src.main --query "drift evaluation" --json
List corpus documents
python -m src.main --list-docs
Optional: Hugging Face Authentication

RISWIS uses sentence-transformers/all-MiniLM-L6-v2 for local embeddings.

The model works without authentication, but unauthenticated requests may show warnings and may have lower rate limits.

Windows PowerShell
$env:HF_TOKEN="YOUR_TOKEN"
Mac / Linux
export HF_TOKEN="YOUR_TOKEN"

Authentication is optional for normal local use.

Example Output
doc_001 | tier=T1 | sim=0.664 | mult=1.5 | weighted=0.996
doc_002 | tier=T3 | sim=0.495 | mult=0.7 | weighted=0.347
Policy effect
Without weighting:
doc_001 = 0.664
doc_002 = 0.495

With RISWIS governance:
doc_001 = 0.664 × 1.5 = 0.996
doc_002 = 0.495 × 0.7 = 0.347

This demonstrates that ranking policy remains explicit and measurable.

Tier Weighting (Policy Layer)

RISWIS exposes ranking governance through configurable tier multipliers.

Example configuration
T1 = 1.5   high-trust sources
T2 = 1.0   baseline sources
T3 = 0.7   lower-trust sources

Example source interpretation:

T1 = peer-reviewed papers, verified documentation

T2 = general technical articles, unverified but credible sources

T3 = forums, user-generated content, weakly verified claims

The tier layer remains configurable so ranking policy can evolve without modifying the similarity engine.

RISWIS treats ranking policy as an explicit system component rather than hidden heuristics.

Retrieval Integrity

In RISWIS, retrieval integrity means ranking results are produced under conditions that are:

transparent

reproducible

resistant to silent system drift

Integrity enforcement includes:

explicit ranking policy via configurable tier multipliers

deterministic configuration and audit logging

strict separation between similarity scoring and ranking governance

verification that cached embeddings match the document manifest

If the corpus changes while cached embeddings remain stale, RISWIS aborts retrieval rather than producing potentially corrupted rankings.

System Phases

RISWIS development progressed in two implementation phases.

Phase 1 — Governance Isolation

Tag: phase1-stable

Phase 1 implemented deterministic ranking without real embeddings.

Features

deterministic ranking skeleton

configuration-driven tier multipliers

strict tier validation

Top-K enforcement

seed-controlled reproducibility

structured audit logging

Similarity scores were simulated to validate ranking behavior independently of embedding models.

git checkout phase1-stable
python -m src.main
Phase 2 — Semantic Retrieval + Integrity Verification

Phase 2 integrates real semantic retrieval while preserving deterministic governance.

Enhancements

sentence-transformer embeddings (all-MiniLM-L6-v2)

cached document embeddings (doc_embeddings.npz)

cosine similarity candidate retrieval

CLI query interface

JSON output mode

manifest-bound embedding cache

fail-fast corpus integrity verification

python -m src.main --query "drift evaluation"
Logging

Each execution produces an audit log containing:

query

configuration

tier multipliers

embedding metadata

ranked results

Logs are written to:

logs/
Corpus Integrity Enforcement

RISWIS binds cached embeddings to the manifest used to generate them.

If the manifest changes without regenerating embeddings, retrieval aborts before ranking.

RuntimeError: Embeddings/manifest mismatch.
Fix: re-run python -m src.retrieval.doc_embeddings

This prevents silent corruption caused by stale embeddings.

Validation artifacts are stored in:

Validation/
What RISWIS Is Not

Not a production RAG system

Not a benchmark suite

Not a policy standard

RISWIS is a governance prototype focused on transparent retrieval behavior.

Reproducibility and Validation

RISWIS separates runtime telemetry from curated validation artifacts.

Runtime Logs (logs/)

Every retrieval run produces an immutable log containing:

query

ranking configuration

similarity scores

weighted ranking results

execution metadata

Validation Runs (Validation/runs/)

Curated validation runs document controlled experiments including:

drift-related queries

unrelated query handling

tier weighting behavior

integrity violation scenarios

manifest mutation detection

embedding regeneration recovery

These artifacts demonstrate deterministic behavior and fail-fast safeguards.

Repository Structure
config/       configuration files
data/         manifest and cached embeddings
src/          retrieval and ranking implementation
logs/         runtime audit logs
Validation/   validation runs and artifacts
Relationship to CAS 2.0

RISWIS was developed alongside CAS 2.0 as part of broader work on transparent system behavior under explicit constraints.

CAS 2.0 evaluates long-horizon drift under frozen parameters.

RISWIS applies similar design discipline to retrieval systems through explicit ranking governance and reproducible policy enforcement.

Author

Ronald Reed
Independent Engineer
Ebysslabs