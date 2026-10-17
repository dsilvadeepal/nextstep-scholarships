import re
import time

from nextstep.models import RetrievedEvidence
from nextstep.rag.scope import scope_chunk
from nextstep.rag.target import targeted_ranking
from rank_bm25 import BM25Okapi

HYBRID_WEIGHTS = {"hybrid": (1.0, 1.0), "hybrid_60_40": (0.6, 0.4)}


def tokens(text):
    return re.findall(r"\w+", text.casefold())


class Retriever:
    def __init__(self, chunks, dense):
        self.chunks = chunks
        self.dense = dense

    def retrieve(self, request):
        started = time.monotonic()
        if not request.corpus_version:
            raise ValueError("Retrieval must be pinned to a corpus")
        groups = request.program_ids or [None]
        rankings = []
        scores = {}
        coverage = {}
        for program in groups:
            corpus = [
                scoped
                for c in self.chunks
                if c.corpus_version == request.corpus_version
                and (program is None or c.program_id == program)
                and (scoped := scope_chunk(c)) is not None
            ]
            by_id = {c.id: c for c in corpus}
            limit = (40 if request.method == "semantic" else 20) // len(groups)
            dense_ids = self.dense.search(
                request.question, request.corpus_version, program, limit
            )
            dense = list(dict.fromkeys(i for i in dense_ids if i in by_id))[:limit]
            if request.method in HYBRID_WEIGHTS and corpus:
                bm = BM25Okapi(
                    [tokens(c.heading + " " + c.text) or [""] for c in corpus]
                )
                bm_scores = bm.get_scores(tokens(request.question))
                keyword = [
                    c.id
                    for _, c in sorted(
                        zip(bm_scores, corpus), key=lambda pair: (-pair[0], pair[1].id)
                    )[:limit]
                ]
                fused = {}
                for ranking, weight in zip(
                    (dense, keyword), HYBRID_WEIGHTS[request.method]
                ):
                    for rank, i in enumerate(ranking, 1):
                        fused[i] = fused.get(i, 0) + weight / (60 + rank)
                ordered = sorted(fused, key=lambda i: (-fused[i], i))
                scores.update(fused)
            else:
                ordered = dense
                scores.update({i: 1 / (60 + r) for r, i in enumerate(dense, 1)})
            ranking = [by_id[i] for i in ordered]
            if request.retrieval_policy == "targeted" and program is not None:
                ranking, coverage[program] = targeted_ranking(
                    request.question, corpus, ranking
                )
            rankings.append(ranking)
        selected = []
        used = 0
        seen = set()
        # Round-robin reserves representation before filling remaining slots.
        while any(rankings) and len(selected) < 8:
            for ranking in rankings:
                while ranking:
                    chunk = ranking.pop(0)
                    if chunk.id in seen or used + chunk.token_count > 5000:
                        continue
                    selected.append(chunk)
                    seen.add(chunk.id)
                    used += chunk.token_count
                    break
                if len(selected) == 8:
                    break
        return RetrievedEvidence(
            chunks=selected,
            ranks={c.id: scores.get(c.id, 0.0) for c in selected},
            selection_details=coverage,
            timings={"retrieval_seconds": time.monotonic() - started},
        )
