import re
import time
from rank_bm25 import BM25Okapi
from nextstep.models import RetrievedEvidence

def tokens(text):
    return re.findall(r'\w+',text.casefold())

class Retriever:
    def __init__(self,chunks,dense):
        self.chunks=chunks; self.dense=dense

    def retrieve(self,request):
        started=time.monotonic()
        if not request.corpus_version:
            raise ValueError('Retrieval must be pinned to a corpus')
        groups=request.program_ids or [None]
        rankings=[]; scores={}
        for program in groups:
            corpus=[c for c in self.chunks if c.corpus_version==request.corpus_version and (program is None or c.program_id==program)]
            by_id={c.id:c for c in corpus}
            limit=(40 if request.method=='semantic' else 20)//len(groups)
            dense_ids=self.dense.search(request.question,request.corpus_version,program,limit)
            dense=list(dict.fromkeys(i for i in dense_ids if i in by_id))[:limit]
            if request.method=='hybrid' and corpus:
                bm=BM25Okapi([tokens(c.heading+' '+c.text) or [''] for c in corpus])
                bm_scores=bm.get_scores(tokens(request.question))
                keyword=[c.id for _,c in sorted(zip(bm_scores,corpus),key=lambda pair:(-pair[0],pair[1].id))[:limit]]
                fused={}
                for ranking in (dense,keyword):
                    for rank,i in enumerate(ranking,1):
                        fused[i]=fused.get(i,0)+1/(60+rank)
                ordered=sorted(fused,key=lambda i:(-fused[i],i)); scores.update(fused)
            else:
                ordered=dense; scores.update({i:1/(60+r) for r,i in enumerate(dense,1)})
            rankings.append([by_id[i] for i in ordered])
        selected=[]; used=0; seen=set()
        # Round-robin reserves representation before filling remaining slots.
        while any(rankings) and len(selected)<8:
            for ranking in rankings:
                while ranking:
                    chunk=ranking.pop(0)
                    if chunk.id in seen or used+chunk.token_count>5000:
                        continue
                    selected.append(chunk); seen.add(chunk.id); used+=chunk.token_count
                    break
                if len(selected)==8: break
        return RetrievedEvidence(chunks=selected,ranks={c.id:scores[c.id] for c in selected},timings={'retrieval_seconds':time.monotonic()-started})
