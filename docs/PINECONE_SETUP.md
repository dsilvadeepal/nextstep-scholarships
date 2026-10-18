# Pinecone configuration and setup history


Current release uses index `nextstep-scholarships` and namespace `candidate-2026-10-16-v4`, with 201 chunks. The October 17 hosted checks exercised retrieval; this documentation review did not query Pinecone again. See [build status](BUILD_STATUS.md).

## Original setup — October 14

Created at the owner’s explicit request using the API key in ignored `.env`.

- Index: `nextstep-scholarships`
- Serverless: AWS `us-east-1`, on-demand reads
- Dense vectors: 1536 dimensions, cosine similarity
- Deletion protection enabled
- Control-plane readiness and data-plane stats verified; empty at setup (0 vectors)
- `.env` contains `PINECONE_INDEX=nextstep-scholarships`; key never printed
- No documents/vectors uploaded, no OpenAI calls, no billing-plan change
- Credit balance/expiry not independently verified; application retrieval was outside this initial setup checkpoint

This verifies index access/configuration, not application retrieval or eval quality. It matches `text-embedding-3-small` with explicit 1536 dimensions.

## Historical SDK finding — resolved

The installed SDK rejects `pc.Index(host=host, timeout=15)` with TypeError (unexpected timeout keyword); `pc.Index(host=host)` successfully reads stats. The current adapter now configures the Pinecone client and constructs `Index(host=description.host)` without that unsupported argument. The finding is retained as implementation history.
