# Reviewable release packet

Local feature branch: `feat/nextstep-native`. Main is unchanged. No merge, push, deployment, recording or course submission performed.

Ready locally: responsive student profile/results/details/scenarios/shortlist/print, cited chat component and bounded API, default-deny admin with saved run inspector/driver, source collector/parsers/extraction/provenance/partition/reconciliation, rate guards, versioned publication/rollback, 24 fictional reference cases, synthetic controlled update, production build and one-port scripts.

Evidence: `BUILD_STATUS.md`, `SOURCE_INSPECTION.md`, `EVAL_REPORT.md`, `DATA_DICTIONARY.md`, `ENVIRONMENT.md`, automated tests, synthetic screenshots/PDFs under `/tmp/nextstep-*`. Synthetic browser answers are explicitly test responses, not live model output. The public preview intentionally reports unavailable catalog until a real corpus is published.

Required before approval request:

- Configure development PostgreSQL, App Storage, owner OIDC and OpenAI with provider credentials. Pinecone setup exists separately; verify adapter end-to-end with the first real vectors.
- Run real extraction, inspect flagged source partitions/cycles/conditions and incomplete leads, then publish only a query-ready namespace. Preserve original artifacts and prior ready version.
- Execute tuning and heldout comparison, inspect failures, record cold/warm latency and threshold outcomes. Label correlated judge limitations.
- Verify hosted anonymous denial and genuine owner login, API failure fallback, profile privacy, source citations and a real printable plan.
- Confirm Replit Autoscale machine/maximum-instance settings and included allowance; obtain explicit publication approval. Do not assume credentials authorize publication.
- After approval, publish, verify the public URL and rollback, synchronize actual outcomes to the submission draft, and record/approve a <=5 minute video. Course submission remains the owner's action unless explicitly delegated.

Rollback: `uv run python -m nextstep.ingest.cli rollback --version PREVIOUS_READY_VERSION` with the intended database selected. No garbage collection or deletion of prior namespaces is part of this release.
