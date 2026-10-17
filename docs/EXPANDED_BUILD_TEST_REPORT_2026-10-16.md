# Expanded corpus build and testing — October 16, 2026

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

Local build and candidate testing are complete. The candidate remains **inactive**:
`candidate-2026-10-16-v4`, with 39 award records, 31 families, 63 contributing
official documents, and 201 chunks (175 distinct texts). The authoritative active
version is still `verified-2026-10-14-v2`: 18 records and 174 chunks.

The ingestion scope explicitly excluded activation. No hosted deployment,
publication, namespace deletion, Docker operation, or `.env` edit occurred.

## Executed checks

| Check | Observed result |
| --- | --- |
| Backend | 131 passed; two PostgreSQL checks skipped in the default invocation |
| Native PostgreSQL | Both skipped checks passed separately on the dedicated Unix socket |
| Frontend units | 12 passed |
| Phone/desktop browser regressions | 20 passed; mocked API fixtures |
| TypeScript and Vite production build | Passed |
| Ruff and whitespace | Passed |
| Real candidate matching API | 39 records/matches for three fictional profile variants |
| Real candidate browser | Phone/desktop catalog, shortlist, disabled-service behavior, no horizontal overflow or page errors |
| Real paid candidate chat | Browser-to-API-to-Pinecone/OpenAI path passed for an unselected UAB question; original passages and links displayed |
| Final focused-context API | Same UAB question returned a direct cited no-superscore answer, only UAB retrieval, and no invented test-date restriction |
| Printing | One-page candidate plan; heading, award, unresolved requirements, and official links verified in extracted text and rendered page |

The candidate app checks used an isolated catalog fixture database. All paid
providers used the original `artifacts/nextstep-live.db` ledger. They did not
create a second spending ledger or alter the authoritative active pointer.
Viewport screenshots replayed the saved real answer for visual inspection without
additional paid calls; they are not additional live-answer runs.

## Saved live evaluation

Both suites use the existing equal-weight hybrid method, `text-embedding-3-small`
at 1,536 dimensions, targeted passage selection, and the same frozen v4 corpus.
No 512-dimension or alternate retrieval-method comparison was performed.

| Exposed tuning suite | Saved run | Cases passed | Checked claim support | Required evidence found | Answer p95 |
| --- | --- | ---: | ---: | ---: | ---: |
| Expanded source cases | `717ae56b-6a7b-4d5b-a4df-fb672122b2a9` | 21/21 | 31/31 | 23/23 | 3.75 s |
| Previously exposed regressions on the candidate | `6726a4e6-d131-4105-a814-444d10f77681` | 26/26 | 37/37 | 25/25 | 5.27 s |

Each complete run passed its automated critical-case and citation gates. These are
two separate tuning runs, not one independent held-out trial. The 26-case run
preceded the final Cooke-only source-distinction renderer. A subsequent free
check confirmed that renderer produces no additional blocks for any of those 26
saved requests; the complete 21-case suite was run with the final renderer.

References retain the original required retrieval units. Judge context also
contains the other admitted, source-bound passages needed to assess an answer's
additional claims. This happens after retrieval and does not feed answer-key
material into the student answer path. Repeated source units are deduplicated
when building the judge context.

The evaluator uses the same model family as answer generation. Its support
judgments are correlated automated assessments, not independent scholarship
accuracy measurements. Source spot-checks caught errors and incomplete answers
that earlier automated passes missed. No fresh held-out accuracy is claimed.

## Fixes demonstrated by failures and retests

- Reject whitespace-only questions at the API boundary before a model call.
- Remove stale deferred-program aliases for programs now covered by the candidate.
- Prevent ordinary words in award names, including “and” and “general,” from
  falsely blocking valid claims as cross-award contamination.
- Require factual judge claims to match displayed answer blocks exactly; an
  empty non-answer cannot pass merely because the judge read the source fact.
- Use a separate schema for gap-only judgments instead of a provider array
  constrained to zero items. Preserve provider failures without automatic retries.
- Preserve renewal-versus-entry distinctions, final test dates versus exclusive
  test windows, and each award's own evidence IDs.
- Narrow unselected questions naming an explicit catalog acronym such as UAB
  or UAH. Explicit user-selected programs continue to control the search scope.
- For a simple negative superscore-policy question, draft from the explicit
  policy line; keep the complete original passage for review and citations.
  Questions also asking about dates, GPA, official scores, or multiple parts
  retain the broader context.
- Present reviewed transcript/income source distinctions as cited explanations
  only when both corresponding retrieved contexts are available. Preserve
  sponsor confirmation instead of choosing a settled rule.
- Avoid adding an unasked award-classification paragraph to a priority-deadline
  answer.

Historical failures, incomplete runs, and superseded scores remain saved. For
example, runs `578df683-06a5-4ebe-a561-3e004290795c` and
`a3168bda-79d1-4ba8-8e6f-b3038d377038` exposed the citation guard, incomplete
judge references, and responsiveness problems. Run
`9cb19fda-8a3e-4165-833f-1ff7d82127c1` retains a provider timeout. An earlier
automated 21/21 pass was not accepted as final proof because its UAB answer was
empty and its Watson-Brown answer did not resolve the entry-versus-renewal question.

## Metadata, costs, and remaining boundary

The immutable bundle SHA-256 remains
`ecbaad48333345838dd2bd983298f8a0127723b5eb35c104c7f87bd87f09c52e`.
All 201 staged vector metadata objects matched exact readback, including all
serialized source references, cycle fields, program/version links, review dates,
and inactive-candidate status. Raw hashes, exact admitted spans, offsets,
headings, table exceptions, and registered content exclusions passed validation.

The cumulative ledger after the final evaluation is **$2.07346354 of $5**. It
includes conservative charges for ambiguous provider operations; it was not
reset. New v3 document embeddings cost $0.00153482; v4 reused all 201 cached
vectors. Subsequent changes required no document re-embedding.

The corpus is not comprehensive. Deferred programs, unpublished future-cycle
rules, unknown GPA scales/types, and Cooke's source distinctions remain explicit.
Candidate publication and hosted auth/deployment checks are separate from this
local evidence. Retain the prior namespace and the same ledger when activating.

Raw receipts are under `artifacts/reports/`, including the two saved run IDs,
`candidate-api-preview.json`, `candidate-browser-preview.json`,
`candidate-browser-live-answer.json`, `candidate-final-live-api-answer.json`,
and `candidate-print-plan.pdf`.
