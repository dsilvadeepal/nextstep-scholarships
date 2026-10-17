# NextStep Scholarships — 4–5 minute recording script

Target: **4:45**, including three answer waits. Based on the two verified journeys in [October 17 rehearsal](DEMO_REHEARSAL_2026-10-17.md). Use the final verified demo URL when available; publication is not yet complete. Do not show keys, Secrets, billing screens or the terminal during the recording.

Before recording: open the app and this script side by side; copy the prompts below to a scratch note. Use two fresh browser tabs, one per scenario, so the junior profile does not carry into the senior example. Paste instead of typing. Keep sources open only long enough to show the evidence. Allow 10–15 seconds for each generated answer; if necessary trim waiting time in the recording, without implying faster measured latency. Use the hosted demo after its final checks.

## 0:00–0:25 — The problem and promise

**Show:** app landing page.

**Say:** “This is NextStep Scholarships, a scholarship planning app for Georgia high-school juniors and seniors. It combines a confirmed student profile with scholarship source documents, so students can find relevant options, ask follow-up questions, and inspect the evidence. It helps them plan; it does not promise eligibility or an award.”

## 0:25–1:05 — Junior profile and confirmation

**Click:** School year → Junior; Georgia resident → Yes; optional GPA → 3.5; GPA type → Estimated. Paste the junior note below. Review the detected details; check **Use these reviewed details in my matches**; click **Find my matches**.

**Say:** “First, a junior interested in engineering at Georgia Tech or Kennesaw State. They have Science Olympiad experience but no volunteer experience. The app extracts these details for review before matching. Notice that citizenship and residency are already captured. Both college preferences are retained, but our current collection has no Kennesaw-specific scholarship, so the app should not invent one.”

## 1:05–1:55 — Junior planning, chat and evidence

**Click:** locate Georgia Tech Stamps President’s and Gold Scholarships; click **Ask about this**. Wait for the introductory question to finish populating, then replace it with the junior question below. Click **Ask**. When the response appears, open **Sources (n)** and show the calendar passage; close the sources popup.

**Say while waiting:** “The card uses reviewed eligibility rules. The conversation retrieves relevant passages to explain preparation and dates. For a junior, a published deadline may belong to a different application cycle.”

**Say after reading:** “Here I’m checking that the answer separates preparation now from dates that need verification for a future cycle. The compact Sources pill opens the original evidence, so I can check the claim instead of simply trusting the model.”

Do not assert a particular answer before reading it. The rehearsal correctly labeled October 15, 2026 as the Fall 2027 cycle; do not describe that closed deadline as upcoming.

## 1:55–2:40 — Senior profile and shortlist

**Click:** switch to the second fresh tab. Senior; Georgia resident Yes; GPA 3.7; Final/school record. Paste the senior note. Review/confirm detected details. Expand **Add more details**: graduation year 2027, GPA scale 4-point, unweighted. Find matches. In company scholarships, add **Burger King Scholars — General Track** to the plan. Expand **Explore**, find **Auburn Academic Charter**, and add it. Check that exactly these two awards are saved.

**Say:** “Now a senior considering engineering at Auburn, with a final 3.7 unweighted GPA. The results separate potential matches from options needing more checking. I’ll save one company award and one college award. Auburn is useful here because an unweighted school GPA is not automatically the GPA Auburn recalculates.”

## 2:40–3:35 — Compare two saved scholarships

**Click:** **Ask about scholarships**; confirm the conversation shows the two saved scholarships; paste the comparison question below; Ask. Open the response’s Sources pill; show Burger King’s General Track threshold, then Auburn’s merit table and GPA footnote; close it.

**Say while waiting:** “I’m asking the app to distinguish confirmed requirements, missing information, and preparation—not just give me a confident yes. It combines the same confirmed profile with source passages about these two awards.”

**Say after reading:** “The important distinction is the GPA calculation. The answer should use Burger King’s General Track rules and keep Auburn’s recalculation and test-score questions unresolved. Meeting a listed requirement also does not tell us the chance of winning.”

## 3:35–4:10 — Conversational refinement

**Click:** in the same conversation, paste the Auburn follow-up below; Ask. Show the focused Auburn answer and open a source if time allows.

**Say:** “I can keep refining the plan. This follow-up should stay focused on Auburn. Not entering SAT or ACT scores in this app does not mean the student failed to submit scores to the university. That distinction is one of the cases we tested.”

## 4:10–4:45 — Explain the RAG and learning

**Show:** return to results, or briefly show the architecture diagram in the submission document. No need to open local admin during this short video.

**Say:** “Under the hood, the current collection has 39 award records across 63 source documents. We use structure-aware chunks targeting 500 tokens with 75-token overlap, OpenAI embeddings, and Pinecone. Hybrid retrieval combines semantic and keyword rankings; up to eight passages ground the answer. I compared retrieval strategies in evals and inspected failures, including wrong award-track evidence and GPA assumptions. My main learning is that a citation alone isn’t enough: the passage must support the right claim, for the right scholarship and application cycle.”

## Copy/paste inputs — not part of the spoken track

### Junior note

```text
I am interested in engineering; I want Georgia Tech and maybe Kennesaw State. I do not have any volunteer experience.But I am part of the Science Olympiad School. I am a Georgia resident and a United States citizen.
```

### Junior question

```text
I’m a junior. Based on the sources, what can I prepare now, and which dates or requirements need checking for my future application cycle? Do not assume the current deadline applies to me.
```

### Senior note

```text
I am interested in engineering and considering Auburn. I am a Georgia resident and a United States citizen.
```

### Comparison question

```text
Compare my two saved scholarships. With a final 3.7 unweighted GPA on a 4-point scale, what requirements can you confirm, what information is still missing, and what should I prepare for each? Separate eligibility from the chance of winning.
```

### Auburn follow-up

```text
I haven’t provided SAT or ACT scores. How does that affect what you can conclude about Auburn?
```

## Recording checks

- Use the final hosted release only after its smoke test; until then the rehearsal is evidence of local behavior.
- Match counts and Sources counts are snapshot-dependent; read what appears, rather than promising a fixed number.
- Ensure Georgia Tech does not ask again for confirmed US citizenship.
- Both college preferences should appear in the reviewed profile; no Kennesaw award exists in this corpus.
- Ensure Auburn's recalculation footnote remains visible in citations.
- If a response fails or contradicts evidence, stop and report it; do not narrate an expected result over a failed response.
- The 95% faithfulness goal is a target, not an achieved result established by this recording. Historical tuning evals are not a new benchmark of every current award.
