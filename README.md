# RISWIS

**Retrieval Integrity & Structured Weighted Information System**

A governance-first retrieval prototype that separates semantic similarity from ranking policy through explicit tier weighting, corpus integrity enforcement, and auditable ranking behavior.

```bash
python -m src.main --query "drift evaluation" --topk 5 --json
```

## Why RISWIS?

Most retrieval systems combine semantic similarity, ranking heuristics, and trust policy inside a single scoring path.

When trust rules change — for example, prioritizing verified sources over weakly verified content — developers often must alter retrieval logic directly or rely on opaque ranking adjustments that are difficult to inspect.

RISWIS isolates those concerns.

Semantic similarity remains one layer.

Governance remains another.

This makes ranking policy visible, configurable, testable, and reproducible.

RISWIS exists to explore a simple question:

> What happens when semantic relevance and trust policy disagree — and can that disagreement remain interpretable?

---

## Why This Matters

Modern retrieval pipelines increasingly influence what users see first, what evidence systems prefer, and what information appears trustworthy.

Yet in many systems:

* trust policy is hidden
* ranking shifts are difficult to explain
* source preference is embedded inside opaque scoring paths

RISWIS treats ranking governance as a system component that should be inspectable rather than assumed.

This makes it possible to observe:

* when policy reinforces relevance
* when policy remains neutral
* when policy overrides stronger semantic matches

---

## Retrieval Architecture

```text
query
↓
embedding similarity
↓
candidate documents
↓
tier-weighted governance layer
↓
ranked output
```

* Similarity scoring identifies candidate documents
* A deterministic governance layer applies configurable tier multipliers
* Similarity modeling and trust policy remain independent

---

## Engineering Highlights

* Separation of similarity modeling and ranking governance
* Deterministic policy-based ranking layer
* Raw semantic rank vs weighted rank visibility
* Rank delta tracking per document
* Manifest-bound embedding cache integrity verification
* CLI interface with machine-readable JSON output
* Structured audit logging for reproducibility

---

## Quick Start

### Create environment

```bash
python -m venv .venv
```

### Activate environment

**Windows**

