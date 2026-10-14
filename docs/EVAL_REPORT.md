# Evaluation status — October 14, 2026

No real-corpus evaluation has run. No semantic/hybrid quality, citation-support, cost or latency result is available. Unit tests exercise deterministic local behavior using synthetic fixtures and test doubles; they are not the 24-case source-checked reference suite.

Implemented local checks cover profile unknowns, rule grouping, stale retrieval exclusion, per-program evidence allocation, evidence offsets, chunk limits, publication failure/rollback, serialized spend reservations and evaluation leases. See `BUILD_STATUS.md` for actual verification counts and remaining work.

Semantic remains the proposed default until the controlled comparison exists. No thresholds have been changed. Heldout cases have not been created or consumed. The controlled sponsor-rule update demonstration has not run.
