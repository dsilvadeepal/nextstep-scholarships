# Recording readiness — October 17, 2026

**Ready for the two tested local course-demo journeys at http://127.0.0.1:8014/.** This is bounded demo validation, not a claim that every scholarship or generated answer is correct. Replit deployment was not changed or tested here.

## Fixes

- Junior answers distinguish published Fall 2027 dates from unknown future-cycle dates; a code-level boundary also withholds unqualified personalized dated timelines.
- Query-time source scoping separates Burger King General Track eligibility and selection excerpts from employee and WHOPPER award criteria. Original index and source references remain intact; no re-embedding or ingestion spending.
- Focused follow-ups about Auburn narrow a saved multi-award comparison to Auburn, rather than repeating Burger King.
- Guardrails withhold claims that an unweighted GPA meets a recalculated threshold, invented full-time enrollment, incomplete sentences, and an exact ACT tier expanded to “or higher.”
- Missing scores in the app are explicitly distinguished from scores submitted to a university.
- Sources pills count unique URLs, while the popup retains all cited passages from each URL, including Auburn's threshold table and GPA footnote.
- GPA follow-up notices use readable text instead of Python dictionary formatting.

## Final observed journeys

### Junior

Inputs: Junior; Georgia resident Yes; estimated GPA 3.5. Exact note:

> I am interested in engineering; I want Georgia Tech and maybe Kennesaw State. I do not have any volunteer experience.But I am part of the Science Olympiad School. I am a Georgia resident and a United States citizen.

Confirmed extraction: both colleges, engineering, US citizen, Georgia resident, no volunteer experience, Science Olympiad. Results: 2 matches and 15 Explore options. Georgia Tech does not request citizenship again. Kennesaw remains a preference; the corpus has no Kennesaw-specific award. Explore expands successfully.

Georgia Tech question:

> I’m a junior. Based on the sources, what can I prepare now, and which dates or requirements need checking for my future application cycle? Do not assume the current deadline applies to me.

Final response: prepare essays/extracurricular descriptions and program pillars; apply in senior year; October 15, 2026 is labeled as the Fall 2027 cycle, with the future deadline and interview dates needing verification. Citizenship and Georgia residency are acknowledged, without claiming full eligibility. Sources (3) opens Application Review, Scholarship Calendar, and Program Pillars, including all cited sections. Official URLs and relevant text inspected in the popup.

Screenshot: [junior final](../artifacts/demo-validation/junior-final.jpg).

### Senior

Inputs: Senior; Georgia resident Yes; GPA 3.7 Final/school record; graduation 2027; 4-point, unweighted. Note:

> I am interested in engineering and considering Auburn. I am a Georgia resident and a United States citizen.

Confirmed profile; 11 matches and 7 Explore options. Saved Burger King General Track and Auburn Academic Charter from Explore; plan count 2.

Question:

> Compare my two saved scholarships. With a final 3.7 unweighted GPA on a 4-point scale, what requirements can you confirm, what information is still missing, and what should I prepare for each? Separate eligibility from the chance of winning.

Final response: Burger King uses the correct 2.0/4.0 General Track threshold; enrollment remains conditional; transcript, financial information, deadline and competitive selection are described. Auburn requires GPA recalculation and unknown test scores; admission file and score deadlines are described. No guarantee of winning. Sources (2) includes Scholarship America's General Track eligibility and Auburn's Charter table (3.5; ACT 29–30) and recalculation footnote.

Follow-up:

> I haven’t provided SAT or ACT scores. How does that affect what you can conclude about Auburn?

Final response stays on Auburn, describes official test-score requirements and superscore policy, and explicitly states that scores not supplied here do not establish whether scores were submitted to the university. Sources (2) opens Auburn's first-year merit policy and test-score policy, with table and footnote passages available. No unrelated Burger King answer or citations.

Screenshots: [comparison](../artifacts/demo-validation/senior-comparison.jpg), [follow-up](../artifacts/demo-validation/auburn-followup.jpg).

## Verification and limitations

- Backend: 138 passed, 2 skipped.
- Frontend: 14 passed; TypeScript/Vite production build passed.
- Browser regression suite: 20 passed across phone and desktop, including synthetic print/PDF checks. The first attempts could not launch the browser until the documented browser path and macOS execution permissions were used; these were environment failures.
- Ruff and git diff --check passed for the changed scope.
- Live answers were tested in the browser with real providers. Intermediate iterations exposed residual overclaims; fixes and regression checks preceded further live calls. One initial junior request included the auto-filled introductory question; the exact question was subsequently tested, including a final clean journey.
- Native OS printing of the real selected plan is not certified by the synthetic print tests. No physical print was issued.
- Citations were inspected in the app; external websites were not freshly recrawled. Wording can vary across model runs. Missing facts and sponsor verification notices are intentional.
- Snapshot facts are corpus-specific. These tests do not add Kennesaw awards or validate a production eligibility decision.

## Cumulative budget

Authoritative ledger: artifacts/nextstep-live.db; no replacement ledger.

Before fixes: completed $2.07732158 + ambiguous $0.03584024 = $2.11316182.
After testing: completed $2.11392522 + ambiguous $0.03584024 = **$2.14976546**.
Increment: **$0.03660364**. Remaining under $5: **$2.85023454**. No pending reservation at final check.
