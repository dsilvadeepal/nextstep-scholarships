# Staged candidate corpus handoff

## Local activation — October 16, 2026, 9:03 p.m. ET

Following explicit user approval, `candidate-2026-10-16-v4` is now the active local
catalog: **39 records / 31 families / 201 chunks / 63 official documents**.
The version name retains its immutable staging identifier. The previous
`verified-2026-10-14-v2` catalog (18 records / 174 chunks) and Pinecone namespace
remain intact and ready for rollback. Both namespaces passed fresh ID/count/query
readiness checks before the transactional active-pointer switch.

Post-activation checks against the actual app on port 8014 passed: 39-record
matching; cited UAB no-superscore answer; Cooke transcript/income source distinctions
with explicit sponsor-confirmation caveats; HOPE 2027–28 coverage gap without paid
calls; invalid-program rejection; and server-side version pinning despite a stale
client version. Phone and desktop rendered 39 awards without page errors or
horizontal overflow. These are smoke checks, not a new 47-case evaluation run.

Activation cost $0. Testing added **$0.00807484**; cumulative ledger total is
**$2.08153838 / $5**, including four previously recorded ambiguous-call liabilities.
There are zero outstanding reservations. The original live ledger remains authoritative.
No Docker, hosted deployment, namespace deletion, or `.env` edits occurred.

Receipts: `artifacts/reports/local-activation-2026-10-16.json` and
`artifacts/reports/local-activation-smoke-2026-10-16.json`.
The frozen bundle and vector metadata preserve their staging-time
`inactive_candidate` label; runtime activation is determined solely by the SQL
active-corpus pointer and namespace, not that historical metadata field. Evidence,
source hashes, cycle metadata, and all source references were preserved unchanged.

Rollback from the repository root (does not reset or restore the spend ledger):

```sh
PYTHONPATH=backend:scripts .venv/bin/python - <<'PYROLLBACK'
from sqlalchemy import create_engine
from reviewed_runtime import live_settings
from nextstep.repository import Repository
repo = Repository(create_engine(live_settings().database_url))
repo.activate_version('candidate-2026-10-16-v4', 'verified-2026-10-14-v2')
print(repo.active_version())
PYROLLBACK
```

The checkpoints below describe pre-activation work and remain historical evidence.

Final candidate: `candidate-2026-10-16-v4`, inactive and query-ready in Pinecone.
Bundle: `data/expanded-corpus-2026-10-16.json`, also preserved as
`data/corpus-candidate-2026-10-16-v4.json`.
SHA-256: `ecbaad48333345838dd2bd983298f8a0127723b5eb35c104c7f87bd87f09c52e`.

## Verified collection and coverage

- 68 new official URL attempts; 65 downloaded and parsed. Three failures:
  Georgia United (SSL), an unavailable FSU benefits URL, and the initial South
  Alabama freshman URL. FSU's current application page and South Alabama's
  linked canonical freshman page succeeded.
- 39 award records across 31 families; 63 contributing official documents,
  including 19 from the previous corpus and 44 from this collection.
- 201 packed chunks, 175 distinct chunk texts. The 26 repeated texts are shared
  UA/Auburn policies copied for award-level retrieval isolation; they do not
  count as additional unique coverage.
- 72,138 passage tokens before the embedding heading prefix. Most chunks are
  within 75–500 tokens. Two explicit short exceptions retain a current deadline
  calendar and the caveat beside UAH's indivisible 750-token award table.
- The 500–550 chunk aspiration was not met. Reaching it from this material would
  require padding or excessive fragmentation. Assess answer coverage first.

The source inventory and decisions are in
`data/expansion-source-inventory-2026-10-16.json` and
`data/expansion-source-review-2026-10-16.json`. Candidate deferred coverage is
`data/expanded-coverage-2026-10-16.json`. Failed downloads, older cycles and
unpublished new applications were not embedded as current rules.

## Data and metadata gates

The candidate-specific loader is `scripts/expanded_runtime.py:load_candidate`.
It validates models, program/version relationships, original-byte hashes,
admitted source spans, exact quotes and offsets, heading/date preservation,
cycle fields, field/condition reference resolution and registered exclusions.
It does not establish that every source interpretation is correct.

