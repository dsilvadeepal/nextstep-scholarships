"""Flag retrieved evidence overlapping reviewed non-rule source spans."""


def retrieval_exclusion_violations(chunks, exclusions):
    hits = []
    for chunk in chunks:
        for ref in chunk.evidence:
            for excluded in exclusions:
                if (
                    ref.source_id == excluded["source_id"]
                    and ref.section_id == excluded["section_id"]
                    and ref.document_version == excluded["document_version"]
                    and ref.start < excluded["end"]
                    and excluded["start"] < ref.end
                ):
                    hits.append(
                        {"chunk_id": chunk.id, "reason": excluded["reason"]}
                    )
    return hits
