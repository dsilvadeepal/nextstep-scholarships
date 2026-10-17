# Pinecone setup — October 14, 2026

Created at the owner’s explicit request using the API key in ignored `.env`.

- Index: `nextstep-scholarships`
- Serverless: AWS `us-east-1`, on-demand reads
- Dense vectors: 1536 dimensions, cosine similarity
- Deletion protection enabled
- Control-plane readiness and data-plane stats verified; empty at setup (0 vectors)
- `.env` contains `PINECONE_INDEX=nextstep-scholarships`; key never printed
- No documents/vectors uploaded, no OpenAI calls, no billing-plan change
- Credit balance/expiry not independently verified; live extraction/embedding and full RAG verification remain outstanding

This verifies index access/configuration, not application retrieval or eval quality. It matches `text-embedding-3-small` with explicit 1536 dimensions.

## Integration finding for the active build

The installed SDK rejects `pc.Index(host=host, timeout=15)` with TypeError (unexpected timeout keyword); `pc.Index(host=host)` successfully reads stats. The current PineconeStore constructor uses that unsupported keyword. Fix it with a regression test and verify supported request-timeout configuration before claiming the app adapter works. This setup task did not modify the active build’s provider source.
