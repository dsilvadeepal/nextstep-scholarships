"""Conservative query-time boundaries for reviewed multi-track source pages.

Keep contiguous original excerpts, never rewrite scholarship facts. The index and
original evidence references remain intact; no re-embedding or provider calls.
"""

import re


def scope_chunk(chunk):
    if chunk.program_id != "burger-king-general":
        return chunk
    text = chunk.text
    heading = chunk.heading.rsplit(" — ", 1)[-1]
    if heading == "Eligibility":
        general = re.search(r"BURGER KING\s*®?\s*General Track", text)
        if not general:
            return None  # employee-track continuation, not general eligibility
        start = general.start()
        end = re.search(r"BURGER KING\s*®?\s*Employee-Based Track", text[start:])
        text = text[start : start + end.start()] if end else text[start:]
    elif heading == "Selection of Recipients":
        general = re.search(
            r"(?:BURGER KING\s*®?\s*)?General Track\s*(?:for high school|–)", text
        )
        if not general:
            return None  # WHOPPER / Nancy McLamore criteria
        start = general.start()
        end = re.search(r"(?:BURGER KING\s*®?\s*)?Employee-Based Track", text[start:])
        text = text[start : start + end.start()] if end else text[start:]
    return chunk.model_copy(update={"text": text.strip()})
