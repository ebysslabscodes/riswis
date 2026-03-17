Why RISWIS?

Most retrieval systems combine semantic similarity, ranking heuristics, and source preference inside a single scoring path.

When trust policy changes — for example, prioritizing verified sources over weakly verified content — ranking behavior often shifts through opaque scoring adjustments that are difficult to inspect or reproduce.

RISWIS separates these concerns into explicit layers:

semantic similarity remains responsible for candidate retrieval

governance remains responsible for ranking policy

This allows ranking policy to be inspected, modified, validated, and audited independently of the embedding model.

RISWIS explores a practical systems question:

What happens when semantic relevance and trust policy disagree, and can that disagreement remain observable?

Why This Matters

Retrieval systems increasingly influence:

which documents appear first

which sources are treated as credible

which evidence becomes visible to downstream systems

In many production pipelines:

trust policy is hidden inside scoring behavior

ranking changes are difficult to explain

source preference is difficult to isolate from semantic similarity

RISWIS treats ranking governance as an explicit system layer rather than an implicit side effect.

This makes it possible to observe when policy:

reinforces semantic relevance

remains neutral

overrides stronger semantic matches

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

Similarity scoring identifies candidate documents

A deterministic governance layer applies configurable tier multipliers

Similarity modeling and trust policy remain independent

Engineering Highlights

Separation of similarity modeling and ranking governance

Deterministic policy-based ranking layer

Raw semantic rank and weighted rank visibility

Rank delta tracking per document

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

RISWIS uses Sentence Transformers model all-MiniLM-L6-v2 for local embeddings.

The model functions without authentication, though unauthenticated requests may trigger warnings or lower rate limits.

Windows PowerShell
$env:HF_TOKEN="YOUR_TOKEN"
Mac / Linux
export HF_TOKEN="YOUR_TOKEN"

Authentication is optional for standard local use.

Example Output
doc_107 | tier=T1 | raw_rank=3 | weighted_rank=1 | delta=+2 | sim=0.365 | mult=1.5 | weighted=0.548
doc_109 | tier=T3 | raw_rank=1 | weighted_rank=3 | delta=-2 | sim=0.630 | mult=0.7 | weighted=0.441

This output makes semantic ranking and policy intervention visible in the same execution trace.

Policy Effect
Without weighting
doc_A = 0.630
doc_B = 0.365
With RISWIS governance
doc_A = 0.630 × 0.7 = 0.441
doc_B = 0.365 × 1.5 = 0.548

Similarity-only ranking places doc_A above doc_B.

RISWIS governance ranks doc_B above doc_A.

This demonstrates explicit policy intervention through a visible ranking layer.

Tier Weighting (Policy Layer)

RISWIS exposes ranking governance through configurable tier multipliers.

Example configuration
T1 = 1.5   high-trust sources
T2 = 1.0   baseline sources
T3 = 0.7   lower-trust sources
Example source interpretation

T1 = peer-reviewed papers, verified documentation, formal references

T2 = technical articles, neutral summaries, general reference text

T3 = forums, casual summaries, weakly verified content

The tier layer remains configurable so policy can evolve without modifying similarity logic.

Retrieval Integrity

In RISWIS, retrieval integrity means rankings are produced under conditions that remain:

transparent

reproducible

resistant to silent corpus drift

Integrity enforcement includes:

explicit ranking policy

deterministic configuration

audit logging

strict separation between similarity and governance

verification that cached embeddings match the current manifest

If the corpus changes while cached embeddings remain stale, RISWIS aborts retrieval rather than producing potentially invalid rankings.

System Phases
Phase 1 — Governance Isolation

Tag: phase1-stable

Phase 1 validated deterministic ranking behavior without embeddings.

Features

deterministic ranking skeleton

tier multiplier enforcement

strict validation

Top-K control

seed reproducibility

structured logging

Phase 2 — Semantic Retrieval + Integrity Verification