```bash
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Generate document embeddings

```bash
python -m src.retrieval.doc_embeddings
```

### Run retrieval

```bash
python -m src.main --query "drift evaluation"
```

### Return JSON output

```bash
python -m src.main --query "drift evaluation" --json
```

### List corpus documents

```bash
python -m src.main --list-docs
```

---

## Optional: Hugging Face Authentication

RISWIS uses `sentence-transformers/all-MiniLM-L6-v2` for local embeddings.

The model works without authentication, though rate limits and warnings may appear when unauthenticated.

**Windows PowerShell**

```powershell
$env:HF_TOKEN="YOUR_TOKEN"
```

**Mac / Linux**

```bash
export HF_TOKEN="YOUR_TOKEN"
```

Authentication is optional for normal local use.

---

## Example Output

```text
doc_107 | tier=T1 | raw_rank=3 | weighted_rank=1 | delta=+2 | sim=0.365 | mult=1.5 | weighted=0.548
doc_109 | tier=T3 | raw_rank=1 | weighted_rank=3 | delta=-2 | sim=0.630 | mult=0.7 | weighted=0.441
```

This makes semantic ranking and policy intervention visible in the same output.

---

## Policy Effect

### Without weighting

```text
doc_A = 0.630
doc_B = 0.365
```

### With RISWIS governance

```text
doc_A = 0.630 × 0.7 = 0.441
doc_B = 0.365 × 1.5 = 0.548
```

Similarity-only ranking would place `doc_A` above `doc_B`.

RISWIS governance ranks `doc_B` above `doc_A`.

This demonstrates explicit policy intervention rather than hidden scoring.

---

## Tier Weighting (Policy Layer)

RISWIS exposes ranking governance through configurable tier multipliers.

### Example configuration

```text
T1 = 1.5   high-trust sources
T2 = 1.0   baseline sources
T3 = 0.7   lower-trust sources
```

### Example source interpretation

* T1 = peer-reviewed papers, verified documentation, formal references
* T2 = technical articles, neutral summaries, credible reference text
* T3 = forums, casual summaries, weakly verified content

The tier layer remains configurable so ranking policy can evolve without modifying similarity logic.

---

## Retrieval Integrity

In RISWIS, retrieval integrity means rankings are produced under conditions that remain:

* transparent
* reproducible
* resistant to silent drift

Integrity enforcement includes:

* explicit ranking policy
* deterministic configuration
* audit logging
* strict separation between similarity and governance
* verification that cached embeddings match the current manifest

If the corpus changes while embeddings remain stale, RISWIS aborts retrieval rather than producing corrupted rankings.

---

## System Phases

RISWIS development currently spans four structured stages.

### Phase 1 — Governance Isolation

**Tag:** `phase1-stable`

Phase 1 validated deterministic ranking without embeddings.

#### Features

* deterministic ranking skeleton
* tier multiplier enforcement
* strict validation
* Top-K control
* seed reproducibility
* structured logging

---

### Phase 2 — Semantic Retrieval + Integrity Verification

**Tag:** `phase2-stable`

Phase 2 introduced local semantic retrieval while preserving deterministic governance.

#### Enhancements

* sentence-transformer embeddings (`all-MiniLM-L6-v2`)
* cached embeddings
* cosine similarity retrieval
* CLI query support
* manifest-bound cache verification

---

### Phase 3 — Controlled Governance Behavior Validation

Phase 3 expanded RISWIS into controlled ranking behavior analysis.

#### Enhancements

* expanded controlled corpus
* raw rank visibility
* weighted rank visibility
* rank delta tracking
* override mapping

#### Phase 3 Result

Three behavior classes became observable:

* defensible override
* neutral reinforcement
* sensitivity / possible over-correction

This established that RISWIS can classify policy behavior instead of only applying weighting.

---

### Phase 4A — Controlled External Topic Testing (in progress)

Phase 4A introduces controlled semantic collisions outside RISWIS-native retrieval topics.

#### Current additions

A medical trio was added across trust tiers:

* T1 formal medical phrasing
* T2 neutral explanatory phrasing
* T3 casual public-facing phrasing

#### Initial observation

Across blood-pressure-related queries:

* formal sources often remain weighted winners
* casual phrasing often wins raw semantic ranking
* trust policy creates repeatable but interpretable overrides

This is the first controlled evidence of semantic-policy tension outside native retrieval topics.

---

## Embedding Validation (MTEB Baseline)

Embedding baseline validated using MTEB with `sentence-transformers/all-MiniLM-L6-v2`.

### Observed semantic similarity scores

* STSBenchmark Spearman: 0.8203
* SICK-R Spearman: 0.7758

MTEB validates embedding quality only.

RISWIS governance remains independent of embedding performance.

---

## Logging

Each run produces an audit log containing:

* query
* configuration
* tier multipliers
* embedding metadata
* raw rank
* weighted rank
* delta movement

Logs are written to:

```text
logs/
```

---

## Corpus Integrity Enforcement

RISWIS binds embeddings to the manifest used to generate them.

If the manifest changes without regeneration:

```text
RuntimeError: Embeddings/manifest mismatch.
Fix: re-run python -m src.retrieval.doc_embeddings
```

This prevents silent ranking corruption.

Validation artifacts remain in:

```text
Validation/
```

---

## Reproducibility and Validation

RISWIS separates runtime telemetry from curated validation artifacts.

### Runtime Logs

Every retrieval run records immutable execution evidence.

### Validation Runs

Controlled validation captures:

* trust-sensitive queries
* override behavior
* integrity failures
* regeneration recovery
* rank movement analysis

---

## Repository Structure

```text
config/       configuration files
data/         manifest and embeddings
src/          retrieval and ranking implementation
logs/         runtime audit logs
Validation/   controlled validation artifacts
tools/        utility scripts
```

---

## What RISWIS Is Not

* Not a production RAG system
* Not a benchmark suite
* Not a policy standard

RISWIS is a governance-first retrieval prototype focused on transparent ranking behavior.

---

## Author

**Ronald Reed**
Independent Engineer
Ebysslabs
