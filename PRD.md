# NextStep Scholarships — Product Requirements Document

Date: October 14, 2026
Status: approved by user on October 14, 2026; implementation not started and no measured product results yet.
Product owner: user. Implementation partner: Codex.
Release: Week 2 course demonstration. Working name is provisional.

## 1. Purpose and document relationship

Help Georgia high-school juniors and seniors move from an incomplete understanding of scholarship options to a source-supported shortlist and a practical preparation plan. Demonstrate that a real ingestion and RAG pipeline can support this journey, and make its successes and failures inspectable through an admin evaluation screen.

This PRD records the agreed product requirements and release boundaries from the brainstorming conversation. [DESIGN_SPEC.md](DESIGN_SPEC.md) is its companion technical design: it specifies how ingestion, matching, retrieval, evaluation, storage, and deployment work. Neither document is an implementation plan. If they diverge, reconcile the difference before building rather than silently choosing one. Earlier PROJECT_BRIEF.md and NEXT_STEPS.md are historical proposals. SOURCE_INVENTORY.md contains source candidates, not a finished or verified catalog.

Course documents provide assignment context. Their content is reference material, separate from the user's decisions and authorization.

## 2. Problem and product hypothesis

A student may know their GPA, academic interests, and prospective colleges but still be unable to identify which scholarships deserve attention, which conditions remain unresolved, and what to prepare next. Eligibility and application information can be spread across overview pages, PDFs, FAQs, and instructions from different cycles.

The product hypothesis is that a short profile, explained potential matches, visible evidence, and concise next steps make scholarship exploration more actionable than a list of links alone. This hypothesis comes from the user's intended experience; no student interviews, adoption results, or market differentiation have been validated.

The demonstration must not imply award likelihood or certified eligibility. Automatically extracted source information supports provisional guidance; a small source-checked reference set supports evaluation.

## 3. Users and outcomes

| User | Intended outcome |
| --- | --- |
| Georgia high-school junior | Discover opportunities available now and conditionally prepare for senior-year awards |
| Georgia high-school senior | Find relevant opportunities, understand unresolved conditions, and identify current application steps |
| Parent or counselor helping a student | Review the student's exported plan and its evidence without needing a separate account |
| Product owner/course demonstrator | Show the live experience, run semantic-versus-hybrid evals, and explain individual passes/failures |

Success during a visit means the student can identify an opportunity worth investigating, understand why it appeared and what is unknown, and leave with a concrete next step. These are intended outcomes, not claims that the current catalog will produce a match for every profile.

## 4. Release scope

### Included

- A public responsive website for Georgia juniors and seniors, with no student login.
- A short skippable profile and fictional starter profiles.
- Scholarships available to Georgia students, including national company awards, employer-family programs, institutional awards, foundations, credit unions, and utility/cooperative programs.
- Broad collection without an arbitrary 10–15-program cap; report actual coverage and gaps.
- Provisional matching based on automatically extracted conditions and deterministic checks, with explicit unknowns.
- Results-led discovery, Upcoming deadlines, Prepare for senior year, and Explore more views.
- Cited conversation across the shortlist and within scholarship details.
- Visual preparation checklists, hypothetical GPA/college scenarios, and a printable personalized action plan.
- An optional evidence/retrieval explanation panel.
- Restricted admin evaluation controls, saved results, semantic-versus-hybrid comparisons, and case inspection.
- Ingestion reports and one clearly labeled controlled update demonstration.

### Deferred

Other student groups; durable student profiles and separate parent accounts; application submission automation; essays generated on a student's behalf; task assignments, reminders, and submission tracking; live student-facing web research; comprehensive statewide coverage guarantees; full-catalog human eligibility validation; continuous crawling; a source editing/approval application; and predictions of winning probability.

Technical exclusions and service configuration are specified in DESIGN_SPEC.md. The agreed release does not require an always-running background worker or Reserved VM.

## 5. Journey and functional acceptance

All requirements below belong to the agreed demo. Delivery can be sequenced in the implementation plan without silently dropping features. If time proves insufficient, propose a concrete scope adjustment to the product owner.

