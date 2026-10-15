"""Query-time coverage of requested rule facets using existing versioned chunks.

No embeddings, source edits or additional model calls. Baseline fused ranks break ties.
"""

import re

FACETS = (
    (
        "threshold",
        r"gpa|score|tier|minimum|round",
        r"gpa|act|sat|minimum|tier|non.round",
    ),
    ("score_policy", r"score|act|sat", r"superscore|single.test.date|single test date"),
    (
        "eligibility",
        r"eligib|cycle|junior|senior|before applying|qualif",
        r"eligib|must intend|juniors|citizen|permanent residen",
    ),
    (
        "deadline",
        r"deadline|due|when|complete|date",
        r"deadline|priority|by nov|by feb|by dec|pacific time",
    ),
    (
        "materials",
        r"letter|reference|recommendation|document",
        r"letters? of|recommendation|reference",
    ),
    ("application", r"separate|application|apply", r"application|apply"),
    (
        "guarantee",
        r"guarantee|renew|one.time",
        r"not.*guarantee|competitive|automatic|renew|one.time",
    ),
)


def targeted_ranking(question, corpus, ranked):
    rank = {c.id: i for i, c in enumerate(ranked)}
    anchors, diagnostics = [], {}
    for name, trigger, pattern in FACETS:
        if not re.search(trigger, question, re.IGNORECASE):
            continue
        candidates = []
        for chunk in corpus:
            if chunk.token_count > 5000:
                continue
            text = chunk.text.lower()
            if not re.search(pattern, text, re.IGNORECASE):
                continue
            title, _, section = chunk.heading.partition(" — ")
            score = len(re.findall(pattern, text, re.IGNORECASE)) / max(
                len(text.split()), 20
            )
            # Prefer an award-specific table to a generic score equivalency chart.
            if name == "threshold":
                if (
                    re.search(r"\d", text)
                    and "gpa" in text
                    and ("act" in text or "sat" in text)
                ):
                    score += 3
                if "|" in text:
                    score += 1
                if (
                    section
                    and section.lower() in title.lower()
                    and len(section.split()) >= 2
                ):
                    score += 3
            if name == "deadline":
                score += (
                    bool(
                        re.search(
                            r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december|nov\.?|dec\.?)\s+\d",
                            text,
                        )
                    )
                    * 2
                )
            if name == "materials":
                score += (
                    bool(
                        re.search(
                            r"\b(two|2)\b.{0,35}(letter|reference|recommendation)", text
                        )
                    )
                    * 2
                )
            if name == "eligibility":
                score += ("eligibility requirements" in text) * 2
            if name == "application":
                score += ("separate" in text) * 2
            candidates.append(
                (score, -rank.get(chunk.id, len(corpus)), chunk.id, chunk)
            )
        if candidates:
            selected = max(candidates, key=lambda x: x[:3])[3]
            diagnostics[name] = selected.id
            if selected.id not in {c.id for c in anchors}:
                anchors.append(selected)
    seen = {c.id for c in anchors}
    return anchors + [c for c in ranked if c.id not in seen], diagnostics
