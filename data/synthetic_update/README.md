# Synthetic controlled update

These invented rules never belong in the real source register or a production namespace. The automated test stages two separate `synthetic-*` corpora in its temporary database, checks source-to-chunk provenance, shows GPA/deadline changes in matching and cited output together, verifies a failed upsert preserves the old corpus, and rolls back.

Run `uv run pytest tests/test_update_demo.py -q`. No model or Pinecone is called; this proves local version coordination, not live retrieval quality.
