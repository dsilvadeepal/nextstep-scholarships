"""Guard source-audit corrections against future corpus regressions; no paid calls."""

import json
from datetime import date
from pathlib import Path

from nextstep.matching import match_catalog
from nextstep.models import Chunk, NormalizedDocument, Scholarship, StudentProfile

ROOT = Path(__file__).resolve().parents[1]


def corpus():
    bundle = json.loads((ROOT / "data/reviewed-corpus-2026-10-14.json").read_text())
    records = {r["id"]: Scholarship.model_validate(r) for r in bundle["records"]}
    chunks = [Chunk.model_validate(c) for c in bundle["chunks"]]
    docs = {
        d["source_id"]: NormalizedDocument.model_validate(d) for d in bundle["sources"]
    }
    return bundle, records, chunks, docs


def test_reviewed_corpus_provenance_and_exclusion_boundary():
    bundle, records, chunks, docs = corpus()
    assert len(records) == 18
    assert len({c.id for c in chunks}) == len(chunks)
    assert {c.program_id for c in chunks} == set(records)
    allowed = {
        (s["program_id"], s["source"], sid)
        for s in bundle["selections"]
        for sid in s["sections"]
    }
    for chunk in chunks:
        assert chunk.corpus_version == bundle["version"]
        for ref in chunk.evidence:
            doc = docs[ref.source_id]
            section = next(s for s in doc.sections if s.id == ref.section_id)
            assert (chunk.program_id, ref.source_id, ref.section_id) in allowed
            assert ref.document_version == doc.content_hash
            assert section.text[ref.start : ref.end] == ref.quote == chunk.text
    assert not {
        "gafutures-hope",
        "amicalola",
        "georgias-own",
        "delta-annual",
        "cfa-criteria",
    } & set(records)
    delta = [c for c in chunks if c.program_id == "delta-hbcu"]
    assert {sid for c in delta for sid in c.section_ids} <= {"s2", "s3", "s4", "s5"}
    assert all("Tyler Lawrence" not in c.text for c in delta)


def test_reviewed_cycles_exclusions_and_unknown_gpa_are_preserved():
    _, records, chunks, _ = corpus()
    cfa = "\n".join(c.text for c in chunks if c.program_id == "cfa-community")
    assert "Be 18 years of age by July 15, 2027." in cfa
    assert "three business days after the application deadline" in cfa
    assert "Past recipients may not reapply." in cfa
    assert "2027-2028" in cfa
    ua = "\n".join(c.text for c in chunks if c.program_id == "ua-presidential")
    assert "UA does not use superscores" in ua
    auburn = "\n".join(c.text for c in chunks if c.program_id == "auburn-presidential")
    assert "ACT/SAT superscore" in auburn
    assert "not a guarantee" in auburn
    gsu = "\n".join(c.text for c in chunks if c.program_id == "georgia-southern-merit")
    assert "recalculated core GPA" in gsu and "non-renewable" in gsu
    park = next(c for c in records["park"].conditions if c.kind == "gpa")
    assert park.value == {"value": 3.8, "type": "unweighted", "scale": None}
    matches = {
        m.scholarship_id: m
        for m in match_catalog(
            list(records.values()),
            StudentProfile(grade=12, graduation_year=2027),
            date(2026, 10, 14),
        )
    }
    assert matches["coolidge"].group == "unmet"
    assert matches["coca-cola"].timing == "closed"
    assert matches["park"].fit == "Missing profile information"


def test_real_rules_do_not_treat_preferences_or_high_gpa_as_full_eligibility():
    _, records, _, _ = corpus()
    profiles = [
        StudentProfile(),
        StudentProfile(grade=11, graduation_year=2028, residence={"state": "GA"}),
        StudentProfile(
            grade=12,
            graduation_year=2027,
            residence={"state": "FL"},
            prospective_colleges=["Morehouse College"],
            gpa={"value": 4, "type": "weighted", "scale": 4},
        ),
    ]
    for profile in profiles:
        matches = {
            m.scholarship_id: m
            for m in match_catalog(list(records.values()), profile, date(2026, 10, 14))
        }
        assert all(m.fit != "Potential match" for m in matches.values())
        # An intended HBCU is not evidence of an acceptance letter.
        assert any(c.status == "unknown" for c in matches["delta-hbcu"].conditions)
        # Source limitations remain visible even with an excellent self-reported GPA.
        assert any(
            c.status == "unknown" for c in matches["georgia-southern-merit"].conditions
        )
        assert matches["coca-cola"].timing == "closed"
    assert matches["delta-hbcu"].group == "unmet"
    assert matches["georgia-southern-merit"].group == "unmet"
