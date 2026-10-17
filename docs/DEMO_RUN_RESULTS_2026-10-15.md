# Five live 50/50 hybrid demo runs — October 14, 2026 (reported October 15)

These are five separate local `/api/chat` requests using the fictional homepage inputs in `docs/DEMO_TEST_SCENARIOS.md`, the exact saved questions, reviewed corpus `verified-2026-10-14-v2`, and equal-weight hybrid retrieval (`method: hybrid`). Each request had empty chat history. The blocks below reproduce the app's source-excerpt answer text in returned order; gaps are the app's separate unresolved-requirement messages. No extra question was asked. All five returned a server response. A successful server response means the request completed; it does not certify the answer's quality. Costs are before/after differences in the shared OpenAI ledger, not estimates. The full API responses are retained in ignored `artifacts/reports/demo-five-50-50-2026-10-14.json`.

| Case | OpenAI cost for this query | Input tokens | Output tokens | Response |
| --- | ---: | ---: | ---: | --- |
| Georgia Southern | $0.00156330 | 2938 | 242 | returned; 11 cited blocks; 2 gaps |
| Park | $0.00297960 | 6811 | 159 | returned; 10 cited blocks; 3 gaps |
| Coolidge | $0.00540200 | 12627 | 219 | returned; 11 cited blocks; 1 gap |
| Alabama versus Auburn | $0.00192922 | 4469 | 88 | returned; 5 cited blocks; 6 gaps |
| 2027–28 HOPE gap | $0.00000000 | 0 | 0 | returned; 0 cited blocks; 1 gap |

**Five-query total:** $0.01187412. Shared ledger: $0.81145530 before → $0.82332942 after (of the original $5 cap). The HOPE coverage guard used no OpenAI tokens. Later user questions will add cost.

## 1. Georgia Southern

**Question:** For a Georgia resident entering Georgia Southern in Fall 2027, is the first-year merit scholarship renewable? Is my 3.60 transcript GPA enough to know the award tier, and when should I complete the admission application?

**Cost:** $0.00156330. **Server status:** 200 (request completed; answer quality assessed below).

**Returned answer blocks (exact text):**

- One-time award
- for your first academic year
- (non-renewable)
- applying for Fall 2027 are automatically evaluated for merit scholarships when they submit their completed admission application by February 1st, 2027.
- February 1st, 2027
- recalculated core GPA
- This calculated GPA focuses on core academic coursework and may differ from the cumulative GPA on your high school transcript.
- First-year merit awards are
- one-time grants distributed across your first academic year
- and are not renewable for subsequent years.
- 3.50 – 3.79 | $500

**Returned gaps (exact text):**

- georgia-southern-merit: Confirm first-time full-time Fall 2027 enrollment and the university's recalculated admissions core GPA. The minimum tier is 3.50; cumulative transcript GPA is not equivalent.
- georgia-southern-merit: Confirm Georgia in-state tuition status and a complete admission application by the February 1, 2027 priority date.

**Cited official pages:**

