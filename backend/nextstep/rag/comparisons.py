"""Conservative arithmetic over an explicitly named ACT table row and user input.

Only negative threshold conclusions are emitted; reaching a tier never proves eligibility.
No inferred test scores, GPA conversions, range extrapolation or source modifications.
"""

import re

from nextstep.models import AnswerBlock


def score_comparisons(question, evidence, records):
    matches = re.findall(
        r"\bACT\s+(?:super)?score\s+(?:is|of|=|:)\s*(\d{1,2})\b",
        question,
        re.IGNORECASE,
    )
    if len(set(matches)) != 1 or not 1 <= int(matches[0]) <= 36:
        return []
    score = int(matches[0])
    names = {r.id: r.name for r in records}
    output, seen = [], set()
    for chunk in evidence.chunks:
        if chunk.program_id in seen or chunk.program_id not in names:
            continue
        name = names[chunk.program_id]
        rows = [line.split("|") for line in chunk.text.splitlines() if "|" in line]
        tier = None
        # Vertical named-award table; generic score-concordance tables do not match.
        section = chunk.heading.partition(" — ")[2].strip()
        if (
            section
            and section.casefold() in name.casefold()
            and len(section.split()) >= 2
        ):
            for row in rows:
                if len(row) >= 2 and re.fullmatch(
                    r"ACT(?:\s+Score)?\s+Required\**", row[0].strip(), re.IGNORECASE
                ):
                    tier = row[1].strip()
        # Horizontal table: bind row label to the selected award's name, not its neighbor.
        if rows and any(h.strip().casefold() == "act" for h in rows[0]):
            col = next(
                i for i, h in enumerate(rows[0]) if h.strip().casefold() == "act"
            )
            for row in rows[1:]:
                label = row[0].strip()
                if (
                    len(row) > col
                    and label
                    and re.search(r"\b" + re.escape(label) + r"\b", name, re.IGNORECASE)
                ):
                    tier = row[col].strip()
        if not tier or not re.fullmatch(r"\d{1,2}(?:\s*[–-]\s*\d{1,2})?\+?", tier):
            continue
        minimum = int(re.match(r"\d+", tier).group())
        if score < minimum:
            output.append(
                AnswerBlock(
                    text=f"Your stated ACT score of {score} is below the listed ACT {tier} tier for {name}. This comparison addresses the score threshold only.",
                    evidence_ids=[chunk.id],
                    program_id=chunk.program_id,
                    kind="explanation",
                    supporting_quotes=[chunk.text],
                )
            )
            seen.add(chunk.program_id)
    return output


def award_classification(question, evidence, records):
    if not re.search(r"guarantee|automatic|competitive", question, re.IGNORECASE):
        return []
    output, seen = [], set()
    names = {r.id: r.name for r in records}
    for chunk in evidence.chunks:
        if chunk.program_id in seen or chunk.program_id not in names:
            continue
        if re.search(
            r"automatic merit scholarships? (?:are|is) awarded",
            chunk.text,
            re.IGNORECASE,
        ):
            output.append(
                AnswerBlock(
                    text=f"{names[chunk.program_id]} is an automatic merit award, subject to all published eligibility and application requirements. This does not confirm an award for you.",
                    evidence_ids=[chunk.id],
                    program_id=chunk.program_id,
                    kind="explanation",
                    supporting_quotes=[chunk.text],
                )
            )
            seen.add(chunk.program_id)
    return output
