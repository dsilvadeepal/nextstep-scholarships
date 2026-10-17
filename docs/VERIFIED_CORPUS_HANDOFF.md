# Verified local corpus handoff

Checkpoint: October 14, 2026, after the second-pass source audit. The owner approved local ingestion/testing under the original cumulative $5 cap and separately authorized setup coordination. No Docker is required.

## Transfer and preserve

The sanitized source archive includes the current tracked/unignored source tree and reviewed public source data. It excludes `.env`, all provider keys, `.git`, artifacts/databases, virtual environments, node modules, test reports, and the local `.replit` file. **Preserve the remote `.replit` environment/workflow configuration and remote development secrets during sync.** No merge/push/deployment is implied by creating this package.

The exact active corpus is `data/reviewed-corpus-2026-10-14.json` (`verified-2026-10-14-v2`): 18 records, 174 chunks, 19 contributing source documents. It already exists in the shared `nextstep-scholarships` Pinecone index. Do not rerun paid extraction or embeddings to import the SQL manifest. Do not import old `live-reviewed-sources.yaml` or the provisional v6 corpus. Retain the new version string and `data/reviewed-coverage-2026-10-14.json` together: the latter prevents answers about deferred programs from substituting other awards.

## Hosted catalog setup

Keep `LIVE_CALLS_ENABLED=false`. Use the remote's existing approved development `DATABASE_URL`, run its schema migration, then call `scripts/reviewed_runtime.load_bundle()` and `nextstep.ingest.cli.stage_or_resume(repo, version, records, chunks)` against that database. `load_bundle` validates exact quotes, source hashes/locations, version consistency and admitted section boundaries without any provider calls.

Stage first. Before marking ready/activating, match the corpus checksum with the handoff receipt and confirm the intended Pinecone index/namespace agrees with the local publication receipt. The trusted receipt records 174 vectors fetched with exact metadata and query-ready probes. If a different Pinecone index is selected, perform its own readiness verification before activation. Do not claim live hosted RAG has been verified merely because catalog pages load.

The remote should run the normal `nextstep.app` entry point with its environment settings. `scripts/start_reviewed_local.py` is deliberately **local-only**, uses the existing local SQLite ledger, and must not become a hosted startup command. Hosted admin remains fail-closed; evaluation can remain local for the current simple demo scope.

## One cumulative budget

Authoritative ledger: local ignored `artifacts/nextstep-live.db`. Recorded total after authorized test calls: **$0.72160134 of $5**. Subsequent local chat calls accrue to it. This is a local estimate based on provider usage, with conservative charges for ambiguous calls; provider billing is the final authority.

The source packet contains no database or live keys, and its spending receipt is informational. It is **not** a budget reset or a concurrent hosted allowance. Before hosted paid calls are enabled, stop local paid execution and transfer/reconcile the latest cumulative liability to the hosted authoritative ledger, or configure both to use one shared authoritative ledger. Never run independent local and hosted instances each with a fresh $5 cap. Setup has acknowledged that hosted paid calls remain disabled pending that handoff.

## Executed evidence and limits

- 84 backend tests passed; both native PostgreSQL integration checks passed separately. Seven frontend unit tests, TypeScript/build, 18 mocked browser checks, and six real local phone/desktop/API/print checks passed.
- Source-grounded regression comparison: 26/26 semantic and 26/26 hybrid, run `d7190260-2f19-4cc5-9926-6315e8dc43f2`.
- Fresh held-out output under the old rubric scored 5/6 per method because the correct Clemson gap was marked unresponsive. Original raw run `d4ae9518-f1a8-4035-823a-d0a508fed8a3` remains unchanged. Explicit expected-gap rubric rescoring on saved outputs gives 6/6, with no paid replay or claim of fresh holdout. This is explained in the source-review report and sanitized receipt.
- Older failed attempts remain recorded; the HOPE-to-Georgia-Southern substitution was fixed and moved to regression coverage. Conservative unknowns remain for criteria not represented by the profile or unspecified GPA scale/type.
- The broader Georgia/five-neighbor-state research register includes deferred, historical, conflicting and access-limited programs. It does not imply all 28 university entry points or all their awards are in the app. Current 2027–28 HOPE/Zell Miller rules, unresolved Georgia Tech/CFA Team Member wording, and inaccessible UAB rules were not admitted.

Use `docs/SECOND_PASS_REVIEW_2026-10-14.md` for the complete admission/defer decisions and metadata contract. A passed local pilot is not a public production release or an independent human audit of every scholarship rule.
