RISWIS — Phase 2 Validation Checklist (Formal)
Purpose

Phase 2 validation is behavioral, not performance-based.

We validate that RISWIS governance remains deterministic, reproducible, and integrity-enforced when real semantic similarity is introduced (embeddings + cosine similarity), without modifying Phase 1 governance logic.

Out of Scope

Phase 2 does not evaluate:

Retrieval “accuracy”

Benchmark scores

Model quality comparisons

Runtime speed or scaling

In Scope

Phase 2 validates:

Deterministic governance behavior under real similarity variation

Tier weighting behavior under multiplier changes

Integrity enforcement under manifest tampering

Reproducibility of similarity + ranking under repeated runs

Preconditions
Environment

Same machine + Python version for all tests

Same embedding model identifier and parameters

Same document set + same manifest (except in integrity tests)

Same config (except in multiplier sensitivity tests)

Required Outputs

CLI output showing ranked results

Log file(s) capturing:

query text

embedding model ID/version (or your internal “embedder_id”)

candidates with raw similarity

tier multiplier applied

final score

final ranking order

manifest verification outcome (pass/fail)

Test 1 — Similarity Spread Test
Goal

Confirm ranking changes only when semantic similarity meaningfully changes, while tier weighting stays consistent.

Commands

Run each query once:

python -m src.main "drift evaluation"
python -m src.main "neural retrieval systems"
python -m src.main "peer reviewed governance ranking"
python -m src.main "random unrelated topic"
Observe / Record

For each query, capture:

top-K ranked documents

raw similarity distribution (min/median/max)

whether tier multipliers changed ordering, and where

Pass Criteria

Ranking shifts track semantic similarity shifts (not randomness).

Tier multipliers apply consistently (no missing/incorrect tier application).

When similarity is close, higher tier should reliably win (as designed by policy).

Fail Signals

Unstable ranking across clearly similar queries

Tier multipliers not applied / applied inconsistently

Tier ordering flips without similarity justification (or without multiplier change)

Test 2 — Multiplier Sensitivity Test
Goal

Quantify where governance weighting overrides semantics.

Method

Use identical queries while altering only tier multipliers.

Baseline Multipliers

Set in config/settings.json (or equivalent):

T1: 1.2

T2: 1.0

T3: 0.9

Run:

python -m src.main "drift evaluation"
python -m src.main "peer reviewed governance ranking"
Stress Multipliers

Change to:

T1: 2.0

T2: 1.0

T3: 0.3

Run the same commands again.

Observe / Record

For each query:

compare rank ordering between baseline and stress multipliers

identify documents whose ordering changed only due to multiplier change

record the similarity deltas where flips occur

Pass Criteria

Rank flips occur in predictable ways explained by multiplier changes.

A clear “override zone” becomes visible:

high-tier wins when similarity is close

similarity wins when separation is large (unless deliberately designed otherwise)

Fail Signals

Changes that don’t correlate with multiplier modification

Multiplier changes not reflected in final scoring

Tier labels missing or mismatched vs manifest

Test 3 — Integrity Enforcement Test
Goal

Prove the system fails fast when integrity assumptions are violated.

Manipulations (do one at a time)

Change a document’s text content

Add a new document file

Modify a document tier in the manifest

Modify a stored embedding (if applicable)

Command
python -m src.main "test"

(or run any query if integrity check is always on)

Expected

Run should fail fast with manifest mismatch / integrity error.

Logs should clearly indicate:

what failed (hash mismatch / missing doc / unknown doc / tier mismatch)

which file/doc caused it

Pass Criteria

Integrity failure is deterministic and immediate.

No ranking output is produced when integrity fails (unless explicitly allowed in “unsafe mode,” which should be off by default).

Fail Signals

Continues to run despite mismatch

Silent failures or unclear logs

Partial success without explicit “unsafe override” flag

Test 4 — Reproducibility Test
Goal

Verify identical inputs yield identical outputs (similarity + ranking), confirming determinism survives embedding integration.

Command

Run the same query twice with no changes:

python -m src.main "drift evaluation"
python -m src.main "drift evaluation"
Compare

raw similarity scores per candidate

final scores after multipliers

ranking order

log trace (should be byte-for-byte comparable where feasible)

Pass Criteria

Similarity values match (within your defined tolerance; ideally exact if cached).

Final rankings match exactly.

Governance trace is identical.

Fail Signals

Similarity drift across runs with no changes

Ranking changes across runs

Embedder metadata inconsistent between runs

Phase 2 Freeze Conditions

Phase 2 is considered validated and freeze-ready when:

All four tests pass

The repo contains:

validation checklist (this doc)

sample logs from each test category

the exact settings.json used (or config snapshot)

a short “Phase 2 Freeze Note” stating:

what was validated

what was explicitly not tested

the embedder ID/model used

Deliverable Artifacts

Minimum artifacts to archive/tag:

docs/phase2_validation_checklist.md

logs/phase2/ folder containing:

similarity_spread_test.log

multiplier_sensitivity_baseline.log

multiplier_sensitivity_stress.log

integrity_fail_examples.log

reproducibility_run1.log

reproducibility_run2.log

config/settings.phase2.freeze.json (snapshot)

One-Line Phase 2 Claim

“Phase 2 validates deterministic governance under real semantic similarity variation, with reproducible scoring and fail-fast integrity enforcement.”