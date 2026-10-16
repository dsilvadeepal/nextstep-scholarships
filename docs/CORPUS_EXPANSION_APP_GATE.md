# App and evaluation gate for a candidate corpus

This is a handoff checklist for the next scholarship corpus version. Source research,
extraction, chunking, embedding, and staging belong to the ingestion workstream.
This document does not authorize activation or paid evaluation.

## Candidate contract

- Supply one immutable candidate `version`, its normalized award records, chunk
  manifest, contributing source list, and staged Pinecone readiness receipt.
  Every record and chunk must carry that version; every chunk's `program_id`
  must name a record in the same version. Keep the old version and spending
  ledger intact.
- Supply a reviewed source-and-section admission ledger keyed by `source_id`
  and section ID. Only scholarship rules, eligibility, application steps,
  deadlines, materials, award terms, renewal conditions, and necessary policy
  context may be admitted. Exclude candidate or recipient profiles, winner
  biographies, testimonials, alumni stories, and recipient-centered press
  releases, even when an official sponsor publishes them. A mixed official
  page needs section-level decisions so its rule text can be kept while its
  promotional sections are excluded. Each candidate chunk and each record's
  factual evidence must map to admitted sections. The existing chunk schema
  carries `source_id` and `section_ids`; it does not carry a content-class label,
  so the handoff ledger is necessary for a reliable audit.
- Supply the candidate coverage decision for named programs that remain out of
  scope, including their official handoff links. The current guard in
  `rag/answer.py` reads `data/reviewed-coverage-2026-10-14.json` only when its
  `corpus_version` matches. Without a candidate coverage file and app update,
  deferred-program questions would enter retrieval and might cite a different
  program's rules.
- Identify retained, renamed, removed, and added award IDs. The app rejects
  selected IDs absent from the active version, and the student interface
  refreshes its shortlist when a new version is returned. Renames may affect
  saved evaluation case IDs even when a source is otherwise unchanged.
- Supply source-checked fictional cases for added or materially changed
  programs. Existing evaluation files contain checked source hashes, section
  IDs, quotes, program IDs, and cycle-specific expected answers; a candidate
  run cannot assume they remain valid. The snapshot in `evals/suite.py` also
  hashes the old coverage file, so its metadata must be updated with the
  candidate register before a new-version run.

## App verification after handoff

1. Validate candidate records and chunks against `models.py`, check unique IDs
   and version/program links, inspect cycle and evidence metadata, and compare
   the vector readiness receipt with the manifest. Reject any chunk or record
   evidence whose source/section is absent from the admitted rule ledger.
   Audit carried-forward material too, not only new sources. Do this without
   changing `active_corpus`.
2. Update the version-aware deferred coverage guard and evaluation snapshot.
   Verify an absent named program returns an evidence gap without a model call;
   verify a newly covered program is no longer deferred.
3. Run backend, frontend, and phone/desktop browser regressions against the
   candidate fixture. Check a Georgia-first case, a neighboring-state case,
   an existing-program deeper-document case, and a cross-award citation case.
   Keep unknown residency, GPA scale/type, cohort, acceptance, and deadlines
   explicit.
4. Inspect matched retrieval on the unchanged 50/50 dense/BM25 default and
   targeted passage selection. The final eight-passage/5,000-token cap remains;
   assess whether relevant rule passages survive it as the corpus grows. Flag
   **any** retrieved candidate profile, winner biography, testimonial, alumni
   story, or recipient-centered release as a corpus failure, even if the final
   answer does not cite it. Require zero such failures before activation.
   Review source meaning and section boundaries; a keyword such as “recipient”
   can also occur in a legitimate eligibility or renewal rule.
5. Run only an approved, budgeted evaluation against frozen cases and the same
   candidate version. Record exact answer text, evidence IDs, failed claims,
   cost, latency, and limitations. Do not reuse exposed development cases as a
   fresh held-out accuracy claim. Reconcile the shared cumulative ledger before
   any hosted paid call.
6. Activate only after the source and answer-quality checks pass and the
   expected old version matches. Keep the previous ready version for a
   compare-and-swap rollback; never restore an old spending ledger.

No re-chunking or re-embedding is proposed for existing material by this app
gate. The ingestion owner decides the new corpus contents and provides the
candidate manifest; the app work begins from that frozen handoff.
