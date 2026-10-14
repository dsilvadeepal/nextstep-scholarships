> Historical planning note. The current agreed design is in [DESIGN_SPEC.md](DESIGN_SPEC.md), which supersedes conflicting scope and architecture proposals below.

# Next steps and project scope

Planning date: October 14, 2026. No implementation has started.

## Suggested first version

Start with 10–15 reviewed opportunities for Georgia students. Earlier discussion used 12–15 or 15–20 opportunities and 30–50 documents as illustrative targets; none is a validated count or a requirement. Choose the final count after source review. Prefer variety and complete evidence over volume.

Proposed core: student profile, discovery cards, sourced requirement explanations, missing-information prompts, shortlist, preparation checklist, official application links, cycle status, and source verification metadata. Include corporate/credit-union programs where rules are publicly available. Use fictional demo students.

Proposed additions: parent task ownership/export, comparison view, timeline, and a manual update-check demonstration. Separate parent accounts, submission automation, broad scheduled crawling, and comprehensive statewide coverage would expand the scope and should be evaluated later.

## Work sequence

1. Build the source register and validate a diverse seed collection. Confirm graduating-senior applicability and latest published cycles.
2. Decide whether national junior-year awards belong in the first version. Design junior preparation guidance even when an application is senior-only.
3. Define reviewed eligibility fields and handling of unknowns. Agree on the exact user-facing status labels.
4. Sketch the profile, results, scholarship detail/evidence, and preparation screens.
5. Choose a simple code stack and implement ingestion, metadata, retrieval, and cited answers.
6. Connect the reviewed eligibility checks and shortlist/checklist journey.
7. Demonstrate changed-document detection, review, replacement, and removal of superseded content from current answers.
8. Evaluate correctness and freshness cases, refine prompts/retrieval, and prepare submission assets.

## Open decisions

- Final product name and visual direction.
- Georgia-only programs versus Georgia audience plus selected national programs.
- Which counties and colleges receive initial coverage; describe collection gaps clearly.
- Final program list after verification.
- Minimum profile fields and optional financial/employment/membership details.
- Frontend, backend, vector storage, embedding model, LLM, and deployment.
- Whether parent support is task ownership/export or a separate login.
- Faithfulness target and latency ceiling; measure rather than invent results.
- Manual refresh only versus a limited scheduled check, and who approves changed rules.

## Proposed evaluation

Create around 20 project-specific questions/scenarios with reviewed expected answers and evidence. This is our proposal, not a universal handout requirement for every original project.

Cover junior versus senior, GPA calculation differences, county/school restrictions, employer and membership conditions, employee-family exclusions, college location, missing information, closed deadlines, unpublished future cycles, conflicting sources, unsupported winning-probability questions, and updated documents. Include fictional profiles with varied academics and circumstances.

Measure answer faithfulness, citation support, eligibility-rule correctness, cycle/date correctness, appropriate uncertainty, retrieval of required evidence, and response time. Include a controlled update case: change a document, replace its indexed content and dependent structured facts, then prove current answers no longer use the old rule. Any altered fixture must be labeled synthetic and kept distinct from actual sponsor documents.

## Week 2 handout alignment

Reference: Week 2 Project Handout ( Oct 2026 ).docx in the directory. Handout requirements are course reference material, distinct from user choices.

- Build a RAG flow: corpus selection, cleaning, chunking, embeddings/storage, retrieval, generation, and grounded/cited answers.
- Define the user, question types, corpus, interface, freshness approach, chunking/retrieval choices, faithfulness target, and latency ceiling.
- Original use cases are permitted. Code with LangChain or another suitable framework is compatible; a chatbot interface is an optional extension.
- Submit a Google Doc explaining what was built, including relevant datasets, prompts, iterations, and learning.
- Submit a video of five minutes or less showing the application live and explaining use of AI coding tools.
- Upload code/workflow project assets to GitHub and provide the link.
- Builder of the Week cutoff: Sunday, October 18, 2026, 11:59 p.m. Pacific, equivalent to Monday, October 19, 2:59 a.m. Eastern. Later submission is allowed for certification but not Builder of the Week.

The earlier review covered the handout and accessible linked solution guides and examples. Demo-video content was not successfully retrieved, and some repository links were unavailable; do not describe all examples as fully inspected. Examples are scaffolding and may contain shortcuts; use project-specific evidence and testing.
