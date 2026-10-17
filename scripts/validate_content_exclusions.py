"""Reject registered non-operational source spans in a candidate corpus; no API calls.

Usage: python scripts/validate_content_exclusions.py path/to/candidate.json
This check supplements manual section review; it is not a general bio classifier.
"""

import argparse
import json
from pathlib import Path


def violations(bundle, exclusions):
    hits = []
    for chunk in bundle["chunks"]:
        for excluded in exclusions:
            for ref in chunk.get("evidence", []):
                if (
                    ref["source_id"] == excluded["source_id"]
                    and ref["section_id"] == excluded["section_id"]
                    and ref["document_version"] == excluded["document_version"]
                    and ref["start"] < excluded["end"]
                    and excluded["start"] < ref["end"]
                ):
                    hits.append({"chunk_id": chunk["id"], "reason": excluded["reason"]})
    return hits


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    register = json.loads(
        (root / "data/content-exclusions-2026-10-16.json").read_text()
    )
    hits = violations(json.loads(args.bundle.read_text()), register["exclusions"])
    print(json.dumps({"passed": not hits, "violations": hits}, indent=2))
    raise SystemExit(1 if hits else 0)
