# Week 2 — Georgia Scholarship Planner

Status: Credential-free implementation and local verification completed on `feat/nextstep-native`; live extraction, hosted integrations, measured model evaluation and release await access and approved spend. No Docker is required. See [build status](docs/BUILD_STATUS.md) and [setup handoff](docs/ENVIRONMENT.md).

Working name: **NextStep Scholarships**.

Repository: [dsilvadeepal/nextstep-scholarships](https://github.com/dsilvadeepal/nextstep-scholarships) (private).

## Start here

- [Implementation plan](docs/superpowers/plans/2026-10-14-nextstep-scholarships.md): 12 sequenced tasks, independent work, credentials, spend gates, tests and review checkpoints.

- [Submission draft](docs/SUBMISSION_DRAFT.md): populated RAG framework, planned prompts and placeholders for actual build/evaluation evidence. [Native Google Doc](https://docs.google.com/document/d/1Nn_ZbfUnSVDwCozP7RpaeimTY08WvDCH0MwjedAYRts/edit).
- [Product requirements](PRD.md): audience, outcomes, release scope, functional acceptance criteria, and demonstration requirements.
- [Design specification](DESIGN_SPEC.md): current consolidated product, ingestion, RAG, evaluation, and deployment design. This supersedes conflicting earlier proposals.
- [Source inventory](SOURCE_INVENTORY.md): discovery candidates; program details and cycles require checking during ingestion.
- [Earlier project brief](PROJECT_BRIEF.md): historical brainstorming context.
- [Earlier next steps](NEXT_STEPS.md): historical scope proposals and course requirements.
- [Week 2 handout](Week%202%20Project%20Handout%20%28%20Oct%202026%20%29.docx): course reference material.

## Agreed demo direction

Help Georgia high-school juniors and seniors find potential college scholarships, including national company awards, understand source-supported conditions, and prepare next steps. Broad discovery includes identifiable incomplete leads; there is no fixed 10–15-program cap.

Use automated extraction and deterministic checks with explicit unknowns, standard cited RAG, and semantic-versus-hybrid retrieval evaluation. The catalog is not independently verified in full; a small evaluation reference set is checked against sources.

Build a responsive React + FastAPI app using LangChain, OpenAI, Pinecone, Replit PostgreSQL and App Storage, and LangSmith. Use manual ingestion and Replit Autoscale when ready to publish; no Reserved VM or always-running worker. Students need no account; admin controls are restricted.

Run instructions and connection gates: [environment](docs/ENVIRONMENT.md). Main remains untouched pending tests, review and the owner's merge decision.