- [Merit-Based Aid](https://www.georgiasouthern.edu/admissions-aid/tuition-and-scholarships/types-of-aid/scholarships)

**What this run shows:** The answer returned cited source fragments for one-time/non-renewable, recalculated core GPA, and February 1, 2027. It also showed a 3.50–3.79 tier excerpt, while the gaps correctly withheld a tier decision from the self-entered transcript GPA.

## 2. Park

**Question:** Park lists a 3.80 unweighted minimum. Can my 3.79 be rounded up? Do I need separate NC State and Park applications, and when are the applications and recommendations due?

**Cost:** $0.00297960. **Server status:** 200 (request completed; answer quality assessed below).

**Returned answer blocks (exact text):**

- Have a minimum unweighted GPA of 3.80 (non-rounded).
- The application processes for Park Scholarships and NC State undergraduate admissions are separate, so be sure to follow the instructions below.
- By 11:59 pm ET, November 1:
- Apply for
- undergraduate admission
- to NC State.
- Complete the
- Park Scholarships application
- Two recommendations
- Recommendations are due by 11:59pm, November 1.

**Returned gaps (exact text):**

- park: Park requires at least 3.80 unweighted, without rounding. Confirm the GPA scale with Park; the public rule does not state a scale.
- park: Confirm U.S. citizen/permanent resident OR graduation from a U.S.-located high school regardless of citizenship; apply for fall first-year baccalaureate admission; transfers excluded.
- park: Confirm availability for the published semifinalist/finalist interviews; alternate dates cannot be arranged.

**Cited official pages:**

- [Document](https://park.ncsu.edu/apply/)
- [What are the eligibility requirements to apply for the Park Scholarship?](https://park.ncsu.edu/faq/)

**What this run shows:** The answer returned the non-rounded 3.80 rule, separate NC State/Park applications, November 1 timing, and two recommendations. The structured fit remains unknown because the public rule does not specify a numeric GPA scale; no eligibility was promised.

## 3. Coolidge

**Question:** I am a junior graduating in spring 2028. Is this the Coolidge cycle for me? What is the deadline for the application and two reference letters, and what should I check before applying?

**Cost:** $0.00540200. **Server status:** 200 (request completed; answer quality assessed below).

**Returned answer blocks (exact text):**

- No, only high school juniors graduating in the spring of 2028 and starting college in the fall of 2028 are eligible to apply for the 2026-27 scholarship.
- December 1, 2026 at 5:00 PM Pacific Time
- : All application materials, including letters of reference must be submitted by the deadline.
- When thinking through who to ask to write your letters, please consider who is best positioned to speak to how you fit the
- Your letters, taken together, should speak to your academic abilities and accomplishments as well as the scholarship’s secondary criteria: humility, service, interest in policy, and appreciation of Coolidge values.
- The best recommendation letters come from individuals who know you well and can describe your achievements and character in detail with specific examples.
- Please note that your letters may NOT be from a member of your family or one of your peers (i.e.
- someone close to your own age).
- Each letter should only come from one individual (i.e.
- co-written letters or letters written or signed by multiple recommenders are not permitted).
- Please speak with your letter writers to gain their permission before you list them in your application.

**Returned gaps (exact text):**

- coolidge: Confirm U.S. citizenship or legal permanent residence by deadline; first full-time accredited U.S. undergraduate enrollment in Fall 2028; and no excluded immediate family relationship. Gap-year and early-graduation exceptions are not allowed.

**Cited official pages:**

- [Document](https://coolidgescholars.org/about/faq/)
- [Document](https://coolidgescholars.org/eligibility/)
- [Document](https://coolidgescholars.org/selection-timeline/)

**What this run shows:** The answer included the Fall 2028 junior cycle and December 1, 2026 at 5 p.m. Pacific deadline, but its leading source fragment begins "No, only high school juniors..."—confusing for this junior's question. It also did not explicitly state the requested count of two reference letters. Do not use this case in the recording without correcting and retesting the behavior.

## 4. Alabama versus Auburn

**Question:** My ACT superscore is 27, but neither single test date was 27. Could that satisfy Alabama's Capstone score rule? Does Auburn handle scores the same way, and are these awards guaranteed?

**Cost:** $0.00192922. **Server status:** 200 (request completed; answer quality assessed below).

**Returned answer blocks (exact text):**

- UA does not use superscores for scholarship purposes.
- Starting fall 2024, Auburn University will accept the ACT Superscore Report.
- Auburn will calculate a superscore for the SAT and any individual score reports from ACT.
- Automatic merit scholarships are awarded based on standardized test scores and GPA.
- This chart is a guide and is not a guarantee of future awards.

**Returned gaps (exact text):**

- auburn-heritage: Confirm the exact nonresident GPA/test tier in the source table; these are competitive consideration ranges, not guaranteed awards.
- auburn-heritage: Confirm summer/fall enrollment immediately after high-school graduation, completed admission file by December 1, and official test reports. Updated scores for reconsideration are due January 11.
- auburn-heritage: Auburn may recalculate nonstandard GPA scales. Confirm its GPA calculation rather than substituting self-reported cumulative GPA.
- ua-capstone: Confirm UA-qualified GPA 3.50+ and ACT 27 OR SAT 1260–1290 for Capstone ($8,000/year). The public GPA weighting is not specified; do not compare an arbitrary transcript GPA.
- ua-capstone: Official testing-agency single-date ACT composite or SAT total required; UA does not use superscores for scholarships.
- ua-capstone: Confirm first-time nonresident/international Summer/Fall 2027 status and the completed application plus official scores by December 4, 2026; later consideration is funds-dependent.

**Cited official pages:**

- [Test Scores](https://afford.ua.edu/scholarships/oos-international-freshman/)
- [Competitive Merit Charts for Fall 2027 Enrollment](https://www.auburn.edu/administration/finaid/apply/first-year-students.php)
- [ACT and SAT Score Equivalencies](https://www.auburn.edu/admissions/testscores.php)

**What this run shows:** The answer cited UA's no-superscore rule, Auburn's superscore acceptance, UA's automatic merit basis, and Auburn's no-guarantee warning. It did not give a complete direct yes/no comparison or confirm an award for the chat-only ACT score. Treat this as a partial answer, not a clean demo.

## 5. 2027–28 HOPE gap

**Question:** What are the confirmed 2027–28 HOPE Scholarship rules for a student entering college in Fall 2027? Can you confirm my required GPA and application deadline?

**Cost:** $0.00000000. **Server status:** 200 (request completed; answer quality assessed below).

**Returned answer blocks (exact text):**

- None.

**Returned gaps (exact text):**

- HOPE Scholarship is not in this verified corpus. Confirmed 2027–28 state regulations were not located; the retained 2026–27 regulations cannot establish later-year rules.

**Cited official pages:**

- None; this is a coverage gap, not a cited source answer.

**What this run shows:** The versioned coverage guard returned the correct missing-rule statement without a model call or cost. It did not include a direct GSFC/GAfutures link, so the planned source handoff is incomplete.

The app returns selected verbatim evidence fragments rather than a newly written prose paragraph. This is why some responses read as lists or sentence pieces. Citations attach to the returned blocks; the unanswered checks live in the separate gaps list. These are observed local results, not a guarantee that a later hosted run will select identical blocks.
