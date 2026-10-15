# Evaluation status — October 14, 2026

**No real-corpus model comparison has run.** There are no measured semantic/hybrid accuracy, live citation-support, model cost or live latency results. Semantic remains the default; no thresholds were changed.

Prepared: 24 fictional cases (18 tuning, 6 held out), 15 original-checked evidence excerpts across six source documents, frozen October 14 date, critical flags and unknown/GPA/residence/acceptance/membership/exclusion/historical/missing-answer/adversarial/comparison cases. Expected-source references are used only for scoring; they do not prefilter retrieval. Explicit user shortlist inputs default empty. The suite must be bound and checked against the first extracted corpus before interpreting its metrics. A missing expected condition/evidence unit fails visibly.

Executed: local deterministic matching, extraction provenance, retrieval budgets, citation/support gates, publication failure/cache/rollback, evaluation leases/retries/cancellation, database persistence, security boundaries, and responsive student/admin browser checks. These are implementation tests, not the 24-case quality evaluation.

The separate synthetic update test changed an invented GPA threshold from 3.0 to 3.5 and deadline from November 1 to October 1, 2026. Matching and cited output moved together after publication; failed publication preserved the old version; rollback restored it. No real sponsor rule or model behavior is inferred from this fixture.

## Live protocol ready to execute

1. Configure approved credentials, prices and numerical budget caps. Collect/extract/inspect and publish a ready corpus.
2. Freeze suite/program bindings and config. Run 18 tuning cases with both semantic and hybrid methods, alternating order. Inspect all critical failures and a sample of passes against original sources.
3. Make bounded fixes, documenting changed prompts/config. Open six heldout cases once after tuning. Reusing exposed holdouts requires a new suite for any generalization claim.
4. Record completed-answer p95, completion rate, cases/errors/denominators, evidence recall, supported/checked/unscorable claims, citation resolution, paired regressions and usage. Judge assessment is correlated automation, not independent truth. Optional LangSmith traces contain only fixed fictional evals and cannot prevent local result persistence.
5. Require all critical/missing-evidence cases, recall >=90%, answer pass >=90%, support >=95%, citation resolution 100%, and >=95% of cases completed within 15 seconds. Incomplete cases/errors are failures; no factual claims is N/A for support. Report cold starts separately.
6. Prefer hybrid only when measured evidence improves without critical regressions or unacceptable latency. Otherwise retain semantic.

Live result table remains intentionally empty until provider execution is authorized. See `BUILD_STATUS.md` for actual implementation-test counts.
