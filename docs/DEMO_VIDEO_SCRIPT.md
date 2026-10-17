# NextStep Scholarships — 4–5 minute recording script

Target: **4:45**, including three answer waits. Based on the two verified journeys in [October 17 rehearsal](DEMO_REHEARSAL_2026-10-17.md). Published app: https://nextstep-scholarships.replit.app/. Both journeys were verified on the published app; see [the hosted check](PUBLISHED_DEMO_CHECK_2026-10-17.md). Do not show keys, Secrets, billing screens or the terminal during the recording.

Before recording: open the app and this script side by side; each step includes its paste-ready text, so you can follow this script from top to bottom. Use two fresh browser tabs, one per scenario, so the senior profile does not carry into the junior example. Paste instead of typing. Keep sources open only long enough to show the evidence. Allow 10–15 seconds for each generated answer; if necessary trim waiting time in the recording, without implying faster measured latency. Both hosted scenarios have passed their recording check.

## 0:00–0:20 — What the app does

**Show:** the app’s opening page, without entering a profile yet.

**Say:** “I built NextStep Scholarships to help Georgia high-school juniors and seniors find scholarships that fit their plans. Students can describe themselves, review their matches, and ask follow-up questions about requirements and what to prepare. The answers link back to scholarship sources so they can check the details.”

## 0:20–0:55 — A look behind the app

**Show:** briefly show the architecture diagram in the submission document, then return to the app. No need to open local admin during this short video.

**Say:** “Behind the app, I’ve organized 39 award records from 63 source documents. I split the content around its structure, aiming for 500-token chunks with 75-token overlap. I use OpenAI embeddings and Pinecone, and combine semantic and keyword search to select up to eight passages for an answer. I also built an evaluation view to compare retrieval strategies and inspect individual answers. Let me show you how that works for a senior, then a junior.”

## 0:55–1:40 — Senior profile and shortlist

**Click:** Senior; Georgia resident Yes; GPA 3.7; Final/school record. Paste the senior note directly below. Review/confirm detected details. Expand **Add more details**: graduation year 2027, GPA scale 4-point, unweighted. Find matches. In company scholarships, add **Burger King Scholars — General Track** to the plan. Expand **Explore**, find **Auburn Academic Charter**, and add it. Check that exactly these two awards are saved.

**Paste into the student description box (not spoken):**

```text
I am interested in engineering and considering Auburn. I am a Georgia resident and a United States citizen.
```

**Say:** “I’ll start with a senior interested in engineering at Auburn, with a final 3.7 GPA. I’m entering their plans in their own words, then checking the details the app picked up. I’ll save Burger King’s General Track and Auburn’s Academic Charter scholarship. That gives me a company award and a college award to compare.”

## 1:40–2:35 — Compare two saved scholarships

**Click:** **Ask about scholarships**; confirm the conversation shows the two saved scholarships; paste the comparison question directly below; Ask. Open the response’s Sources pill; show Burger King’s General Track threshold, then Auburn’s merit table and GPA footnote; close it.

**Paste into the chat question box (not spoken):**

```text
Compare my two saved scholarships. With a final 3.7 unweighted GPA on a 4-point scale, what requirements can you confirm, what information is still missing, and what should I prepare for each? Separate eligibility from the chance of winning.
```

**Say while waiting:** “Now I can ask about both saved scholarships together. I’m asking what the sources confirm, what’s still missing, and what the student should prepare. The conversation uses the same profile I just confirmed.”

**Say after reading:** “Here I can see why the GPA details matter. Burger King has its own published requirement, while Auburn recalculates GPA. I can open this Sources pill to see the actual passages behind the answer. I’m also keeping eligibility separate from the chance of winning.”

## 2:35–3:10 — Conversational refinement

**Click:** in the same conversation, paste the Auburn follow-up directly below; Ask. Show the focused Auburn answer and open a source if time allows.

**Paste into the same chat question box (not spoken):**

```text
I haven’t provided SAT or ACT scores. How does that affect what you can conclude about Auburn?
```

**Say:** “I can keep the conversation going. I haven’t entered SAT or ACT scores, so I’ll ask what that means for Auburn. I want the answer to explain what’s missing here, without assuming the student hasn’t sent scores to the university. I included that distinction in my testing.”

## 3:10–3:50 — Junior profile and confirmation

**Click:** switch to a fresh tab. School year → Junior; Georgia resident → Yes; optional GPA → 3.5; GPA documentation → Estimated. Paste the junior note directly below. Review the detected details; check **Use these reviewed details in my matches**; click **Find my matches**.

**Paste into the student description box (not spoken):**

```text
I am interested in engineering; I want Georgia Tech and maybe Kennesaw State. I do not have any volunteer experience.But I am part of the Science Olympiad School. I am a Georgia resident and a United States citizen.
```

**Say:** “Next I’ll try a junior considering Georgia Tech and Kennesaw State. They’re in Science Olympiad and haven’t volunteered. I can review the citizenship, residency and college details before finding matches. My current collection doesn’t include a Kennesaw-specific award, so I keep that preference without inventing a scholarship for it.”

## 3:50–4:45 — Junior planning, chat and evidence

**Click:** locate Georgia Tech Stamps President’s and Gold Scholarships; click **Ask about this**. Wait for the introductory question to finish populating, then replace it with the junior question directly below. Click **Ask**. When the response appears, open **Sources (n)** and show the calendar passage; close the sources popup.

**Paste into the chat question box, replacing the introductory question (not spoken):**

```text
I’m a junior. Based on the sources, what can I prepare now, and which dates or requirements need checking for my future application cycle? Do not assume the current deadline applies to me.
```

**Say while waiting:** “For this student, I’m more interested in preparation than applying immediately. I’ll ask what they can do now and which dates need checking for their future application cycle.”

**Say after reading:** “The answer separates things they can prepare now from dates they’ll need to verify later. I can open the calendar source and see which cycle that deadline belongs to. The student can keep asking questions from here as their plans develop.”

Do not assert a particular answer before reading it. The rehearsal correctly labeled October 15, 2026 as the Fall 2027 cycle; do not describe that closed deadline as upcoming.

## Recording checks

- Use the published URL above; both scenarios were checked there on October 17.
- Match counts and Sources counts are snapshot-dependent; read what appears, rather than promising a fixed number.
- Ensure Georgia Tech does not ask again for confirmed US citizenship.
- Both college preferences should appear in the reviewed profile; no Kennesaw award exists in this corpus.
- Ensure Auburn's recalculation footnote remains visible in citations.
- If a response fails or contradicts evidence, stop and report it; do not narrate an expected result over a failed response.
- The 95% faithfulness goal is a target, not an achieved result established by this recording. Historical tuning evals are not a new benchmark of every current award.
