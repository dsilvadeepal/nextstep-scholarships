"""Compile the manually reviewed pilot. No model calls or provider writes.

Snapshots retain complete normalized documents; only explicitly selected rules sections
become chunks. Every curated condition and material points to exact source text.
"""

import hashlib
import json
from pathlib import Path

from nextstep.ingest.chunk import make_chunks
from nextstep.models import Condition, EvidenceRef, NormalizedDocument, Scholarship

ROOT = Path(__file__).resolve().parents[1]
VERSION = "verified-2026-10-14-v2"
SOURCES = {
    p.stem: NormalizedDocument.model_validate_json(p.read_text())
    for p in (ROOT / "data/reviewed").glob("*.json")
}
records = []
chunks = []
selections = []


def section(key, sid):
    return next(s for s in SOURCES[key].sections if s.id == sid)


def evidence(key, sid, quote=None):
    doc = SOURCES[key]
    s = section(key, sid)
    quote = s.text if quote is None else quote
    assert quote and s.text.count(quote) == 1, (key, sid, quote)
    start = s.text.index(quote)
    return EvidenceRef(
        id=hashlib.sha256(f"{key}:{sid}:{start}:{quote}".encode()).hexdigest()[:24],
        source_id=doc.source_id,
        document_version=doc.content_hash,
        section_id=sid,
        page=s.page,
        quote=quote,
        start=start,
        end=start + len(quote),
        url=doc.url,
        fetched_at=doc.fetched_at,
        title=s.heading,
    )


def rule(
    key, sid, kind="other", operator="unknown", value=None, quote=None, reason=None
):
    ref = evidence(key, sid, quote)
    return Condition(
        id=f"rule-{ref.id}-{kind}",
        kind=kind,
        operator=operator,
        value=value,
        evidence=[ref],
        reason=reason or "Confirm with the sponsor: " + ref.quote.replace("\n", " "),
    )


def add(
    pid,
    name,
    sponsor,
    cycle,
    selected,
    conditions,
    materials,
    deadline=None,
    opens=None,
    timezone=None,
    status="source_checked",
    scope=None,
):
    refs = {r.id: r for c in conditions for r in c.evidence}
    material_text = []
    material_refs = []
    for text, key, sid in materials:
        r = evidence(key, sid)
        refs[r.id] = r
        material_text.append(text)
        material_refs.append(r.id)
    selected_refs = [evidence(key, sid) for key, ids in selected.items() for sid in ids]
    refs.update({r.id: r for r in selected_refs})
    field = {
        k: [r.id for r in selected_refs]
        for k in ("name", "sponsor", "scope", "cycle", "official_url")
    }
    if materials:
        field["materials"] = material_refs
    for k, v in (("deadline", deadline), ("opens", opens), ("timezone", timezone)):
        if v:
            field[k] = [r.id for r in selected_refs]
    cycles = {
        "uga-foundation-fellowship": {
            "application_cycle": "2026–27",
            "college_entry_year": 2027,
        },
        "delta-hbcu": {"application_cycle": "2026"},
        "cfa-community": {
            "application_cycle": "2026",
            "award_academic_year": "2027–28",
        },
        "coca-cola": {"application_cycle": "2026", "high_school_graduation_year": 2027},
        "coolidge": {
            "application_cycle": "2026–27",
            "college_entry_year": 2028,
            "high_school_graduation_year": 2028,
        },
        "georgia-southern-merit": {
            "application_cycle": "2026–27",
            "college_entry_year": 2027,
        },
        "park": {"application_cycle": "2026–27", "college_entry_year": 2027},
        "vanderbilt-ingram": {"application_cycle": "2026"},
    }
    if pid.startswith(("ua-", "auburn-")):
        cycle_metadata = {"application_cycle": "2026–27", "college_entry_year": 2027}
    else:
        cycle_metadata = cycles[
            pid
        ]  # A newly added program requires an explicit review.
    record = Scholarship(
        id=pid,
        corpus_version=VERSION,
        name=name,
        sponsor=sponsor,
        cycle=cycle,
        scope=scope,
        conditions=conditions,
        materials=material_text,
        deadline=deadline,
        opens=opens,
        timezone=timezone,
        date_precision="day" if deadline else None,
        information_status=status,
        official_url=SOURCES[next(iter(selected))].url,
        evidence=list(refs.values()),
        field_evidence=field,
        source_checked_at="2026-10-14",
        cycle_metadata=cycle_metadata,
    )
    records.append(record)
    for key, ids in selected.items():
        doc = SOURCES[key].model_copy(deep=True)
        doc.sections = [
            s.model_copy(update={"program_id": pid})
            for s in doc.sections
            if s.id in ids
        ]
        assert len(doc.sections) == len(ids)
        chunks.extend(make_chunks(doc, [record], VERSION))
        selections.append({"program_id": pid, "source": key, "sections": ids})