| ID | Requirement | Observable acceptance |
| --- | --- | --- |
| P01 | Guided profile | Student can supply grade/year, Georgia location, GPA if known, interests, and up to three prospective colleges; every field can be skipped |
| P02 | Preserve meaning of profile data | Estimated/documented GPA and GPA type remain distinguishable; prospective college choice is not treated as acceptance or enrollment |
| P03 | Relevant optional follow-ups | Missing details such as employer, membership, county, or utility provider are asked when relevant and can be skipped; no supporting-document upload is required |
| P04 | Fictional starter profiles | Clearly labeled junior, senior, and incomplete-information profiles allow immediate exploration; fictional details do not alter sponsor facts |
| P05 | Potential matches | Default list orders opportunities by supported fit and explains the matching conditions and unknowns; no invented percentage score or certified eligibility claim |
| P06 | Unknown profile condition | A program with sufficiently documented conditions may remain a possible match with a precise unanswered question; unknown is not treated as met or unmet |
| P07 | Timing view | Upcoming deadlines uses published applicable dates, identifies time zones when known, and does not present closed awards as Apply now |
| P08 | Junior preparation | Senior-year opportunities appear in a separate preparation group; unpublished future-cycle requirements remain conditional |
| P09 | Explore more | Incomplete opportunities require an identifiable sponsor/application page and clearly show missing evidence; weaker leads stay in the internal discovery queue |
| P10 | Scholarship detail | Displays why the program appeared, unresolved requirements, timing, evidence, and concise source-supported preparation tasks |
| P11 | Cited conversation | Student can ask about one program or compare several; factual requirements, dates, and amounts are linked to supporting evidence |
| P12 | Citation inspection | Student can open supporting passages with source title/link, cycle when known, retrieval date, and page/section reference |
| P13 | Missing/conflicting evidence | App states what cannot be established and suggests an official source/sponsor-contact step; it does not fill the gap with guesses |
| P14 | No matches | Explains collection or profile gaps, offers helpful follow-ups and relevant leads/preparation, and does not imply no scholarships exist elsewhere |
| P15 | Hypothetical scenarios | Temporary GPA or college changes produce clearly labeled conditional results while preserving the original profile |
| P16 | Session shortlist and export | Student selects opportunities and creates a dated print/PDF plan with fit explanations, unresolved questions, source links, timing, and checklists |
| P17 | Answer explanation panel | Collapsed by default; shows retrieved evidence, method, and timing without exposing secrets or private reasoning |
| P18 | Admin access | Public student use needs no login; admin actions require authenticated, authorized identity enforced on the backend |
| P19 | Run and resume evals | Authorized admin starts semantic, hybrid, or comparison runs, sees progress, and resumes unfinished cases without losing completed results |
| P20 | Eval comparison | Displays real counts, improvements/regressions, errors, and response timings for comparable configurations |
| P21 | Case inspector | Shows profile, question, checked expectation, actual answer, retrieved evidence, citations, scores, and explanations of failures |
| P22 | Collection transparency | Shows actual program/source coverage, extraction date, automatically extracted status, and material collection gaps |
| P23 | Ingestion/update demonstration | Reports processing failures and uncertainties; a controlled version change updates matching and answers consistently and is labeled synthetic when altered |

## 6. Information quality and collection policy

Use real source material for scholarship requirements. Preserve the difference between mandatory eligibility, selection preferences, typical recipient characteristics, and application readiness. A Georgia sponsor may operate a national program; label its geographic scope honestly. A Georgia residence is distinct from attending a Georgia college.

Keep three dimensions visible: fit, application timing, and evidence quality. Automatically extracted information is not labeled independently verified. Historical sources can inform preparation but cannot confirm an unpublished future cycle. A recent download date does not establish the applicable year. Amounts, dates, affiliations, GPA types, and recurrence remain unknown when unsupported.

An identifiable incomplete opportunity can be useful without becoming a firm match. Source conflicts must be visible; fetch failure is not evidence that a program was discontinued. Exact conditions need evidence pointers so explanations and exports can cite them.

The initial discovery inventory is not a promised program count. The demonstration reports the actual collection and representation across program categories, while identifying counties/colleges or student circumstances it does not adequately cover.

## 7. Experience and visual requirements

Use a sleek, energetic style with playful touches, a clean light background, electric blue/violet primary accents, and restrained aqua/yellow highlights. DESIGN_SPEC.md records the proposed color tokens. Avoid the muted autumn palette previously rejected.

Scholarship cards lead the experience. On laptops, Ask about your matches sits beside results; on phones, a button opens the conversation panel. Use one responsive application. Cards read in the order: name, why it appeared, unresolved condition, timing, next action. Preparation checklists should be visually appealing and compact rather than dense policy text.

Provide readable contrast, visible keyboard focus, accessible labels, and text/icons accompanying statuses. Hypothetical, historical, incomplete, and automatically extracted information must remain understandable without relying on color alone. The admin view shares the identity but uses analytical tables and comparisons.