Multi-section chunks contain the original source heading followed by its exact
body quote. Every reference shares the chunk's source and preserves its own
section, page and offsets. Pinecone metadata includes `evidence_refs_json` for
all references, plus the existing source/program/version fields, cycle fields,
review status/date, family, timing and `publication_status=inactive_candidate`.
All 201 metadata objects matched exact readback, including the serialized
references. Readiness checked fetched IDs, namespace count and query probes.

Recipient biographies, winner lists/stories, testimonials and promotional
background are excluded from embedded passages and catalog evidence. Raw
snapshots remain only for provenance. Four previously embedded chunks overlapped
the initial exclusion register; their replacement passages omit those spans.
Further mixed-page exclusions include GSU scholar outcomes, Ron Brown alumni
testimonials/statistics, Taco Bell scholar profiles, historical dates and page
navigation. See the explicit selection manifest and review notes.

## Source limitations that evaluation must preserve

- Cooke's official pages conflict on transcript stage and gross income versus
  AGI. The record is `conflicting`, with the unresolved distinctions recorded.
- Elks MVS and Legacy pages conflict on accepting multiple ENF awards. Those
  stacking sentences are excluded and the conflict is recorded. Legacy's
  deadline is 11:59 **AM** Pacific, not midnight.
- Sawnee's current page states January 8, 2027; its linked PDFs still contain
  2025/2026 dates. PDFs are excluded; verify the current application packet.
- GT uses the current dated April 2027 calendar. Undated March wording is
  excluded. Its structured record is the Georgia-resident route; non-GA dates
  in the calendar must not be substituted as that route's deadline.
- Levine's record deadline is the October 15 nomination gate. Already-nominated
  applicants have later November deadlines. Hagan's record is the fall
  application route; the spring application is a separate timeline.
- Gates is closed by its September 15, 2026 date despite a stale Open label.
- Unknown GPA scales/types remain unknown. New records include a full-rule
  confirmation condition so a few structured facts cannot establish complete
  personal eligibility. Some program eligibility remains in cited text rather
  than machine-evaluable conditions.
- Clemson, Emory, Mercer and other dated-coverage gaps remain explicit; do not
  substitute unrelated university rules. Georgia credit-union leads did not
  yield a complete current-cycle addition in this pass.

## Cost and validation evidence

The only cumulative ledger remains `artifacts/nextstep-live.db`. Embedding v3
used 76,741 input tokens and cost $0.00153482. An evidence-binding correction
for the GT Georgia-route condition produced v4; all 201 embeddings were reused
from cache, with zero additional OpenAI charge. Both namespaces remain intact.

Cumulative spend after staging: **$0.98532120 of $5**. Embedding model remains
OpenAI `text-embedding-3-small`, 1,536 dimensions. User declined a 512-dimension
comparison. No Docker, secret-file edits or activation occurred.

Receipts: `artifacts/reports/candidate-2026-10-16-v4-validation.json` and
`artifacts/reports/candidate-2026-10-16-v4-staged-index.json`.
Final free checks: 131 backend tests passed, two additional native PostgreSQL
checks passed, Ruff and whitespace checks passed. Three new chunking
tests exercise exact multi-section provenance, excluded middle spans and the
75-token overlap limit with repeated text.

## App and evaluation handoff

`data/expanded-eval-reference-2026-10-16.json` supplies 21 source-grounded tuning
cases, including all newly admitted families. They are source references, not
results or fresh held-out evidence. The primary workstream subsequently took
ownership of the remaining app fixes and paid testing. The 21 expanded cases and
26 previously exposed regressions passed against the candidate using the default
50/50 hybrid method. Real API, phone/desktop browser, live chat, citation and print
checks also completed. The cumulative ledger is now **$2.07346354 of $5**.
See [the final build/test report](EXPANDED_BUILD_TEST_REPORT_2026-10-16.md) for exact
run IDs, intermediate failures, source-context corrections and limitations.

The active pointer remains `verified-2026-10-14-v2`. Do not activate until source,
retrieval, answer-support and app gates pass. Keep the old namespace and ledger
for rollback. Hosted paid operation/deployment is a separate gate.
