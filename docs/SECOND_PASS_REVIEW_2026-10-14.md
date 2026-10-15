# Second-pass source review — October 14, 2026

Owner authorization: verify sources, ingest the admitted records, and test locally within the existing cumulative $5 OpenAI ceiling. No Docker. This review resumes the previously paused local ingestion; it does not authorize a public release or assert hosted acceptance.

## Method and actual coverage

Re-fetched all 65 distinct official URLs in the first audit: 63 parsed, two failed. Followed 16 additional official rules, FAQ, application, policy, and score-equivalency links: 15 parsed and one failed. Two alternate access attempts did not yield usable rules (UAB returned an error page; Clemson's guessed first-year path failed). A successful HTML parse alone was never treated as evidence of a valid scholarship page.

Original files, collection timestamps, SHA-256 hashes, full normalized sections, and link-following results are retained locally under `artifacts/research/second-pass/`. Nineteen documents contribute explicitly selected sections to the admitted corpus. Twenty public normalized snapshots are saved under `data/reviewed/`; one UA FAQ snapshot is retained as review context but contributes no vector chunks. All twenty were reparsed from hash-checked originals and reproduced exactly. No extraction model was needed: reviewed records were prepared with deterministic quote anchoring.

This is a bounded audit of the original leads and 28 university entry points across Georgia and AL/FL/NC/SC/TN. It is not an exhaustive inventory of every university, department, donor fund, or portal-only award in those states.

## Corrections found on the second pass

- Chick-fil-A Community Scholars' administrator [rules](https://scholarshipamerica.org/scholarship/cfacommunityscholars/) add **age 18 by July 15, 2027**, full-time study, service/leadership in the prior twelve months, program participation, and a past-recipient exclusion. Required documents include tax return pages and a complete transcript. At least one online recommendation is due within three business days after the application deadline. Deadline is **November 3, 2026, 3 p.m. Central**. The sponsor's [eligibility page](https://www.chick-fil-a.com/community-scholars/application-tips) additionally states demonstrated financial need. Both sources are retained; neither substitutes for the other.
- Georgia Tech [application review](https://stampsps.gatech.edu/apply/application-review) explicitly includes U.K. citizens, while its [FAQ](https://stampsps.gatech.edu/apply/frequently-asked-questions) says U.S. citizens/permanent residents are generally eligible, with rare international consideration. The FAQ also describes January/March interviews while the dated [2027 calendar](https://stampsps.gatech.edu/apply/calendar) gives February/April. **Deferred**, rather than making a single definitive rule from these conflicting pages.
- Chick-fil-A Team Member administrator FAQ says high-school students can apply if dual enrolled, while the principal criteria permit planned Fall 2027 enrollment. The FAQ's generic no-minimum-service statement also needs to be read alongside the $25,000 tier's one-year requirement, and the resource hub retains an obsolete cycle heading. **Deferred** from this corpus, including both tiers, pending a clear interpretation from the administrator. Do not import the hub as a generic employee award.
- Georgia's Own's application page now contains a closed **2026–27** cycle (May 31, 2026 deadline), newer than the old 2025 PDF. It remains historical for Fall 2027 entrants. The 2025 PDF is not treated as the newest rules.
- Park's [application page](https://park.ncsu.edu/apply/) confirms **two Park-specific recommendations**, both application paths by **11:59 p.m. ET November 1**, and a **3.80 unweighted, non-rounded GPA**. The public GPA rule does not state its numeric scale; the structured scale remains unknown. No nomination is required.
- Alabama's [2027 table](https://afford.ua.edu/scholarships/oos-international-freshman/) and official scores use **single test dates**, not superscores. December 4 is a **priority** date; later automatic-merit consideration can be funds-dependent. Seven named tiers are separate records, not one guaranteed award.
- Auburn's current [first-year page](https://www.auburn.edu/administration/finaid/apply/first-year-students.php) is more useful than its scholarship landing page. Its Fall 2027 nonresident table has three named awards, uses superscores, and expressly says competitive chart values are estimates, not guarantees. Its [score equivalency](https://www.auburn.edu/testscores) page is retained with the chart.
- Georgia Southern's Fall 2027 award uses **recalculated admissions core GPA**, is **one-time**, and is **not renewable**. A student's cumulative GPA cannot be substituted for that calculation.
- Coolidge's current junior cycle is for **Fall 2028**, with no gap-year/early-graduation exception; Coca-Cola's 2027 cycle is **closed**. Both distinctions remain in records and test references.

## Admission decisions: original non-university leads

| Lead | Decision | Reason / applicable year |
|---|---|---|
| HOPE public/private; Zell Miller | Deferred for Fall 2027 corpus | Official 2026–27 regulations retained for research; 2027–28 rules not located. Do not silently apply the earlier regulation year to a later award year. |
| Greater Atlanta Foundation funds | Deferred | Official listings still refer to closed 2026–27 awards; split funds and exclude current-college-only awards when next-cycle rules are posted. |
| Central Georgia Foundation | Deferred | Public page explains universal application; current named-award criteria require further portal-level evidence. No directory-only eligibility record. |
| Jones County list | Historical discovery only | Older PDF is a lead, not current award rules. |
| Amicalola | Deferred | 2026 application closed; recipient announcement excluded. |
| Delta Community HBCU | Admitted: senior route | Current 2026 nomination rules; Georgia residence, graduating-senior/HBCU acceptance path, 250-word nomination, October 31 at 6 p.m. ET. No inferred 2027–28 academic year. All biographies excluded. |
| Delta annual | Deferred | Closed 2026–27 cycle; next-cycle rules unknown. |
| Georgia's Own | Deferred | Closed 2026–27 application supersedes the 2025 lead; next cycle unknown. |
| CFA Team Member tiers | Deferred, conflicting | High-school eligibility, service wording, and cycle-heading inconsistencies need clarification. |
| CFA Community | Admitted | Explicit 2027–28 administrator and sponsor rules; preserve all additional restrictions above. |
| Coca-Cola | Admitted, closed | 2027 award for 2026–27 graduating seniors; closed September 30, 2026. Useful for preparation and closed-cycle tests, not an open opportunity. |
| Coolidge | Admitted | Current 2026–27 junior application cycle, first college enrollment Fall 2028. Exact application-portal essay prompts are not reproduced or invented. |

## University coverage and decisions

Admission here means named awards in the verified pilot, not every scholarship at that institution.

| State | University | Decision and remaining boundary |
|---|---|---|
| GA | UGA | Foundation Fellowship admitted. Current admissions/Honors/Fellowship sequence, recommendation reuse, November deadline and mandatory February 2027 interview verified. Georgia Commitment/Goizueta/general merit remain discovery; broad redirects and initiative directories do not establish complete named-award rules. |
| GA | Georgia Tech | Deferred for conflicting official citizenship/interview wording described above. |
| GA | Georgia State | Deferred. Fall 2027 admissions timeline exists, but general merit text still references Fall 2026 and Stamps/Presidential need award-level review; no generic GSU scholarship record. |
| GA | Georgia Southern | First-year merit admitted. Honors awards remain separate: named criteria and interview route cannot be borrowed from first-year automatic merit. |
| GA | Kennesaw State | Deferred. Fall 2027 timeline/ScholarshipUniverse date is verified discovery, not a named award with full rules. |
| GA | Emory | Deferred. Woodruff program and application route are public but the scholarship page lacks an explicit new-cycle year; no inferred current GPA threshold or award guarantee. |
| GA | Morehouse | Deferred. Automatic match process is public; donor-specific/current-entry-cycle rules not fully established. |
| GA | Spelman | Deferred. Public named scholarships exist, but current-cycle terms and award-specific conditions need confirmation. |
| GA | Clark Atlanta | Deferred. Public institutional merit policy exists, but no explicitly identified Fall 2027 award cycle was established. |
| GA | North Georgia | Deferred. BOLD has Fall 2027 first-year requirements and says application opens February 2027; mixed prior-year event schedule and no complete current application deadline. |
| GA | Mercer | CASE retained as early high-school discovery (2026–27 sophomores/juniors), outside the Fall 2027 freshman pilot. Admission-based freshman awards not established from CASE. |
| AL | Alabama | Seven named 2027 nonresident automatic-merit tiers admitted; competitive ASAM awards are separate and excluded from these records. |
| AL | Auburn | Three Fall 2027 nonresident competitive-merit awards admitted with official score equivalencies and no-guarantee wording. |
| AL | UAB | Deferred, access-limited. Main alias fetch failed; alternate official URL returned an error page. Search-index text alone is not ingested. |
| SC | Clemson | Deferred. Official recruiting and renewal rules are useful; current explicit Fall 2027 deadline/cycle not established. The counselor guide found by search is for earlier years. No South Carolina resident-only award is recommended to Georgia residents. |
| SC | South Carolina | Deferred. Nonresident directory/Top Scholars route public; dated award-level current-cycle rules not established. |
| SC | College of Charleston | Deferred. AcademicWorks lists a 2026–27 application cycle and mixed continuing-student awards; do not interpret individual 2027 dates as proof of 2027–28 freshman eligibility. |
| FL | Florida | Deferred. Named freshman/waiver policies public but no explicit current 2027 entry terms established by the inspected page. Florida-only aid excluded from Georgia matches. |
| FL | Florida State | Deferred. Public named awards/out-of-state waiver policy lacks explicit new-cycle confirmation in inspected material. |
| FL | UCF | Deferred. Pegasus/Provost discovery and prior-year costs are insufficient for current named nonresident award rules. Transfer application dates are unrelated. |
| FL | USF | Deferred. Page explicitly describes Summer/Fall 2026; no current 2027 terms established. |
| NC | NC State | Park admitted with exact current application/FAQ rules. PACK ASSIST/general awards are separate. North-Carolina-only Goodnight is outside the Georgia-resident scope. |
| NC | UNC | Morehead-Cain deferred. Nomination versus admissions-referral routes verified, but route-specific scholarship deadlines remain unpublished/portal-specific. October 15 is a UNC early-action route date, not a universal Morehead-Cain deadline. |
| NC | Duke | Deferred. General merit page says no separate Duke-administered application; named awards load dynamically and were not fully available in the collected source. |
| NC | Wake Forest | Deferred. 2027–28 need-aid instructions verified separately; generic November 15 merit consideration does not establish all named-award conditions. Some named awards explicitly reference 2026 or 2028 entry. |
| TN | UT Knoxville | Deferred, conflicting/previous-cycle. December 15/January 15/January 5 application wording and 2026–27 award table are unresolved. |
| TN | Vanderbilt | Ingram prospective-first-year route admitted, due December 1, 2026. February 28 enrolled-first-year route excluded from its deadline. Other signature awards require separate records. |
| TN | Memphis | Deferred. Mixed prior-year cost/rate and evergreen scholarship text; current award cycle not established. |

## Metadata contract

Canonical records and chunks retain the cycle description and separate `application_cycle`, `college_entry_year`, `award_academic_year`, `regulation_academic_year`, and `high_school_graduation_year`. Only source-supported values are populated. For example, Coolidge is application cycle 2026–27, college entry 2028 and graduation 2028; its award academic year is not inferred. CFA Community explicitly specifies award year 2027–28 but does not restrict all applicants to first-time college entry.

Each Pinecone vector stores `program_id`, `source_id`, `corpus_version`, `text`, `heading`, `section_ids`, `source_url`, `document_hash`, `fetched_at`, `source_title`, `quote_start`, `quote_end`, `evidence_ids`, `cycle`, `information_status`, `source_checked_at`, and any supported separate year fields. `page_number` is populated for PDF chunks; it is omitted for HTML. Unknown values are omitted from Pinecone, and remain null in the canonical typed record. The index contains public source evidence, not student profiles or credentials.

Pinecone retrieval is pinned to a version namespace and filters the same corpus version and requested program. The full exact quote, normalized-section location and evidence-to-field mapping remain in the SQL/JSON manifests. Review status means the source was checked; it does not mean a student meets all requirements. Unrepresented requirements and unspecified GPA scale/type remain explicit unknowns.

## Test and publication record

Candidate `verified-2026-10-14-v2`: 18 records across 10 award families, 174 chunks, 19 contributing official documents. `verified-2026-10-14-v1` was an unactivated staging checkpoint before the metadata schema was expanded; embeddings were reused from the cache for v2. Neither the original v6 nor the staged v1 should be used as a release corpus. The old namespaces remain available until the final verified version is activated and retention is reviewed.

Fresh live evaluation, metadata fetch verification, active pointer, application checks, and final ledger totals are recorded below after execution. Original prior-corpus eval files were archived under `artifacts/research/pre-second-pass-evals/`; old paid results and all ledger rows remain in the same SQLite database.

### Executed result

`verified-2026-10-14-v2` was activated locally after source, metadata, readiness and answer checks. The prior v6 namespace remains retained for rollback; no index or old namespace was deleted. Publication receipt: `artifacts/reports/verified-2026-10-14-v2-published.json`.

| Check | Result |
|---|---|
| Stored vector metadata | 174/174 exact matches to the canonical manifest; fetched back from Pinecone |
| Revised regression suite | 26/26 semantic and 26/26 hybrid; saved run `d7190260-2f19-4cc5-9926-6315e8dc43f2` |
| Fresh held-out factual questions | 5/5 for each method; source exclusions, citizenship alternative, prior university matriculation, early graduation, and state residency |
| Fresh held-out missing-program question | Correct Clemson coverage gap for both methods; old judge marked it unresponsive, so raw held-out grades are 5/6 per method in run `d4ae9518-f1a8-4035-823a-d0a508fed8a3` |
| Explicit-gap rubric correction | Saved-output rescore 6/6 per method; original expected questions/claims and raw scores retained. No paid replay and **no fresh held-out claim**. Receipt `artifacts/reports/heldout-gap-rescore.json` |
| Backend | 84 passed, two PostgreSQL checks skipped in default invocation; both passed separately on native PostgreSQL |
| Frontend | Seven unit tests, TypeScript and production build passed |
| Browser | 18 mocked regressions plus six real local phone/desktop/API/print checks passed |
| Budget | $0.72160134 cumulative after test calls, out of the original $5 ceiling; no ledger reset |

The initial eight-case held-out expansion exposed a real problem: a missing HOPE question could retrieve related Georgia Southern rules and return them as an answer. That attempt and its failure remain saved in run `4035701c-f15e-4a53-8a35-6a2495d7c187`. Those exposed cases were moved to regression use. The fix adds a version-pinned deferred-program coverage register, catalog scope in the selector prompt, and per-unit program IDs; unsupported named programs produce a gap rather than another award's rules. The coverage register hash and scoring version enter evaluation configuration fingerprints.

Two earlier tuning attempts encountered a Pinecone timeout and a provider/selection `ValueError`. They were persisted and explicitly retried after inspection; no blind automatic paid retries were enabled. The completed post-fix 26-case comparison required no such retry. These small fictional suites are evidence about tested behavior, not a statistical guarantee of scholarship-answer correctness or an independent human audit.

Real application checks also confirmed that an intended college does not establish an acceptance letter; unknown requirements remain unresolved even with a high self-reported GPA; a Florida resident fails the Georgia-only conditions; Coca-Cola stays closed; removed old-corpus program IDs return 422; browser-supplied corpus IDs cannot select old data; and anonymous admin requests return 401. Print testing caught duplicated long source quotes/blank first page; the plan now retains requirements and checklist with deduplicated source URLs, hashes and section anchors. One-award phone/desktop printouts fit one readable page and were visually inspected.

Local startup: `./.venv/bin/python scripts/start_reviewed_local.py`. This reads keys from the protected `.env` without rewriting it and applies explicit process-local database/pricing/budget settings. Hosted paid calls must remain disabled until the local/hosted ledger handoff prevents independent instances from each spending a separate $5 allowance.
