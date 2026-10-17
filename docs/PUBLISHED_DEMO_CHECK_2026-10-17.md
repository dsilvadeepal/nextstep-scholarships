# Published demo verification — October 17, 2026

**Ready to record the two rehearsed journeys** at https://nextstep-scholarships.replit.app/.

Release source merged through PR #1 into main (`1d404568d37513ea2279669993a103116cb4025d`). Replit published successfully after build, bundle and promotion. This report records real browser use against the public production URL, not the development preview or mocked answers.

## Senior: Auburn and Burger King

Entered Senior, Georgia resident Yes, final GPA 3.7, graduation 2027, 4-point unweighted; pasted the Auburn engineering note from the recording script and confirmed the extracted profile.

- 11 matches and 7 Explore opportunities; college choices constrain college results.
- Saved Burger King General Track and Auburn Academic Charter from Explore; conversation showed two saved programs.
- Submitted the exact comparison question from the script. The answer cited Burger King's 2.0 threshold and conditional full-time enrollment; it distinguished competitive selection from requirements. Auburn's GPA recalculation and unknown scores remained unresolved; no award guarantee.
- Sources (2) opened the official Scholarship America and Auburn URLs, including the Charter threshold table and GPA recalculation footnote.
- Submitted the exact SAT/ACT follow-up. The answer stayed on Auburn, explained official-score timing and superscores, and explicitly distinguished missing scores in this app from whether scores were submitted to the university.
- Follow-up Sources (2) contained only Auburn's merit policy and test-score policy.

## Junior: Georgia Tech and Kennesaw State

Entered Junior, Georgia resident Yes, estimated GPA 3.5 and the exact engineering/Science Olympiad/no-volunteering note. Confirmed both college choices, US citizenship, residency, volunteer status and activities.

- 2 matches and 15 Explore opportunities. Georgia Tech showed 2 reviewed requirements matched and did not ask again for citizenship.
- Kennesaw State remained a confirmed preference; the corpus has no Kennesaw-specific award.
- Submitted the exact future-cycle planning question. The response distinguished the published October 15, 2026 deadline from the student's future application cycle, suggested preparation and flagged unknown future dates.
- Sources (4) opened Application Review, Scholarship Calendar, Program Pillars and Application Process/Selection of Major, with source quotations and official links.

## Technical checks and limits

- Local backend: 142 passed, 2 skipped. Frontend: 14 passed. TypeScript/Vite build and Git whitespace checks passed.
- Production `/api/health`: HTTP 200. Production `/api/admin/runs`: HTTP 401.
- Both source popups opened and were inspected. This verifies the stored evidence presentation; source websites were not freshly recrawled during this check.
- Answers can vary between runs, including source counts and the length of clarification lists. The generated gaps can be repetitive. These are bounded demo checks, not a benchmark of every scholarship or an eligibility certification.
- No application code fixes were needed during the published journeys. A browser automation label lookup was corrected to use the rendered control roles before entering the first profile; it was not an app failure.
- Local Python's certificate store failed an auxiliary HTTPS request; curl with normal certificate verification successfully checked the production endpoints. Browser access also succeeded.

Record using [the conversational script](DEMO_VIDEO_SCRIPT.md): **senior first, junior second, then a short technical explanation**. The public app requires no student account. The GitHub repository remains private; confirm instructor access separately.
