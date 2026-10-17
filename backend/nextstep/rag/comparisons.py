"""Conservative arithmetic over an explicitly named ACT table row and user input.

Only negative threshold conclusions are emitted; reaching a tier never proves eligibility.
No inferred test scores, GPA conversions, range extrapolation or source modifications.
"""

import re

from nextstep.models import AnswerBlock


def reviewed_conflict_explanations(question, evidence, records):
    topics = {
        "transcript_requirement": (
            r"transcript",
            (
                r"\bunofficial\b.{0,40}\btranscripts?\b",
                r"\bofficial\b.{0,40}\btranscripts?\b",
            ),
        ),
        "income_measure": (
            r"income|\bagi\b",
            (r"annual gross income", r"adjusted gross income"),
        ),
    }
    output = []
    for record in records:
        if record.information_status != "conflicting":
            continue
        own = [c for c in evidence.chunks if c.program_id == record.id]
        for field, (trigger, patterns) in topics.items():
            variants = record.conflicts.get(field)
            if not variants or not re.search(trigger, question, re.IGNORECASE):
                continue
            groups = [
                [c for c in own if re.search(pattern, c.text, re.IGNORECASE)]
                for pattern in patterns
            ]
            pair = next(
                ((a, b) for a in groups[0] for b in groups[1] if a.id != b.id), None
            )
            if pair is None:
                continue
            output.append(
                AnswerBlock(
                    text=f"{record.name}: the reviewed sources use different instructions or terms for {field.replace('_', ' ')}: "
                    + " versus ".join(str(value) for value in variants)
                    + ". This source distinction remains unresolved here; confirm which instructions apply with the official sponsor before applying.",
                    evidence_ids=[c.id for c in pair],
                    program_id=record.id,
                    kind="explanation",
                    supporting_quotes=[c.text for c in pair],
                )
            )
    return output


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
    if re.search(r"deadline|priority", question, re.IGNORECASE) and not re.search(
        r"guarantee|competitive|award type", question, re.IGNORECASE
    ):
        return []
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
