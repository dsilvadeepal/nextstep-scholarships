# Evaluation status — October 14, 2026

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
