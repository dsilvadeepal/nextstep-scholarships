> Historical planning note. The current agreed design is in [DESIGN_SPEC.md](DESIGN_SPEC.md), which supersedes conflicting scope and architecture proposals below.

# Project brief and conversation summary

Recorded October 14, 2026. This is a planning record, not a claim of implementation or current eligibility advice.

## How we arrived here

The original request was for five creative, meaningful RAG use cases outside customer support, informed by the Week 2 handout and linked examples. The user wanted an understandable, visually appealing, rounded product and was comfortable using AI coding agents to implement it. Discussion moved toward students, parents, college preparation, and scholarship eligibility.

The user selected a scholarship app for 11th and 12th graders. The initial geography expanded to Georgia and its neighbors (Alabama, Florida, North Carolina, South Carolina, Tennessee), then narrowed toward Georgia. Official state, foundation, university, corporate, and credit-union sources indicate sufficient variety for a curated Georgia project. We have not completed a current-cycle inventory proving a specific total.

The primary user is the student, with a parent able to help. The two priorities are finding suitable opportunities and next actions, and helping juniors prepare for senior-year opportunities. Build time is approximately 15–25 hours.

## Product promise

Help a Georgia student move from “I do not know what I qualify for” to a sourced shortlist and an actionable preparation plan.

The app assesses published requirements against information supplied by the student. It does not predict winning probability or replace a sponsor's final eligibility determination.

## Proposed user journey

| Stage | Student action | Product response |
|---|---|---|
| Profile | Enter grade, graduation year, home state/county, school, GPA and GPA type, interests, and possible colleges. Allow unknown answers. | Establish a starting profile; ask only relevant follow-up questions. |
| Discover | Explore opportunities. | Show Apply now, Prepare for later, and Need more information views, with a clear collection boundary. |
| Understand fit | Open a scholarship or ask why it appeared. | Explain each reviewed requirement and display supporting source passages. |
| Resolve uncertainty | Supply missing details, such as GPA type or employer affiliation. | Update the assessment while preserving unresolved conditions. |
| Shortlist | Save and compare opportunities. | Compare deadlines, required materials, college restrictions, and award terms. |
| Prepare | Work through application tasks. | Provide a timeline for transcripts, recommendations, essays, and forms; allow student/parent task ownership. |
| Apply | Follow the official sponsor link. | Track progress and allow self-reported submission status. |
| Revisit | Update grades, scores, plans, or graduation details. | Reassess opportunities and explain relevant changes. |

Juniors need both any programs accepting juniors now and preparation for senior-year programs. Seniors need current application windows and missing-material checklists. A first parent experience can be a downloadable checklist; separate accounts are optional later work.

## What could make it stand out

1. Explain every eligibility conclusion rather than displaying an unsupported percentage match.
2. Convert published conditions into concrete preparation actions.
3. Surface county, school, employment, and membership connections where relevant.
4. Keep eligibility, application window, and application readiness as separate statuses.
5. Show evidence beside the answer, including document version, cycle, and page or section.
6. Use an appealing dashboard with cards, a junior-to-senior timeline, comparisons, and a next-three-actions panel. Chat can sit inside scholarship details.

Scholarship matching already exists elsewhere. These are proposed differentiators, not claims of market novelty.

## Eligibility and data principles

- Use statuses such as published requirements appear met, explicit condition unmet, missing information, or sponsor clarification required.
- Do not turn “typical recipient” characteristics into mandatory rules.
- Distinguish weighted, unweighted, and program-specific GPA calculations.
- Distinguish residence from intended college location. Georgia residence does not make a student eligible for another state's resident aid.
- Track graduation year, application cycle, and award/college-entry year separately where available.
- Label national programs honestly if added; a Georgia company can operate a national award.
- Corporate affiliation can qualify or exclude a student. Ask relevant questions without assuming employment guarantees eligibility.
- Use fictional profiles for demos. Avoid requiring sensitive financial-document uploads in the first version.

## Proposed RAG approach

Use structured, reviewed fields for explicit eligibility checks and catalog filtering. Use RAG to explain rules, exceptions, required materials, and source evidence for the relevant scholarship and cycle.

Collect official overview pages, eligibility policies, FAQs, application instructions, and relevant PDFs. Preserve source IDs, cycle, headings, and PDF page numbers. Do not conclude that every requirement is met from a few retrieved chunks; the reviewed rule set must cover the mandatory conditions.

AI may draft extracted fields and evaluation questions, but important eligibility rules need source review. Amounts and deadlines must not be invented. LangChain is a candidate for orchestration; frontend, storage, embedding model, and hosting remain undecided.

## Freshness is a core product requirement

RAG can cite obsolete material accurately. It does not independently establish freshness.

Two problems need handling: our saved copy may be older than the sponsor's current page, or the sponsor's page itself may still describe an old cycle. A recent fetch timestamp only establishes when we checked; it does not establish which year the content applies to.

A production workflow would maintain a source register, periodically fetch official pages/PDFs, compare content hashes, review meaningful policy changes, replace affected indexed chunks, retire superseded versions from current retrieval, and re-evaluate dependent rules. Keep previous versions for audit and explicitly historical questions. Mark sources unavailable or needing review when checks fail; do not infer withdrawal from a temporary fetch error.

Show open, closed, next cycle unpublished, and needs verification states. If a future cycle is unpublished, prior rules can inform clearly labeled preparation guidance but cannot be presented as confirmed future eligibility. Any deadline or amount displayed outside chat must be updated too. Source conflicts need review rather than a silent guess.

For the demo: a dated collection, cycle metadata, a manual Check for updates action, a review flag, and one controlled before/after update test are the proposed scope. Scheduled crawling and monitoring can follow later. Changes cannot be detected before a sponsor publishes them, so absolute freshness cannot be guaranteed.

The user considered switching to a more stable domain. Alternatives discussed were a historical-primary-source research assistant or an application preparation assistant using a fixed, user-supplied cycle. The current recommendation is to keep the curated scholarship planner; the concern remains a design requirement rather than a reason to abandon the idea.