def build():
    add(
        "uga-foundation-fellowship",
        "UGA Foundation Fellowship",
        "University of Georgia",
        "Fall 2027 entry; application deadline November 2026",
        {"source-03": ["s2", "s3", "s4", "s5", "s6"]},
        [
            rule(
                "source-03",
                "s3",
                reason="Confirm first-year status: no prior university matriculation; dual enrollment is allowed; transfers and current undergraduates are excluded.",
            ),
            rule(
                "source-03",
                "s4",
                reason="Finalists must attend February 26–27, 2027; alternate interview dates are unavailable.",
            ),
        ],
        [
            (
                "Submit UGA first-year admission, then begin the Honors/Foundation Fellowship application and submit by November 1.",
                "source-03",
                "s5",
            ),
            (
                "First-year admission recommendations are reused for the Fellowship.",
                "source-03",
                "s6",
            ),
        ],
        deadline="2026-11-01",
        scope="First-year university award; competitive selection, no numeric academic cutoff published.",
    )

    add(
        "delta-hbcu",
        "Delta Community HBCU Scholarship — graduating-senior route",
        "Delta Community Credit Union",
        "2026 nomination cycle; not a verified 2027–28 award-year rule",
        {"source-15": ["s2", "s3", "s4", "s5"]},
        [
            rule(
                "source-15",
                "s4",
                "state",
                "eq",
                "GA",
                "Students must be Georgia residents",
            ),
            rule(
                "source-15",
                "s4",
                "grade",
                "eq",
                12,
                "Graduating high school seniors with an official acceptance letter to an HBCU",
            ),
            rule(
                "source-15",
                "s4",
                reason="Confirm an official HBCU acceptance letter. A prospective college choice is insufficient.",
            ),
        ],
        [
            (
                "Submit a 250-word nomination through V-103; self-nominations are accepted; deadline is 6 p.m. ET October 31, 2026.",
                "source-15",
                "s5",
            )
        ],
        deadline="2026-10-31",
        timezone="America/New_York",
        scope="Georgia graduating seniors; current-undergraduate route is outside this pilot's student profile.",
    )

    add(
        "cfa-community",
        "Chick-fil-A Community Scholars",
        "Chick-fil-A, Inc.",
        "2027–2028 academic year; 2027 award",
        {
            "cfa-community-rules": [
                "s1",
                "s2",
                "s4",
                "s5",
                "s6",
                "s7",
                "s8",
                "s9",
                "s10",
                "s11",
            ],
            "source-20": ["s3", "s5", "s7"],
        },
        [
            rule(
                "cfa-community-rules",
                "s5",
                reason="Confirm age 18 by July 15, 2027; qualifying residence at application and award; current senior/undergraduate/graduate status; full-time accredited 2027–28 study; service/leadership in the prior 12 months; minimum 3.0/4.0 cumulative GPA; participation commitment; employee/family exclusions.",
            ),
            rule(
                "source-20",
                "s7",
                "financial_need",
                "eq",
                True,
                "Demonstrate financial need.",
            ),
            rule(
                "cfa-community-rules",
                "s6",
                reason="Confirm you are not a past recipient; past recipients may not reapply.",
            ),
        ],
        [
            (
                "Upload a complete transcript and the required IRS 1040 or Canadian T-1 tax pages; black out SSNs and bank details.",
                "cfa-community-rules",
                "s11",
            ),
            (
                "At least one online recommendation is due within three business days after the application deadline; up to three recommenders may be listed.",
                "cfa-community-rules",
                "s11",
            ),
        ],
        deadline="2026-11-03",
        opens="2026-08-21",
        timezone="America/Chicago",
        scope="Includes incoming first-year students; application closes 3 p.m. Central. GPA weighting is unspecified, so a self-reported GPA cannot establish qualification.",
    )

    add(
        "coca-cola",
        "Coca-Cola Scholars Program",
        "Coca-Cola Scholars Foundation",
        "2027 award; high-school graduation in 2026–2027",
        {"source-21": ["s1", "s3", "s4", "s5", "s6", "s7", "s8", "s10"]},
        [
            rule(
                "source-21",
                "s4",
                "grade",
                "eq",
                12,
                "Expecting to receive high school diploma during current academic year",
            ),
            rule(
                "source-21",
                "s4",
                "graduation_year",
                "eq",
                2027,
                "who will graduate high school during the 2026-2027 academic school year",
            ),
            rule(
                "source-21",
                "s4",
                reason="Confirm school location, qualifying citizenship/immigration status, accredited U.S. degree plans, overall B/3.0 GPA, and all Coca-Cola employee/family and residency exclusions.",
            ),
        ],
        [
            (
                "Phase 1 is an online application with no essays, transcript, or recommendations; this cycle is closed.",
                "source-21",
                "s5",
            )
        ],
        deadline="2026-09-30",
        opens="2026-08-03",
        timezone="America/New_York",
        scope="Closed cycle; 5 p.m. Eastern deadline. Do not present as an open application.",
    )

    add(
        "coolidge",
        "Coolidge Scholarship",
        "Calvin Coolidge Presidential Foundation",
        "2026–27 application cycle; first college enrollment Fall 2028",
        {
            "source-22": ["s1"],
            "source-23": ["s1"],
            "source-24": ["s1"],
            "coolidge-faq": ["s1"],
            "coolidge-criteria": ["s1"],
        },
        [
            rule(
                "source-22",
                "s1",
                "grade",
                "eq",
                11,
                "students in their junior year of high school, or the equivalent if home schooled, are eligible to apply.",
            ),
            rule(
                "source-22",
                "s1",
                "graduation_year",
                "eq",
                2028,
                "only high school juniors graduating in the spring of 2028 and starting college in the fall of 2028 are eligible",
            ),
            rule(
                "source-22",
                "s1",
                reason="Confirm U.S. citizenship or legal permanent residence by deadline; first full-time accredited U.S. undergraduate enrollment in Fall 2028; and no excluded immediate family relationship. Gap-year and early-graduation exceptions are not allowed.",
            ),
        ],
        [
            (
                "All materials and reference letters are due December 1, 2026 at 5 p.m. Pacific; later rounds include an assessment and finalist interview.",
                "source-23",
                "s1",
            ),
            (
                "Request two reference letters, follow the application essays/readings, and report transcript/GPA information; unofficial transcripts are accepted initially.",
                "coolidge-faq",
                "s1",
            ),
            (
                "Reference letters must be in English, at most 1,200 words, individually authored, and uploaded through the emailed form as PDF or Word.",
                "source-24",
                "s1",
            ),
        ],
        deadline="2026-12-01",
        timezone="America/Los_Angeles",
        scope="Current juniors entering Fall 2028; not Fall 2027 seniors. Exact essay prompts must be checked in the application portal.",
    )

    add(
        "georgia-southern-merit",
        "Georgia Southern First-Year Merit Scholarship",
        "Georgia Southern University",
        "Fall 2027 entry only",
        {"source-32": ["s5", "s6", "s7"]},
        [
            rule("source-32", "s5", "state", "eq", "GA", "Georgia residents only"),
            rule(
                "source-32",
                "s7",
                reason="Confirm first-time full-time Fall 2027 enrollment and the university's recalculated admissions core GPA. The minimum tier is 3.50; cumulative transcript GPA is not equivalent.",
            ),
            rule(
                "source-32",
                "s5",
                reason="Confirm Georgia in-state tuition status and a complete admission application by the February 1, 2027 priority date.",
            ),
        ],
        [
            (
                "No separate merit application; submit the complete admission application by February 1, 2027.",
                "source-32",
                "s5",
            )
        ],
        deadline="2027-02-01",
        scope="One-time first-academic-year award: $500/$750/$1,000 by recalculated core GPA; not renewable.",
    )

    ua = section("source-45", "s4").table_rows
    assert len(ua) == 7
    for index, row in enumerate(ua):
        name, act, sat, gpa, amount = row
        add(
            "ua-" + name.lower().replace(" ", "-"),
            "University of Alabama " + name,
            "The University of Alabama",
            "Summer/Fall 2027 entry; 2027 nonresident freshman merit",
            {
                "source-45": ["s1", "s2", "s3", "s4", "s5", "s6", "s11", "s13"],
                "ua-policy": ["s1", "s2", "s3", "s16"],
            },
            [
                rule(
                    "source-45",
                    "s4",
                    reason=f"Confirm UA-qualified GPA {gpa} and ACT {act} OR SAT {sat} for {name} ({amount}/year). The public GPA weighting is not specified; do not compare an arbitrary transcript GPA.",
                ),
                rule(
                    "source-45",
                    "s11",
                    reason="Official testing-agency single-date ACT composite or SAT total required; UA does not use superscores for scholarships.",
                ),
                rule(
                    "source-45",
                    "s13",
                    reason="Confirm first-time nonresident/international Summer/Fall 2027 status and the completed application plus official scores by December 4, 2026; later consideration is funds-dependent.",
                ),
            ],
            [
                (
                    "Automatic merit requires no additional scholarship application; submit official test reports and the admission application by the priority date.",
                    "source-45",
                    "s2",
                ),
                (
                    "Maintain cumulative 3.0 UA GPA and earn at least 67% of attempted UA credits for renewal; gap-term changes require the published request process.",
                    "ua-policy",
                    "s1",
                ),
            ],
            deadline="2026-12-04",
            scope=f"Nonresident/international first-time freshman; {name}: ACT {act} or SAT {sat}, GPA {gpa}, {amount} yearly. December 4 is a priority deadline, not a guaranteed late-application cutoff.",
        )

    for slug, name, sid in [
        ("presidential", "Academic Presidential", "s18"),
        ("heritage", "Academic Heritage", "s19"),
        ("charter", "Academic Charter", "s20"),
    ]:
        add(
            "auburn-" + slug,
            "Auburn " + name + " Scholarship",
            "Auburn University",
            "Fall 2027 nonresident first-year competitive merit",
            {"source-48": ["s4", "s10", "s17", sid, "s21"], "auburn-sat": ["s2", "s3"]},
            [
                rule(
                    "source-48",
                    sid,
                    reason="Confirm the exact nonresident GPA/test tier in the source table; these are competitive consideration ranges, not guaranteed awards.",
                ),
                rule(
                    "source-48",
                    "s4",
                    reason="Confirm summer/fall enrollment immediately after high-school graduation, completed admission file by December 1, and official test reports. Updated scores for reconsideration are due January 11.",
                ),
                rule(
                    "source-48",
                    "s21",
                    reason="Auburn may recalculate nonstandard GPA scales. Confirm its GPA calculation rather than substituting self-reported cumulative GPA.",
                ),
            ],
            [
                (
                    "No separate competitive-merit application; admission fee, transcript, and official scores must complete the admission file by December 1.",
                    "source-48",
                    "s4",
                ),
                (
                    "Auburn uses ACT/SAT superscores and its official ACT/SAT equivalency table. Renewal requires cumulative unadjusted 3.0 Auburn GPA and 24 Auburn credits per academic year.",
                    "source-48",
                    "s4",
                ),
            ],
            deadline="2026-12-01",
            scope="Nonresident route for Georgia students. Chart amounts are estimates and depend on the applicant pool and funding.",
        )

    add(
        "park",
        "NC State Park Scholarship",
        "North Carolina State University",
        "2026–2027 selection cycle; Class of 2031 (Fall 2027 entry)",
        {
            "source-56": [
                "s4",
                "s5",
                "s6",
                "s7",
                "s8",
                "s9",
                "s12",
                "s14",
                "s15",
                "s18",
                "s19",
                "s22",
            ],
            "park-apply": ["s1"],
        },
        [
            rule(
                "source-56",
                "s4",
                "gpa",
                "gte",
                {"value": 3.8, "type": "unweighted", "scale": None},
                "Have a minimum unweighted GPA of 3.80 (non-rounded).",
                reason="Park requires at least 3.80 unweighted, without rounding. Confirm the GPA scale with Park; the public rule does not state a scale.",
            ),
            rule(
                "source-56",
                "s4",
                reason="Confirm U.S. citizen/permanent resident OR graduation from a U.S.-located high school regardless of citizenship; apply for fall first-year baccalaureate admission; transfers excluded.",
            ),
            rule(
                "source-56",
                "s19",
                reason="Confirm availability for the published semifinalist/finalist interviews; alternate dates cannot be arranged.",
            ),
        ],
        [
            (
                "Submit separate NC State admission and Park applications by 11:59 p.m. ET November 1; Park needs two recommendations, advanced coursework information, and two essays.",
                "park-apply",
                "s1",
            ),
            (
                "Park-specific recommendations are required by November 1; at least one recommender must know your academics, and parents/guardians cannot recommend.",
                "source-56",
                "s9",
            ),
            (
                "Two essays, each limited to 600 words; use the current 2026–2027 prompts.",
                "source-56",
                "s7",
            ),
        ],
        deadline="2026-11-01",
        timezone="America/New_York",
        scope="No nomination required; Park testing is optional. Minimum GPA is an eligibility rule, not an award guarantee.",
    )

    add(
        "vanderbilt-ingram",
        "Vanderbilt Ingram Scholars Program",
        "Vanderbilt University",
        "Prospective first-year application due December 1, 2026",
        {"source-64": ["s1", "s3", "s4"], "vanderbilt-application": ["s1", "s2", "s3"]},
        [
            rule(
                "source-64",
                "s4",
                reason="Confirm prospective first-year Vanderbilt admission application and finalist interview availability; selection considers service, character, entrepreneurial spirit, and leadership.",
            ),
            rule(
                "source-64",
                "s3",
                reason="Confirm willingness to meet scholarship obligations: 20 service hours monthly, a summer service project, and weekly meetings; renewal requires 3.0 GPA and service requirements.",
            ),
        ],
        [
            (
                "Apply for admission first; establish MyAppVU, then upload the scholarship responses as PDF/Word. The Ingram application is strongly encouraged and preferred; prospective-student deadline is December 1, 2026.",
                "vanderbilt-application",
                "s2",
            ),
            (
                "Check for the submission date and green check mark; post-submission corrections are not accepted.",
                "vanderbilt-application",
                "s2",
            ),
        ],
        deadline="2026-12-01",
        scope="Prospective first-year route; the February 28 deadline on the same page is for already enrolled students.",
    )

    bundle = {
        "version": VERSION,
        "reviewed_on": "2026-10-14",
        "review_method": "Manual source review and deterministic evidence anchoring; no paid extraction model",
        "sources": [d.model_dump(mode="json") for d in SOURCES.values()],
        "selections": selections,
        "records": [r.model_dump(mode="json") for r in records],
        "chunks": [c.model_dump(mode="json") for c in chunks],
    }
    path = ROOT / "data/reviewed-corpus-2026-10-14.json"
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n")
    print(
        json.dumps(
            {
                "version": VERSION,
                "programs": len(records),
                "chunks": len(chunks),
                "sources": len({c.source_id for c in chunks}),
            }
        )
    )


if __name__ == "__main__":
    build()