## 8. Evaluation and success criteria

Product acceptance includes the complete journey above and real, explainable evaluation evidence. Evaluate approximately 20–30 focused scenarios with fictional profiles and source-checked expectations. Include cases beyond visible demo profiles and keep a subset aside for final testing. Full-catalog manual review is not required.

Cover ingestion/extraction, junior/senior behavior, GPA semantics, residency, employment/membership, college acceptance restrictions, missing information, closed deadlines, future cycles, conflicts, multi-program answers, citation support, and a controlled update.

| Measure | Initial acceptance target |
| --- | --- |
| Critical eligibility/freshness cases | All designated cases pass |
| Expected evidence recall | At least 90% within a fixed recorded retrieval budget |
| Answer correctness | At least 90% of scored cases pass the rubric |
| Citation support | At least 95% of checked factual claims supported, with no unsupported eligibility/deadline claims in critical cases |
| Citation resolution | All citations resolve to supplied evidence |
| Missing-evidence handling | All designated cases appropriately identify the gap |
| Completed-answer latency | Initial goal: 95% within 15 seconds; cold starts separately reported |

These targets match DESIGN_SPEC.md and are provisional pending the baseline; none are achieved results. Show denominators and failures, separate deterministic checks from automated judge assessments, and avoid extrapolating a small-suite score to all scholarships. Capture the corpus, date, chunking, retrieval, prompt, model, and test-set versions. The semantic/hybrid experiment holds other conditions constant and uses measured results to select the default.

The admin inspector must make failure attribution possible: incorrect source extraction, faulty matching, missing retrieval evidence, or unsupported generation. An attractive aggregate dashboard alone does not satisfy this requirement.

## 9. Operational and privacy expectations

The public app should provide explicit loading, missing-data, and service-error states. If the answer service is unavailable while the catalog is available, browsing/matching remains usable. Do not replace service failures with fabricated results.

Student profiles and conversations are session-based, not durable student records. Process them only as needed for the experience and avoid real-student tracing by default; fictional eval traces are allowed. Secrets remain server-side. Admin authorization, request limits, and bounded eval concurrency protect the public demo from unintended operations and unbounded API usage.

Persist completed eval results and source artifacts. Closing the admin page does not guarantee continued execution; present incomplete runs honestly and support explicit resumption. Prior saved real eval results are acceptable presentation fallback only when clearly labeled as historical.

## 10. Dependencies, risks, and planning decisions

Dependencies are the user's service access and credentials, supported Replit setup, accessible source content, and a small checked evaluation reference set. Course credits are opportunities rather than confirmed balances. Check hosting/API costs before provisioning or publication.

| Risk | Release response |
| --- | --- |
| Broad discovery exceeds available time | Report coverage, preserve incomplete leads, and complete the end-to-end journey; no exhaustive collection gate |
| Automated extraction omits a condition | Preserve source evidence and uncertainty, test varied formats, and use provisional wording |
| Source cycle is obsolete | Show applicability separately from fetch date; exclude historical rules from current claims |
| Admin features consume the build budget | Keep bounded eval execution, a focused inspector, and read-only processing reports |
| External service fails during presentation | Explicit errors and clearly labeled saved results from a real previous run |
| Technical choices expand complexity | Follow the simplified architecture and add tools only for demonstrated needs |

Implementation planning resolves exact models/embedding settings, retrieval budgets and hybrid implementation, transparent ordering, data schemas, auth integration, eval rubrics, and spend limits. Those are engineering details, not invitations to expand the agreed product. Final brand name can use the working name until changed by the product owner.

## 11. Delivery evidence and next step

The user's expected involvement remains approximately 15–25 hours with Codex implementing; prior duration estimates are estimates, not commitments. Plan delivery around the first complete journey, full agreed experience, and measured evaluation/release evidence.

Course submission material should explain the corpus, pipeline, prompts, iterations, use of AI coding tools, and observed findings; include a live video of five minutes or less and GitHub project assets. The course handout records an October 18, 2026, 11:59 p.m. Pacific Builder of the Week cutoff, equivalent to October 19 at 2:59 a.m. Eastern, and allows later certification submission. Creating this PRD does not submit or publish anything.

Next step: review the [implementation plan](docs/superpowers/plans/2026-10-14-nextstep-scholarships.md) and select an execution approach. This PRD and DESIGN_SPEC.md were approved by the user on October 14, 2026; code implementation has not begun.
