# Live demo rehearsal — October 16, 2026

Follow-up: fixes and final rerun results are recorded in [October 17 recording readiness](DEMO_REHEARSAL_2026-10-17.md). The failures below are retained as the original test record.

Local browser: http://127.0.0.1:8014/. Corpus: candidate-2026-10-16-v4, 39 programs. Three live chat questions executed. This is observed browser evidence, not a simulated test. No application code changed during this rehearsal.

**Verdict: do not record the chat demonstration yet.** Controls work, but two material grounding failures remain.

## Junior: Georgia Tech and Kennesaw State

Inputs: junior, Georgia resident, estimated GPA 3.5. Note: “I am interested in engineering; I want Georgia Tech and maybe Kennesaw State. I do not have any volunteer experience.But I am part of the Science Olympiad School. I am a Georgia resident and a United States citizen.”

Confirmed extracted citizenship, residency, both colleges, engineering, no volunteer experience, and Science Olympiad. Results showed 2 matches and 15 Explore options. Georgia Tech did not ask to reconfirm citizenship. Kennesaw was retained as a preference; no Kennesaw-specific award exists in this collection. Explore expanded successfully.

Question: “I’m a junior. Based on the sources, what can I prepare now, and which dates or requirements need checking for my future application cycle? Do not assume the current deadline applies to me.”

FAIL: answer told the junior to prepare for Fall 2027 entry and apply by October 15, 2026, despite the request to distinguish future cycles. It also listed January/February/April 2027 milestones without establishing that this is the student's cycle. Preparation advice was present, but cycle applicability was wrong.

Sources (4) opened and closed correctly. Official URLs and passages were visible for Georgia Tech Application Review, Scholarship Calendar, Program Pillars, and Application Process. Calendar passage explicitly concerned Fall 2027. Citation presence did not prevent misuse of the cycle.

## Senior: Auburn and Burger King

Inputs: senior, Georgia resident, final GPA 3.7, graduation 2027, 4-point unweighted GPA. Note: “I am interested in engineering and considering Auburn. I am a Georgia resident and a United States citizen.” Confirmed extracted profile. Saved Burger King General Track and Auburn Academic Charter; saved count was 2.

Controls passed:
- All types: 11 matches and 7 Explore options.
- College scholarships: 0 matches and 3 Explore options (Auburn Charter, Heritage, Presidential).
- Company scholarships: 5 matches and 2 Explore options.
- Upcoming deadlines: 9 matches and 7 Explore options; closed awards removed, dates ordered within each group.
- Explore resets to collapsed when filters change.

Question: “Compare my two saved scholarships. With a final 3.7 unweighted GPA on a 4-point scale, what requirements can you confirm, what information is still missing, and what should I prepare for each? Separate eligibility from the chance of winning.”

FAIL: Burger King General Track answer claimed a 3.5 unweighted GPA threshold and special leadership/work/financial-need requirements using a passage explicitly headed James W. McLamore WHOPPER Scholarship. This is cross-track contamination within a correctly named program record. Auburn answer claimed a 3.5 GPA and ACT 29–30 tier, but the three displayed citations did not include the named award's numeric table. It did acknowledge missing scores, recalculated GPA, and competitive selection.

Follow-up: “I haven’t provided SAT or ACT scores. How does that affect what you can conclude about Auburn?”

PARTIAL: correctly said Auburn cannot be fully evaluated without official scores. However, it conflated scores not provided to the app with scores not submitted to Auburn, and added unrelated Burger King requirements from the same special-track passage.

Both senior responses opened Sources (3), showing official Scholarship America Burger King, Auburn Competitive Merit, and Auburn Test Scores passages and URLs. Links were inspected in the popup; external destination navigation was not tested.

Print my plan (2) was invoked, but the browser tool timed out on the print action. The saved count remained correct; print output is not verified.

## Corrections needed before recording

1. Enforce student-cycle applicability in synthesis and review: current-cycle dates must remain labeled examples when the future student cycle is unknown.
2. Preserve sub-award boundaries inside Burger King source passages; General Track must not inherit WHOPPER or employee-track conditions.
3. Require exact cited threshold evidence for Auburn numeric comparisons.
4. Distinguish missing profile scores from unsubmitted application scores; keep follow-ups focused on the requested award.
5. Add regression cases for these exact prompts, then rerun the failed journeys once. Avoid repeated paid attempts merely to obtain a favorable answer.

Additional UI issue observed: some GPA confirmation notices expose raw dictionary formatting. This is secondary to the grounding failures.
