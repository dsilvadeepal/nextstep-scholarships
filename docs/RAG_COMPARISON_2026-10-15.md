# Answer construction versus answer construction plus targeted retrieval

Decision: use **phase 1 + phase 2** locally. It retains 50/50 keyword/vector fusion and recovers the named Auburn Heritage threshold that baseline selection omitted. No source re-chunking, corpus re-embedding, Pinecone writes or Docker were used.

These are five exposed fictional regression cases, evaluated after development iterations. Both final runs used the same construction code, profile inputs, date, corpus and cached dense rankings; phase 2 changed final passage selection using existing local chunks. The model remains nondeterministic. This is a small diagnostic comparison, not a held-out accuracy claim.

## What changed

- Full retrieved passages and student context replace sentence/line-fragment selection.
- Strict structured output returns per-award claims and source IDs. Original support passages are attached by code, avoiding fabricated quote text.
- Deterministic checks enforce source/program identity, reject mixed-award claims and affirmative guarantees, and calculate below-tier ACT comparisons from clearly named tables.
- One additional model call reviews support/completeness. It can still make correlated mistakes; exact citations and review approval are not truth guarantees. No automatic model retry.
- Phase 2 reserves existing passages for requested facets (threshold, score policy, eligibility, deadline, materials, application, award type), then fills from 50/50 RRF. Eight passages/5,000 tokens remain the limit; unscoped searches keep baseline ranking.
- HOPE coverage gaps now include official GSFC/GAfutures handoff links without asserting future-cycle rules.

## Remaining limits

Requested-answer coverage improved from four of five cases to five of five in the final inspected pair. This is a coverage count, not five perfectly worded or independently validated answers. The combined Alabama/Auburn answer still says a superscore “could be used to meet the score rule” before qualifying that 27 is below the threshold; the leading code-generated comparison is unambiguous. Some answers repeat requirements and gaps. Structured matching still intentionally leaves GPA scale/recalculation and application facts unresolved.

A stress test also produced “27 or higher” for Capstone, broadening the exact tier despite prompt instructions and model review. Treat exact tier wording as a remaining quality limit; use the linked table. The stress checks prevented a senior gap-year exception, fabricated banking details, and an instruction to guarantee awards; they do not establish comprehensive adversarial robustness.

## Recovery and validation

Original state: `c4fddf4`, tag `checkpoint/pre-rag-answer-2026-10-15`. Branch: `feat/rag-answer-comparison`. Keep the current branch and switch to a new branch/worktree from the checkpoint to inspect the old app; do not use a destructive reset. Secrets remain ignored. Baseline retrieval remains selectable using `retrieval_policy: "baseline"`.

Full run inputs, outputs, retrieved passages, citations, review decisions are tracked in `evals/results/2026-10-15-answer-comparison.json`. Intermediate attempts, including failures, remain under ignored `artifacts/reports/rag-*`.

The final absence-of-information filter converts unsupported-topic statements into gaps instead of citing unrelated passages; it was added after the saved comparison and does not change any of the five demo answers.

Validation complete: **99 backend tests passed, 2 PostgreSQL-dependent tests skipped; 8 frontend tests passed; 18 Playwright phone/desktop tests passed; frontend build, Ruff, and Git whitespace checks passed.** Chromium required execution outside the process sandbox; no product test failed after the browser could launch. The local server was restarted on port 8014; a live HTTP smoke check confirmed targeted selection and official HOPE links. The .env fingerprint matches the pre-change checkpoint.

The final local default is phase 1 + phase 2; this revision has not been deployed to Replit.

## Measured comparison

| Case | Finding |
|---|---|
| Georgia Southern | Renewability, core GPA caveat, February 1 priority date covered in both. |
| Park | Non-rounded 3.80, separate applications and November 1 timing covered in both. |
| Coolidge | Correct junior/Fall 2028 cohort, deadline/timezone, two letters and remaining requirements covered in both. |
| Alabama versus Auburn | Phase 1 misses Heritage ACT31–32 and broadens the exact Capstone tier to 27 or higher. Phase 2 supplies the decisive below-threshold conclusion and automatic versus competitive distinction, with awkward superscore wording. |
| 2027–28 HOPE gap | Both abstain on unconfirmed 2027–28 rules and provide official links. |

Mean latency including the HOPE guard: 3.55s versus 3.47s. These timings exclude uncached dense retrieval for this matched comparison.

## Exact final outputs

### 1. Georgia Southern

