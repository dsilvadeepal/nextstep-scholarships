# Operational scholarship content admission

> Historical evidence: dated checkpoints below are not current setup instructions. The published release is summarized in [build status](BUILD_STATUS.md). Local artifact paths are evidence references, not files distributed with this repository.


Only official operational scholarship content counts toward source and chunk
targets: program descriptions, eligibility/exclusions, cycle status/deadlines,
award amounts/renewal, materials, application steps, selection criteria, FAQs,
policies/terms, and contact or manual-verification guidance.

Exclude candidate/recipient profiles, winner biographies, testimonials, alumni
stories, recipient-centered press releases, and promotional narrative. A mixed
page is admissible only for its operational passages. Preserve the raw snapshot
for provenance, but do not embed excluded passages or count them as useful corpus
coverage. Mentions of alumni conducting interviews or past-recipient exclusions
are operational rules and are not biographies.

Before admitting each document, review every selected section, record excluded
sections or exact spans, and preserve original source offsets and hashes. Run
`scripts/validate_content_exclusions.py CANDIDATE.json` before embedding. This
registered-span check supplements manual review; new source hashes and new
documents require fresh review and exclusion registration.

## Existing corpus audit, October 16, 2026

The active `verified-2026-10-14-v2` corpus has no embedded winner biographies
identified in this audit. Delta's scholar biographies, Coca-Cola's newest-class
section, and Park's graduate-outcome section were already outside its selection
manifest.

Four existing chunks nevertheless overlap four newly registered promotional or
background spans across three documents: Coca-Cola's semifinalist-list promotion,
Coolidge FAQ history/organization background and recipient-class promotion, and
an illustrative Jonas Salk biography within Coolidge selection criteria. Exact
exclusions are in `data/content-exclusions-2026-10-16.json`. Retain the actual
closed-cycle statement and scholarship selection requirements when splitting.

Removal status: these four chunks are flagged for replacement; no active vectors
have been removed, and no cleaned replacement has yet been embedded or activated.
Keep the old namespace for rollback. A candidate cannot pass this admission gate
while its evidence overlaps the registered spans.
