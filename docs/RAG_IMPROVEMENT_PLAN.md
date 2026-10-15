# Answer construction and targeted retrieval comparison

Approved scope: phase 1 then phase 2; no Docker, no source re-chunking, no corpus re-embedding. Preserve existing work and compare actual results within the shared $5 cumulative ledger.

## Recovery

Baseline commit `c4fddf4`, tag `checkpoint/pre-rag-answer-2026-10-15`; implementation branch `feat/rag-answer-comparison`. To inspect/recover baseline without deleting current work, create a separate worktree from the tag or switch to a new branch from it after saving current changes. Do not reset uncommitted work. Ignored runtime database and reports are backed up under `artifacts/checkpoints/pre-rag-answer-2026-10-15`. Secrets remain ignored. Never restore an old usage ledger after paid calls: cumulative expenditure must survive rollback.

## Design and implementation sequence

1. Grounded answer construction: complete retrieved passages, bounded profile and prior user context, typed per-program claims with exact supporting quotations; deterministic provenance validation and an independent model review. Unsupported claims become gaps, with no automatic retry. Source quotes remain separate from explanation. Existing matching results remain authoritative for structured profile conditions. Add official handoff links for deferred coverage without inventing future-cycle rules.
2. Phase-1 tests and checkpoint. Preserve results with baseline retrieval.
3. Targeted retrieval: keep 50/50 RRF, same corpus, eight-passage/5,000-token cap. Reserve relevant existing passages for requested rule facets (thresholds, score policy, deadline, application/materials) per selected program before filling with general ranks. No paid reranking service. Retain baseline policy for A/B comparison.
4. Freeze five demo inputs and expected answer requirements, plus boundary cases. Compare phase 1 versus phase 1+2 using the same dense candidate cache and generator. Save full outputs, claims, verification decisions, retrieval IDs, timings and ledger deltas. Treat these as exposed regression cases, not held-out evidence.
5. Inspect outputs against the independently checked rules; report coverage, contradictions, abstentions and cost. Select the better approach only after results. Run backend and frontend checks, update docs and commit final state.

## Limits

Exact quotes and typed output do not prove entailment. Model review can err, so independent human-readable rubric scoring and regression tests remain necessary. A missing passage must result in an explicit gap, never use model memory. Metadata/corpus boundaries remain pinned. No open-ended agent loop or added API credentials.