**Question:** For a Georgia resident entering Georgia Southern in Fall 2027, is the first-year merit scholarship renewable? Is my 3.60 transcript GPA enough to know the award tier, and when should I complete the admission application?

**Phase 1 — 3.755 seconds**

- The Georgia Southern First-Year Merit Scholarship for Fall 2027 is a one-time award for the first academic year and is not renewable for subsequent years.
- Your 3.60 transcript GPA alone is not sufficient to determine the award tier because the scholarship uses a recalculated admissions core GPA, which may differ from your cumulative transcript GPA.
- To be considered for the Georgia Southern First-Year Merit Scholarship for Fall 2027, you should submit a completed admission application by the priority deadline of February 1, 2027.

**Remaining checks / gaps:**

- georgia-southern-merit: Confirm first-time full-time Fall 2027 enrollment and the university's recalculated admissions core GPA. The minimum tier is 3.50; cumulative transcript GPA is not equivalent.
- georgia-southern-merit: Confirm Georgia in-state tuition status and a complete admission application by the February 1, 2027 priority date.

**Source pages:** [Official page](https://www.georgiasouthern.edu/admissions-aid/tuition-and-scholarships/types-of-aid/scholarships)

**Phase 1 + 2 — 4.053 seconds**

- The Georgia Southern First-Year Merit Scholarship for Fall 2027 is a one-time award and is not renewable for subsequent years. This means the scholarship will only apply to the first academic year and does not continue beyond that.
- Your 3.60 transcript GPA alone is not sufficient to determine the scholarship award tier because the scholarship eligibility and tier are based on a recalculated admissions core GPA, which may differ from your cumulative transcript GPA. The minimum tier for the scholarship is a recalculated core GPA of 3.50.
- To be considered for the Georgia Southern First-Year Merit Scholarship for Fall 2027, you should submit a completed admission application by the priority deadline of February 1, 2027. No separate scholarship application is needed, as all eligible applicants are automatically evaluated.

**Remaining checks / gaps:**

- georgia-southern-merit: Confirm first-time full-time Fall 2027 enrollment and the university's recalculated admissions core GPA. The minimum tier is 3.50; cumulative transcript GPA is not equivalent.
- georgia-southern-merit: Confirm Georgia in-state tuition status and a complete admission application by the February 1, 2027 priority date.

**Source pages:** [Official page](https://www.georgiasouthern.edu/admissions-aid/tuition-and-scholarships/types-of-aid/scholarships)

### 2. Park

**Question:** Park lists a 3.80 unweighted minimum. Can my 3.79 be rounded up? Do I need separate NC State and Park applications, and when are the applications and recommendations due?

**Phase 1 — 3.958 seconds**

- Your 3.79 unweighted GPA does not meet the Park Scholarship's minimum 3.80 unweighted GPA requirement because the rule specifies a non-rounded minimum of 3.80, so rounding up is not allowed.
- You must submit separate applications for NC State undergraduate admission and the Park Scholarships program, as the application processes are separate.
- Both the NC State admission application and the Park Scholarships application, including two recommendations, are due by 11:59 pm ET on November 1.

**Remaining checks / gaps:**

- park: Park requires at least 3.80 unweighted, without rounding. Confirm the GPA scale with Park; the public rule does not state a scale.
- park: Confirm U.S. citizen/permanent resident OR graduation from a U.S.-located high school regardless of citizenship; apply for fall first-year baccalaureate admission; transfers excluded.
- park: Confirm availability for the published semifinalist/finalist interviews; alternate dates cannot be arranged.

**Source pages:** [Official page](https://park.ncsu.edu/apply/) · [Official page](https://park.ncsu.edu/faq/)

**Phase 1 + 2 — 3.826 seconds**

- Your 3.79 unweighted GPA does not meet the Park Scholarship's minimum requirement of 3.80 unweighted without rounding, so it cannot be rounded up to qualify.
- You must submit separate applications for NC State undergraduate admission and the Park Scholarships program, as these are distinct processes.
- Both the NC State admission application and the Park Scholarships application, including two recommendations, must be submitted by 11:59 pm ET on November 1.

**Remaining checks / gaps:**

- park: Park requires at least 3.80 unweighted, without rounding. Confirm the GPA scale with Park; the public rule does not state a scale.
- park: Confirm U.S. citizen/permanent resident OR graduation from a U.S.-located high school regardless of citizenship; apply for fall first-year baccalaureate admission; transfers excluded.
- park: Confirm availability for the published semifinalist/finalist interviews; alternate dates cannot be arranged.

**Source pages:** [Official page](https://park.ncsu.edu/apply/) · [Official page](https://park.ncsu.edu/faq/)

### 3. Coolidge

**Question:** I am a junior graduating in spring 2028. Is this the Coolidge cycle for me? What is the deadline for the application and two reference letters, and what should I check before applying?

**Phase 1 — 5.548 seconds**

- You are in the correct Coolidge Scholarship cycle if you are a high school junior graduating in spring 2028 and plan to start college full-time in fall 2028, which matches the 2026-27 application cycle for first college enrollment in fall 2028.
- The deadline for submitting the Coolidge Scholarship application and the two letters of reference is December 1, 2026, at 5:00 PM Pacific Time.
- Before applying, you should confirm that you are a U.S. citizen or legal permanent resident by the scholarship deadline, intend to enroll full-time at an accredited U.S. college or university for the first time in fall 2028, and ensure you have no excluded immediate family relationships with the Coolidge Foundation or Fund.
- You should also ensure your application is complete, including submitting two letters of reference from individuals who can speak to your academic abilities and character, but not from family members or peers, and that all materials are submitted by the deadline since no updates are accepted after the deadline.

**Remaining checks / gaps:**

- coolidge: Confirm U.S. citizenship or legal permanent residence by deadline; first full-time accredited U.S. undergraduate enrollment in Fall 2028; and no excluded immediate family relationship. Gap-year and early-graduation exceptions are not allowed.

**Source pages:** [Official page](https://coolidgescholars.org/about/faq/) · [Official page](https://coolidgescholars.org/eligibility/) · [Official page](https://coolidgescholars.org/selection-timeline/)

**Phase 1 + 2 — 4.068 seconds**

- The 2026–27 Coolidge Scholarship application cycle is the correct cycle for a student graduating high school in spring 2028 and planning to enroll full-time in college in fall 2028, which matches your junior year and graduation timeline.
- The deadline for submitting the Coolidge Scholarship application and the two required letters of reference is December 1, 2026, at 5:00 PM Pacific Time.
- Before applying, you should confirm that you are a U.S. citizen or legal permanent resident by the application deadline, plan to enroll full-time at an accredited U.S. undergraduate institution for the first time in fall 2028, and ensure you have no excluded immediate family relationships with the Coolidge Foundation.

**Remaining checks / gaps:**

- coolidge: Confirm U.S. citizenship or legal permanent residence by deadline; first full-time accredited U.S. undergraduate enrollment in Fall 2028; and no excluded immediate family relationship. Gap-year and early-graduation exceptions are not allowed.

**Source pages:** [Official page](https://coolidgescholars.org/about/faq/) · [Official page](https://coolidgescholars.org/eligibility/) · [Official page](https://coolidgescholars.org/selection-timeline/)

### 4. Alabama versus Auburn

**Question:** My ACT superscore is 27, but neither single test date was 27. Could that satisfy Alabama's Capstone score rule? Does Auburn handle scores the same way, and are these awards guaranteed?

**Phase 1 — 4.5 seconds**

- University of Alabama Capstone is an automatic merit award, subject to all published eligibility and application requirements. This does not confirm an award for you.
- The University of Alabama Capstone scholarship requires an official ACT composite score from a single test date of 27 or higher; superscores are not accepted for this scholarship. Therefore, an ACT superscore of 27 does not satisfy the Capstone score rule if no single test date score is 27. The award is automatic for qualifying students meeting all eligibility and application requirements.
- Auburn University accepts ACT superscores for admissions and scholarship consideration, including the Academic Heritage Scholarship, which uses the best testing result from superscores. However, the Academic Heritage Scholarship is competitive and not guaranteed; awards depend on the applicant pool, GPA, and other factors.

**Remaining checks / gaps:**

- Is the student's GPA calculation by Auburn consistent with their self-reported GPA?
- Has the student completed the application and submitted official test scores by Auburn's deadlines?
- Is the student enrolling as a first-time freshman in Summer/Fall 2027 at either university?
- auburn-heritage: Confirm the exact nonresident GPA/test tier in the source table; these are competitive consideration ranges, not guaranteed awards.
- auburn-heritage: Confirm summer/fall enrollment immediately after high-school graduation, completed admission file by December 1, and official test reports. Updated scores for reconsideration are due January 11.
- auburn-heritage: Auburn may recalculate nonstandard GPA scales. Confirm its GPA calculation rather than substituting self-reported cumulative GPA.
- ua-capstone: Confirm UA-qualified GPA 3.50+ and ACT 27 OR SAT 1260–1290 for Capstone ($8,000/year). The public GPA weighting is not specified; do not compare an arbitrary transcript GPA.
- ua-capstone: Official testing-agency single-date ACT composite or SAT total required; UA does not use superscores for scholarships.
- ua-capstone: Confirm first-time nonresident/international Summer/Fall 2027 status and the completed application plus official scores by December 4, 2026; later consideration is funds-dependent.

**Source pages:** [Official page](https://afford.ua.edu/scholarships/oos-international-freshman/) · [Official page](https://www.auburn.edu/administration/finaid/apply/first-year-students.php) · [Official page](https://www.auburn.edu/admissions/testscores.php)

**Phase 1 + 2 — 5.416 seconds**

- Your stated ACT score of 27 is below the listed ACT 31–32 tier for Auburn Academic Heritage Scholarship. This comparison addresses the score threshold only.
- University of Alabama Capstone is an automatic merit award, subject to all published eligibility and application requirements. This does not confirm an award for you.
- University of Alabama Capstone requires a single test date ACT composite score of 27, not a superscore, to meet the score rule. Your superscore of 27 does not satisfy this because UA does not use superscores for scholarships.
- Auburn Academic Heritage Scholarship accepts ACT superscores for admissions and scholarship consideration, so your superscore of 27 could be used to meet the score rule. However, the minimum ACT required for the $11,000 tier is 31–32, so a 27 superscore does not meet the minimum score threshold for this award.
- University of Alabama Capstone is an automatic merit award based on meeting published GPA and test score requirements and does not require a separate scholarship application, but this does not guarantee an award.
- Auburn Academic Heritage Scholarship is a competitive merit award requiring a completed admission file by December 1 and official test reports, with reconsideration possible by January 11. It is not guaranteed and depends on the applicant pool and available funding.

**Remaining checks / gaps:**

- Confirm if your GPA meets the specific GPA calculation method used by Auburn for nonresidents.
- Confirm your planned enrollment term and completion of application materials by the stated deadlines for both universities.
- auburn-heritage: Confirm the exact nonresident GPA/test tier in the source table; these are competitive consideration ranges, not guaranteed awards.
- auburn-heritage: Confirm summer/fall enrollment immediately after high-school graduation, completed admission file by December 1, and official test reports. Updated scores for reconsideration are due January 11.
- auburn-heritage: Auburn may recalculate nonstandard GPA scales. Confirm its GPA calculation rather than substituting self-reported cumulative GPA.
- ua-capstone: Confirm UA-qualified GPA 3.50+ and ACT 27 OR SAT 1260–1290 for Capstone ($8,000/year). The public GPA weighting is not specified; do not compare an arbitrary transcript GPA.
- ua-capstone: Official testing-agency single-date ACT composite or SAT total required; UA does not use superscores for scholarships.
- ua-capstone: Confirm first-time nonresident/international Summer/Fall 2027 status and the completed application plus official scores by December 4, 2026; later consideration is funds-dependent.

**Source pages:** [Official page](https://afford.ua.edu/scholarships/oos-international-freshman/) · [Official page](https://www.auburn.edu/administration/finaid/apply/first-year-students.php) · [Official page](https://www.auburn.edu/admissions/testscores.php)

### 5. 2027–28 HOPE gap

**Question:** What are the confirmed 2027–28 HOPE Scholarship rules for a student entering college in Fall 2027? Can you confirm my required GPA and application deadline?

**Phase 1 — 0.001 seconds**

No answer blocks.

**Remaining checks / gaps:**

- HOPE Scholarship is not in this verified corpus. Confirmed 2027–28 state regulations were not located; the retained 2026–27 regulations cannot establish later-year rules.

**Source pages:** [Official page](https://gafutures.org/hope-state-aid-programs/hope-zell-miller-scholarships/hope-scholarship/application-and-deadline/) · [Official page](https://gsfc.georgia.gov/programs-and-regulations)

**Phase 1 + 2 — 0.001 seconds**

No answer blocks.

**Remaining checks / gaps:**

- HOPE Scholarship is not in this verified corpus. Confirmed 2027–28 state regulations were not located; the retained 2026–27 regulations cannot establish later-year rules.

**Source pages:** [Official page](https://gafutures.org/hope-state-aid-programs/hope-zell-miller-scholarships/hope-scholarship/application-and-deadline/) · [Official page](https://gsfc.georgia.gov/programs-and-regulations)
