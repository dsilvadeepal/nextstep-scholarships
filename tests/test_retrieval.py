from nextstep.models import Chunk, RetrievalRequest
from nextstep.rag.retrieve import Retriever

def chunk(i,program,version='v'):
    return Chunk(id=str(i),program_id=program,source_id='s',corpus_version=version,text='Senior science scholarship',heading=program,section_ids=['s'],token_count=4)

class Dense:
    def search(self,question,version,program_id,limit):
        # Deliberately returns stale/incorrect entries to test boundary validation.
        return ['stale','wrong']+[str(i) for i in range(20)]

def test_equal_program_budget_and_no_stale_context():
    corpus=[chunk(i,'a' if i<10 else 'b') for i in range(20)]+[chunk('stale','a','old'),chunk('wrong','c')]
    retriever=Retriever(corpus,Dense())
    for method in ['semantic','hybrid']:
        result=retriever.retrieve(RetrievalRequest(question='science',program_ids=['a','b'],corpus_version='v',method=method))
        assert len(result.chunks)==8
        assert [c.program_id for c in result.chunks].count('a')==4
        assert [c.program_id for c in result.chunks].count('b')==4
        assert all(c.corpus_version=='v' for c in result.chunks)
        assert sum(c.token_count for c in result.chunks)<=5000