Tag: phase2-stable

Phase 2 introduced semantic retrieval while preserving deterministic governance.

Enhancements

local sentence-transformer embeddings

cached embeddings

cosine similarity retrieval

CLI query support

manifest-bound cache verification

Phase 3 — Controlled Governance Behavior Validation

Tags: phase3-control-freeze, phase3-rankdelta

Phase 3 expanded RISWIS into controlled ranking behavior analysis.

Enhancements

expanded controlled corpus

raw rank visibility

weighted rank visibility

rank delta tracking

override mapping

Phase 3 Result

Three observable policy behaviors emerged:

defensible override

neutral reinforcement

sensitivity under close semantic competition

This established that RISWIS can classify policy behavior rather than only apply weighting.

Phase 4 — Controlled External Topic Validation

Tags: phase4a-medical, phase4b-sensitivity, phase4c-publicsource

Phase 4 tested whether RISWIS governance remains stable outside RISWIS-native retrieval language.

Phase 4A — External Semantic Collision Testing

A controlled medical corpus was introduced across trust tiers:

T1 formal medical phrasing

T2 neutral explanatory phrasing

T3 casual public-facing phrasing

Observed result:

casual phrasing often won raw semantic rank

formal sources frequently won weighted rank

governance overrides remained interpretable

Phase 4B — Close Semantic Competition

Phase 4B tested near-equal semantic similarity across tier boundaries.

Observed result:

small similarity differences exposed governance sensitivity

override thresholds became measurable

weighted movement remained deterministic

Phase 4C — Public-Source Semantic Stress Testing

Phase 4C introduced short public-source fatigue excerpts across trust tiers.

Sources included:

T1 public clinical source

T2 public explanatory source

T3 public general health source

Observed result:

public-source T1 material remained strongly competitive after weighting

public-source T2 material stayed visible in mid-rank positions

public-source T3 material could win raw semantic rank when phrasing matched directly, but still fall after weighting

This confirmed that RISWIS governance remained visible even when controlled internal wording was replaced by mixed public-source language.

Phase 4 Conclusion

Phase 4 demonstrated that RISWIS governance survives external topic variation while preserving visible policy behavior.

This moved RISWIS beyond internal proof-of-concept into broader retrieval behavior validation.

Embedding Validation (MTEB Baseline)

Embedding baseline validated using Massive Text Embedding Benchmark baseline references.

Observed semantic similarity scores:

STSBenchmark Spearman: 0.8203
SICK-R Spearman: 0.7758

MTEB validates embedding quality only.

RISWIS governance remains independent of embedding performance.

Logging

Each execution produces an audit log containing:

query

configuration

tier multipliers

embedding metadata

raw rank

weighted rank

delta movement

Logs are written to:

logs/
Corpus Integrity Enforcement

RISWIS binds embeddings to the manifest used during embedding generation.

If the manifest changes without regeneration:

RuntimeError: Embeddings/manifest mismatch.
Fix: re-run python -m src.retrieval.doc_embeddings

This prevents stale embeddings from producing invalid rankings.

Validation artifacts remain in:

Validation/
Repository Structure
config/
data/
src/
logs/
Validation/
tools/
What RISWIS Is Not

Not a production RAG system

Not a benchmark suite

Not a policy standard

RISWIS is a governance-first retrieval prototype focused on transparent ranking behavior.

Phase 5 — What Comes Next

Phase 5 moves beyond controlled corpus validation into broader retrieval stress testing.

Expected focus:

larger corpus expansion

more difficult semantic collisions

policy behavior under mixed-domain retrieval

measurable governance pressure zones

potential tier calibration studies

Phase 5 is necessary because earlier phases proved governance visibility under controlled conditions.

The next technical question is:

Can governance remain explainable as retrieval complexity increases?

That is where RISWIS now advances.

Author

Ronald Reed
Independent Researcher
Ebysslabs