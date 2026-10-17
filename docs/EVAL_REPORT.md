# Evaluation status

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

## October 16: expanded candidate

The staged v4 candidate passed its 21 exposed source cases and 26 known regression
cases using equal-weight hybrid retrieval. The complete saved-run results,
reference corrections, source spot-check limits, and provider failures are in
the [October 16 build/test report](EXPANDED_BUILD_TEST_REPORT_2026-10-16.md).
Cumulative spend is **$2.07346354 of $5**, including ambiguous-call liabilities.
The candidate is inactive. These are tuning results, not fresh held-out accuracy.

## Historical October 14 evaluation

The reviewed local corpus is `verified-2026-10-14-v2`: 18 award records across 10 families, 174 chunks, and 19 contributing official documents. Metadata readback matched 174/174 Pinecone vectors. The cumulative OpenAI ledger is **$0.81145530 of the approved $5 cap** after the tuning-only 60/40 experiment; it was not reset. Semantic remained the student-app default at this checkpoint. The owner later selected the existing equal-weight hybrid method for the demo.

| Tuning method | Saved run | Passed / total | Completed answers | Checked claim support | Expected-evidence recall | Completed-answer p95 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Semantic | `d7190260-2f19-4cc5-9926-6315e8dc43f2` | 26/26 | 26/26 | 32/32 | 25/25 | 2.30 s |
| Hybrid equal RRF weights | same baseline run | 26/26 | 26/26 | 34/34 | 25/25 | 2.09 s |
| Hybrid 60% semantic / 40% keyword | `e9154c90-d94e-4598-9c07-23d182dd295c` | 25/26 | 25/26 | 33/33 among completed | 24/24 among completed | 2.71 s among completed |

The 60/40 method uses actual `0.6/(60 + dense_rank) + 0.4/(60 + keyword_rank)` scoring, with the same corpus, 20+20 candidates, eight final passages, and 5,000-token ceiling. Its numeric weights are frozen in the saved run configuration and validated before execution. Case `verified-05` failed three times, including two explicit retries, because the answer model selected an evidence-unit ID absent from the supplied units. The citation gate rejected that answer and saved the error. All other 25 weighted cases passed. This is a regression against the historical 26/26 semantic and equal-hybrid tuning runs, so **do not switch the default to 60/40**. The weighted run added **$0.08985396** to the cumulative ledger. Its completion failure makes its release gate fail even though the observed support and recall among completed answers are 100%.

These are tuning runs on the same cases and corpus, but the baseline was saved earlier rather than rerun concurrently. The p95 figures are not a paired speed comparison. The automated judge is correlated with the answer model; the claim-support figures are not an independent scholarship accuracy audit. No held-out cases were invoked for the 60/40 experiment.

The earlier six-case held-out run `d4ae9518-f1a8-4035-823a-d0a508fed8a3` remains **raw 5/6 per method**. It produced five factual answers and a correct Clemson evidence gap; the then-current grader expected unavailable rules and marked that gap wrong. A unit-tested explicit-gap rubric rescored those **saved outputs** 6/6 per method without a new paid run. The preceding exposed HOPE wrong-program answer is retained as a failure in run `4035701c-f15e-4a53-8a35-6a2495d7c187`, then moved to regression after the versioned coverage guard fixed it. Neither rescore nor exposed regression is fresh held-out evidence.

The implementation suite now passes 85 backend tests with two default native-PostgreSQL skips; those two integration checks passed separately. Seven frontend units, TypeScript/build, 18 mocked browser checks, and six real local phone/desktop/API/print checks passed. These checks support the local pilot, not exhaustive 2027–28 award eligibility.

Targets remain: all critical and missing-evidence cases pass, expected-evidence recall at least 90%, answer case pass at least 90%, checked claim support at least 95%, citation resolution 100%, and at least 95% of cases completed within 15 seconds. Errors and incomplete answers count as failures. The 60/40 variant does not meet the all-critical/completion/citation release gate. Final independent source spot-checks and a public student smoke test remain before release. No Docker was used.

Five later local demo questions with equal-weight hybrid retrieval added $0.01187412, bringing the shared ledger to **$0.82332942 of $5**. See `docs/DEMO_RUN_RESULTS_2026-10-15.md` for per-query costs and observed answer limits.


## October 15: grounded answers and targeted retrieval

The local default is now phase 1 + phase 2: cited explanations with a bounded support review, source-bound ACT comparisons, and targeted selection of existing passages after 50/50 hybrid search. The same five exposed demo cases were compared against phase 1 alone; the combined approach recovers the missing Auburn Heritage threshold. See [the complete comparison](RAG_COMPARISON_2026-10-15.md) for exact outputs, costs, source links, rollback checkpoints and wording limitations. These results supersede the earlier fragment-based demo outputs, but are not a held-out accuracy claim. Hosted transfer of this new revision remains separate.
