"""Citation resolution gate. Semantic support still requires evaluation."""


def validate_answer(answer):
    supplied = {c.id for c in answer.evidence.chunks}
    supplied.update(ref.id for c in answer.evidence.chunks for ref in c.evidence)
    if any(c.corpus_version != answer.corpus_version for c in answer.evidence.chunks):
        raise ValueError("Mixed corpus versions")
    for block in answer.blocks:
        if not block.evidence_ids or not set(block.evidence_ids).issubset(supplied):
            raise ValueError("Answer has missing or unresolved citations")
    if not answer.blocks and not answer.gaps:
        raise ValueError("Empty answer")
    return answer
