"""Compile explicitly reviewed source spans into an inactive candidate; no API calls."""

import hashlib
import json
from collections import Counter
from datetime import date
from pathlib import Path

from expansion_chunks import make_reviewed_chunks
from nextstep.models import Condition, EvidenceRef, NormalizedDocument, Scholarship

ROOT = Path(__file__).resolve().parents[1]
VERSION = "candidate-2026-10-16-v4"
RESEARCH = ROOT / "artifacts/research/expansion-2026-10-16"
BASE = json.loads((ROOT / "data/reviewed-corpus-2026-10-14.json").read_text())
DOCS = {d["source_id"]: NormalizedDocument.model_validate(d) for d in BASE["sources"]}
DOCS.update(
    {
        p.stem: NormalizedDocument.model_validate_json(p.read_text())
        for p in (RESEARCH / "normalized").glob("*.json")
    }
)
records = [
    Scholarship.model_validate(r).model_copy(update={"corpus_version": VERSION})
    for r in BASE["records"]
]
selections = []
review_notes = []


def select(pid, source, ids, start=None, stop=None):
    spans = []
    for sid in ids.split():
        s = next(s for s in DOCS[source].sections if s.id == sid)
        a = s.text.index(start) if start else 0
        z = s.text.index(stop, a) if stop else len(s.text)
        if s.text[a:z].strip():
            spans.append({"section_id": sid, "start": a, "end": z})
    selections.append({"program_id": pid, "source": source, "spans": spans})


def cut(source, sid, start, stop=None, reason="Non-operational/background passage"):
    s = next(s for s in DOCS[source].sections if s.id == sid)
    a = s.text.index(start)
    z = s.text.index(stop, a) if stop else len(s.text)
    for row in selections:
        if row["source"] != source:
            continue
        result = []
        for span in row["spans"]:
            if span["section_id"] != sid or span["end"] <= a or span["start"] >= z:
                result.append(span)
            else:
                if span["start"] < a:
                    result.append({**span, "end": a})
                if span["end"] > z:
                    result.append({**span, "start": z})
        row["spans"] = result
    review_notes.append(
        {"source_id": source, "section_id": sid, "start": a, "end": z, "reason": reason}
    )


# Existing award IDs stay stable. Their previously selected sections are re-packed,
# with newly disallowed narrative removed before any embeddings are generated.
for row in BASE["selections"]:
    select(row["program_id"], row["source"], " ".join(row["sections"]))
register = json.loads((ROOT / "data/content-exclusions-2026-10-16.json").read_text())
for e in register["exclusions"]:
    cut(e["source_id"], e["section_id"], e["quote"], reason=e["reason"])
    # cut with no stop removes the tail; restore operational text after an interior exclusion.
    if e["end"] < len(
        next(s for s in DOCS[e["source_id"]].sections if s.id == e["section_id"]).text
    ):
        for row in BASE["selections"]:
            if row["source"] == e["source_id"] and e["section_id"] in row["sections"]:
                selections.append(
                    {
                        "program_id": row["program_id"],
                        "source": row["source"],
                        "spans": [
                            {
                                "section_id": e["section_id"],
                                "start": e["end"],
                                "end": len(
                                    next(
                                        s
                                        for s in DOCS[e["source_id"]].sections
                                        if s.id == e["section_id"]
                                    ).text
                                ),
                            }
                        ],
                    }
                )
cut(
    "coolidge-faq",
    "s1",
    "Finally, many applicants report",
    "What",
    reason="Applicant testimonial/promotion",
)


def admit(
    pid,
    name,
    family,
    sources,
    eligibility,
    cycle,
    deadline=None,
    opens=None,
    timezone=None,
    grade=None,
    grad=None,
    state=None,
    citizenship=None,
    gpa=None,
    materials=(),
    notes=(),
):
    for source, ids in sources.items():
        select(pid, source, ids)
    key, sid = eligibility
    doc = DOCS[key]
    s = next(s for s in doc.sections if s.id == sid)
    ref = EvidenceRef(
        id=hashlib.sha256(f"{pid}:{key}:{sid}".encode()).hexdigest()[:24],
        source_id=key,
        document_version=doc.content_hash,
        section_id=sid,
        quote=s.text,
        start=0,
        end=len(s.text),
        url=doc.url,
        fetched_at=doc.fetched_at,
        title=s.heading,
    )
    # An explicit unresolved complete-rule check prevents a few machine-readable
    # fields from being treated as a comprehensive personal eligibility decision.
    conditions = [
        Condition(
            id=f"{pid}-full-rules",
            kind="other",
            operator="unknown",
            evidence=[ref],
            reason="Confirm the full sponsor eligibility and exclusions; structured fields do not establish complete eligibility.",
        )
    ]
    for kind, operator, value in [
        ("grade", "eq", grade),
        ("graduation_year", "eq", grad),
        ("state", "eq", state),
        ("citizenship", "in", citizenship),
        ("gpa", "gte", gpa),
    ]:
        if value is not None:
            conditions.append(
                Condition(
                    id=f"{pid}-{kind}",
                    kind=kind,
                    operator=operator,
                    value=value,
                    evidence=[ref],
                )
            )
    sponsor = next(
        r["sponsor"]
        for r in json.loads(
            (ROOT / "data/expansion-source-inventory-2026-10-16.json").read_text()
        )
        if r["family"] == family
    )
    records.append(
        Scholarship(
            id=pid,
            corpus_version=VERSION,
            name=name,
            sponsor=sponsor,
            scope="Official first-year scholarship guidance; complete eligibility requires sponsor verification.",
            cycle=cycle,
            source_checked_at=date(2026, 10, 16),
            conditions=conditions,
            deadline=date.fromisoformat(deadline) if deadline else None,
            opens=date.fromisoformat(opens) if opens else None,
            timezone=timezone,
            date_precision="date" if deadline else None,
            information_status="source_checked",
            official_url=doc.url,
            evidence=[ref],
            materials=list(materials),
            cycle_metadata={
                "application_cycle": cycle,
                "high_school_graduation_year": grad,
            },
            field_evidence={
                "name": [ref.id],
                "sponsor": [ref.id],
                "cycle": [ref.id],
                "official_url": [ref.id],
            },
        )
    )
    review_notes.append({"program_id": pid, "family": family, "notes": list(notes)})


admit(
    "watson-brown",
    "Watson-Brown Scholarship",
    "watson-brown",
    {"exp-watson-brown-1": "s3", "exp-watson-brown-2": "s1"},
    ("exp-watson-brown-2", "s1"),
    "2027–28",
    deadline="2027-02-01",
)
cut("exp-watson-brown-2", "s1", "How to Apply", "Who is Eligible?", reason="Navigation")
admit(
    "elks-mvs",
    "Elks Most Valuable Student Scholarship",
    "elks-mvs",
    {
        "exp-elks-mvs-1": "s1 s2",
        "exp-elks-mvs-2": "s1 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 s12 s13 s14 s15",
    },
    ("exp-elks-mvs-2", "s2"),
    "2027 contest",
    deadline="2026-11-12",
    timezone="America/Los_Angeles",
    grade=12,
    citizenship=["US citizen"],
)
cut("exp-elks-mvs-1", "s1", "html", "If prompted,", reason="Navigation")
cut(
    "exp-elks-mvs-1",
    "s2",
    "The Elks National Foundation is proud",
    reason="Winner-list promotion",
)
cut(
    "exp-elks-mvs-2",
    "s11",
    "A student can apply for, but cannot accept,",
    "In January,",
    reason="Conflicts with current Legacy page allowing both ENF awards; stacking needs manual verification",
)
admit(
    "elks-legacy",
    "Elks Legacy Awards",
    "elks-legacy",
    {"exp-elks-legacy-1": "s3 s5"},
    ("exp-elks-legacy-1", "s3"),
    "2027 contest",
    deadline="2027-02-01",
    opens="2026-09-01",
    timezone="America/Los_Angeles",
    grade=12,
    notes=[
        "Deadline is 11:59 AM Pacific, not midnight. ENF cross-award stacking statements conflict; do not assert stacking."
    ],
)
cut(
    "exp-elks-legacy-1",
    "s3",
    "Students may apply for more than one ENF scholarship.",
    "Legacy Awards may only",
    reason="Cross-award stacking conflict with MVS FAQ; manual verification",
)
admit(
    "cooke-college",
    "Jack Kent Cooke College Scholarship",
    "cooke",
    {
        "exp-cooke-1": "s2 s3 s4 s5 s6 s7 s8 s9 s10",
        "exp-cooke-2": " ".join(
            f"s{i}"
            for i in [
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
                11,
                13,
                15,
                16,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                30,
                31,
                32,
                33,
                34,
                35,
                36,
                37,
                38,
                39,
                40,
                41,
                43,
                44,
                45,
                47,
                49,
            ]
        ),
    },
    ("exp-cooke-2", "s3"),
    "2027 college scholarship",
    deadline="2026-11-11",
    opens="2026-08-19",
    grade=12,
    grad=2027,
    gpa={"value": 3.75, "scale": None, "type": "unweighted"},
    notes=[
        "Gross-income and AGI wording varies within sponsor text; retain financial review requirement, do not equate the two measures."
    ],
)
admit(
    "geicc",
    "GEICC Energy Workforce Scholarship",
    "geicc",
    {"exp-geicc-1": "s1 s2"},
    ("exp-geicc-1", "s2"),
    "2027 scholarship",
    deadline="2027-03-07",
    opens="2026-10-19",
    grade=12,
    gpa={"value": 2.5, "scale": None, "type": "unknown"},
)
cut(
    "exp-geicc-1",
    "s1",
    "The GEICC Scholarship Program, established",
    "The 2027 scholarship",
    reason="Program history/promotion",
)
admit(
    "cobb-emc",
    "Cobb EMC Foundation College/University Scholarship",
    "cobb-emc",
    {"exp-cobb-emc-1": "s1 s2", "exp-cobb-emc-2": "p1 p2"},
    ("exp-cobb-emc-2", "p1"),
    "2027 scholarship",
    deadline="2027-02-26",
    grade=12,
    notes=[
        "College route only. Acceptance evidence may follow at award time. Teachers/relatives excluded as recommenders. AI essay development prohibited."
    ],
)
cut(
    "exp-cobb-emc-2",
    "p1",
    "Name: ",
    "Please include/attach",
    reason="Blank personal-information form fields",
)
cut(
    "exp-cobb-emc-2",
    "p2",
    "Academic Performance and Potential:",
    "Notice:",
    reason="Blank personal-information form fields",
)
admit(
    "sawnee-youth",
    "Sawnee Foundation Youth Scholarship",
    "sawnee",
    {"exp-sawnee-1": "s2 s3"},
    ("exp-sawnee-1", "s2"),
    "2027 scholarship",
    deadline="2027-01-08",
    grade=12,
    gpa={"value": 2.0, "scale": None, "type": "unknown"},
    notes=[
        "Linked form/conditions contain 2025/2026 dates and are excluded; verify current packet with scholarships@sawnee.coop."
    ],
)
cut(
    "exp-sawnee-1",
    "s3",
    "Previous Scholarship Winners",
    reason="Winner link and unrelated navigation",
)
admit(
    "gsu-stamps-presidential",
    "Georgia State Stamps and Presidential Scholarships",
    "gsu-scholars",
    {
        "exp-gsu-scholars-1": "s2 s3 "
        + " ".join(f"s{i}" for i in list(range(7, 19)) + [21, 22])
    },
    ("exp-gsu-scholars-1", "s3"),
    "Fall 2027 entry",
    deadline="2026-11-15",
    timezone="America/New_York",
    notes=[
        "Stamps requires GA residency and HOPE/Zell eligibility; Presidential also allows out-of-state/international. Recommendation due November 20. Interview date unconfirmed; stale February 2026 sentence excluded."
    ],
)
cut(
    "exp-gsu-scholars-1",
    "s3",
    "Those invited to participate",
    "For questions",
    reason="Stale February 2026 notification sentence in current 2027 page",
)
admit(
    "burger-king-general",
    "Burger King Scholars — General Track",
    "burger-king",
    {
        "exp-burger-king-2": "s1 s2 s5 s6 s7 s8 s9 s10 s11 s12 "
        + " ".join(f"s{i}" for i in range(13, 25))
    },
    ("exp-burger-king-2", "s5"),
    "2027–28",
    deadline="2026-12-15",
    opens="2026-10-15",
    timezone="America/Chicago",
    grade=12,
    notes=[
        "General track only; employee tracks and James W. McLamore eligibility are separate. First 30,000 community applications reviewed."
    ],
)
cut(
    "exp-burger-king-2", "s24", "Browse More Scholarships", reason="Unrelated promotion"
)
admit(
    "live-mas-new",
    "Taco Bell Live Más Scholarship — New Applicants",
    "live-mas",
    {
        "exp-live-mas-1": "s2 s3 s5",
        "exp-live-mas-2": "s2 s3 s4 s5",
        "exp-live-mas-3": "p1 p2 p3 p4 p5 p6 p7",
    },
    ("exp-live-mas-3", "p1"),
    "2026–27 application / 2027–28 funding",
    deadline="2027-01-05",
    opens="2026-10-13",
    timezone="America/Los_Angeles",
    notes=[
        "Age 16–26; no previous award for new-applicant route. AI may assist organization/grammar but cannot substantially author responses; disclosure required."
    ],
)
admit(
    "gates",
    "The Gates Scholarship",
    "gates",
    {"exp-gates-1": "s1 s2 s3 s4 s5"},
    ("exp-gates-1", "s4"),
    "2027 selection",
    deadline="2026-09-15",
    opens="2026-07-15",
    grade=12,
    citizenship=["US citizen", "permanent resident"],
    gpa={"value": 3.3, "scale": 4, "type": "weighted"},
    notes=["Deadline has passed despite stale Open label; date governs closed status."],
)
cut(
    "exp-gates-1",
    "s1",
    "Status:",
    "Available",
    reason="Open label contradicts elapsed September 2026 deadline; retain dated timeline",
)
admit(
    "hagan",
    "Hagan Scholarship — U.S. High School Route",
    "hagan",
    {
        "exp-hagan-1": "s3",
        "exp-hagan-2": "s3",
        "exp-hagan-3": "p2 p3 p4 p5 p6",
        "exp-hagan-4": "p1",
        "exp-hagan-5": "p1",
        "exp-hagan-6": "s3",
    },
    ("exp-hagan-4", "p1"),
    "2027–28",
    deadline="2026-12-01",
    opens="2026-09-01",
    grad=2027,
    gpa={"value": 3.5, "scale": None, "type": "unknown"},
    notes=[
        "Fall deadline stored; spring application March 15, 2027 is a separate opportunity. Apply once only. U.S. high-school attendance required, not U.S. citizenship. GPA scale/type unspecified."
    ],
)
admit(
    "ron-brown",
    "Ron Brown Signature Scholarship",
    "ron-brown",
    {"exp-ron-brown-1": "s1 s2 s3 s4 s5"},
    ("exp-ron-brown-1", "s2"),
    "2027 competition",
    deadline="2026-12-01",
    grade=12,
    citizenship=["US citizen", "permanent resident"],
    notes=[
        "Application December 1; supporting recommendations/transcript December 15; eligibility includes Black/African American identity and financial need."
    ],
)
cut("exp-ron-brown-1", "s2", "Our Leaders Network", reason="Alumni/career promotion")
admit(
    "levine",
    "UNC Charlotte Levine Scholarship",
    "levine",
    {
        "exp-levine-1": "s2 s3 s4 s6 s7 s8 s10",
        "exp-levine-2": "s1",
        "exp-levine-3": "s1",
        "exp-levine-4": "s1 s2",
        "exp-levine-5": "s1 s2",
    },
    ("exp-levine-4", "s2"),
    "2026–27 selection",
    deadline="2026-10-15",
    opens="2026-08-15",
    citizenship=["US citizen", "permanent resident"],
    notes=[
        "Nomination deadline October 15 has passed for new entrants. Existing nominees: university application November 1; supplement and three recommendations November 15. Finalist averages are excluded, not thresholds."
    ],
)
admit(
    "morehead-cain",
    "UNC Morehead-Cain Scholarship — Out-of-State Route",
    "morehead-cain",
    {
        "exp-morehead-cain-1": "s3 s7 s9",
        "exp-morehead-cain-2": "s1 s2 s3 s4 s5 s6 s7 s8",
        "exp-morehead-cain-3": "s2 s3 s4",
        "exp-morehead-cain-4": "s1",
    },
    ("exp-morehead-cain-3", "s3"),
    "2026–27 selection / Class of 2031",
    deadline="2026-10-01",
    opens="2026-08-15",
    notes=[
        "Direct application deadline passed. ARP nomination possible via UNC Early Action October 15, also passed. Do not treat Class of 2031 as college-entry year."
    ],
)
admit(
    "robertson",
    "Robertson Scholars Leadership Program",
    "robertson",
    {"exp-robertson-2": "s1 s2 s4 s5", "exp-robertson-3": "s1 s2"},
    ("exp-robertson-2", "s5"),
    "2026–27 selection",
    deadline="2026-11-15",
    opens="2026-08-15",
    notes=[
        "Separate Duke/UNC admission applications. Early-notification deadline October 15; regular November 15. Exclude stale 2025 group-activity sentence."
    ],
)
cut(
    "exp-robertson-2",
    "s4",
    "Applicants not invited to the Group Activity",
    "Invitations to participate",
    reason="Stale November 2025 reference in 2026–27 timeline",
)
admit(
    "fsu-presidential",
    "Florida State Presidential Scholars",
    "fsu-presidential",
    {"exp-fsu-presidential-1": "s2"},
    ("exp-fsu-presidential-1", "s2"),
    "Fall 2027 entry",
    deadline="2026-12-01",
    timezone="America/New_York",
    notes=[
        "University Honors admission and essay required. Video responses February 28, 2027; required campus interviews April 2–3. No separate Stamps guarantee."
    ],
)
admit(
    "uah-out-of-state",
    "UAH Freshman Out-of-State Academic Scholarships",
    "uah",
    {"exp-uah-1": "s1 s2 s3 s4"},
    ("exp-uah-1", "s2"),
    "2027–28",
    notes=[
        "May 15, 2027 is an upgrade cutoff, not an asserted application deadline. GPA scale/type unspecified. ACT superscore accepted; ACT science no longer considered. Alabama/Tennessee residents use another chart."
    ],
)
admit(
    "gatech-stamps-gold",
    "Georgia Tech Stamps President’s and Gold Scholarships",
    "gatech",
    {
        "exp-gatech-1": "s1 s2",
        "exp-gatech-2": "s1",
        "exp-gatech-3": "s1",
        "exp-gatech-4": "s1 s2 s3 s4 s5 s6",
    },
    ("exp-gatech-3", "s1"),
    "Fall 2027 entry",
    deadline="2026-10-15",
    citizenship=["US citizen", "permanent resident", "UK citizen"],
    notes=[
        "GA deadline October 15; non-GA November 2. Current dated calendar governs April 9–10, 2027 interviews; undated March sentence excluded. Citizenship from application review, no broader exception inferred."
    ],
)
cut(
    "exp-gatech-1",
    "s1",
    "Around 150 finalists",
    reason="Undated March timing conflicts with dated April 2027 calendar",
)
admit(
    "uab-out-of-state",
    "UAB Out-of-State Freshman Scholarships",
    "uab",
    {"exp-uab-1": "s2 s3 s4 s5 s6 s9 s10"},
    ("exp-uab-1", "s2"),
    "2027–28",
    deadline="2027-05-01",
    grade=12,
    notes=[
        "Current official page now downloads successfully; prior coverage gap can be retired for candidate. No superscore; merit tables and test-optional route kept separate. GPA scale/type unspecified."
    ],
)
admit(
    "south-alabama-out-of-state",
    "South Alabama Freshman Admission Scholarship — Out-of-State",
    "south-alabama",
    {"exp-south-alabama-2": "s8 s9 s10 s11"},
    ("exp-south-alabama-2", "s9"),
    "Fall 2027 entry",
    deadline="2027-02-15",
    gpa={"value": 3.0, "scale": None, "type": "unknown"},
    notes=[
        "Priority deadline for Fall 2027 anchored by official scholarship landing-page calendar. Table is evergreen current guidance; amounts not labeled a 2027–28 guarantee. No institutional cap inferred from old 2024–25 policy."
    ],
)
select(
    "south-alabama-out-of-state",
    "exp-south-alabama-3",
    "s2",
    start="Dates and Deadlines",
    stop="October 1",
)

# Final operational-content review: remove duplicate responsive-page copies,
# recipient statistics/testimonials, and background rationale within mixed FAQs.
for row in selections:
    if row["source"] == "exp-cooke-1":
        row["spans"] = [s for s in row["spans"] if s["section_id"] in ("s3", "s7")]
cut(
    "exp-cooke-1",
    "s7",
    "Last year’s cohort",
    "During the selection process",
    reason="Past-recipient income statistic is not an eligibility threshold",
)
cut(
    "exp-ron-brown-1",
    "s1",
    "rbsp",
    reason="Recipient statistics and named alumni testimonial",
)
cut(
    "exp-ron-brown-1",
    "s1",
    "Since the Program’s inception",
    "Applicants for the Ron Brown",
    reason="Historical recipient counts",
)
cut(
    "exp-ron-brown-1",
    "s5",
    "Since 1996,",
    "3. Does",
    reason="Historical recipient count",
)
cut(
    "exp-ron-brown-1",
    "s5",
    "However, the Ron Brown Scholar Program strongly",
    "4. When",
    reason="Alumni relationship promotion",
)
cut(
    "exp-ron-brown-1",
    "s5",
    "19. Which schools",
    reason="Alumni outcomes and promotional statistics",
)
cut(
    "exp-hagan-2",
    "s3",
    "How many colleges and universities",
    "How much is the Hagan Scholarship worth?",
    reason="Recipient attendance statistics",
)
cut(
    "exp-hagan-2",
    "s3",
    "What are my chances of graduating",
    "Can the Hagan Scholarship be used to Study Abroad?",
    reason="Recipient outcome statistic and background advice",
)
cut(
    "exp-hagan-2",
    "s3",
    "Why are recipients required to work?",
    "Can work study",
    reason="Grantor biography/rationale; work requirement retained separately",
)
cut(
    "exp-hagan-2",
    "s3",
    "Why so particular",
    "Is there an application or processing fee?",
    reason="Administrative rationale",
)
cut("exp-hagan-2", "s3", "Hagan Scholarship Brochure", reason="Navigation/footer")
cut(
    "exp-hagan-4",
    "p1",
    "Hagan Scholars have attended",
    "Recipients who graduate",
    reason="Recipient attendance statistics",
)

# Source-specific ambiguity remains visible and prevents match claims.
for record in records:
    if record.id == "cooke-college":
        record.information_status = "conflicting"
        record.conflicts = {
            "transcript_requirement": [
                "How-to-apply: unofficial transcript; official may be requested for semifinalists",
                "FAQ: official transcript via counselor",
            ],
            "income_measure": ["annual gross income", "adjusted gross income"],
        }
    if record.id == "elks-mvs" or record.id == "elks-legacy":
        record.conflicts = {
            "award_stacking": [
                "MVS FAQ says cannot accept more than one ENF award",
                "Legacy page says both ENF awards may be accepted; verify with scholarship@elks.org",
            ]
        }

CYCLES = {
    "watson-brown": {"application_cycle": "2027–28"},
    "elks-mvs": {"application_cycle": "2027 contest"},
    "elks-legacy": {"application_cycle": "2027 contest"},
    "cooke-college": {
        "application_cycle": "2026",
        "college_entry_year": 2027,
        "high_school_graduation_year": 2027,
    },
    "geicc": {"application_cycle": "2026–27"},
    "cobb-emc": {"application_cycle": "2027 scholarship"},
    "sawnee-youth": {"application_cycle": "2027 scholarship"},
    "gsu-stamps-presidential": {
        "application_cycle": "2026",
        "college_entry_year": 2027,
    },
    "burger-king-general": {
        "application_cycle": "2026",
        "award_academic_year": "2027–28",
    },
    "live-mas-new": {"application_cycle": "2026–27", "award_academic_year": "2027–28"},
    "gates": {"application_cycle": "2026"},
    "hagan": {
        "application_cycle": "2026–27",
        "award_academic_year": "2027–28",
        "high_school_graduation_year": 2027,
    },
    "ron-brown": {"application_cycle": "2027 competition"},
    "levine": {"application_cycle": "2026–27"},
    "morehead-cain": {"application_cycle": "2026–27"},
    "robertson": {"application_cycle": "2026–27"},
    "fsu-presidential": {"application_cycle": "2026–27", "college_entry_year": 2027},
    "uah-out-of-state": {"college_entry_year": 2027, "award_academic_year": "2027–28"},
    "gatech-stamps-gold": {"college_entry_year": 2027, "application_cycle": "2026"},
    "uab-out-of-state": {"award_academic_year": "2027–28"},
    "south-alabama-out-of-state": {"college_entry_year": 2027},
}

MATERIALS = {
    "watson-brown": ["transcript", "letter of recommendation"],
    "elks-mvs": ["Counselor Report", "FAFSA Submission Summary"],
    "elks-legacy": ["ONLINE application"],
    "cooke-college": [
        "Two Academic Recommendations:",
        "One Counselor Recommendation:",
        "School Report:",
        "Test Score(s):",
    ],
    "cobb-emc": [
        "Essay (Maximum 800 words)",
        "High school transcript",
        "one letter of recommendation",
    ],
    "gsu-stamps-presidential": ["high school transcripts", "Letter of Recommendation"],
    "burger-king-general": ["transcript"],
    "live-mas-new": ["Video or Essay"],
    "hagan": ["Personal Essay", "Four-Year Plan", "Letter of Recommendation"],
    "ron-brown": [
        "two letters of recommendation",
        "three essays",
        "school transcripts",
    ],
    "levine": ["Three letters of recommendations", "official high school transcript"],
    "robertson": ["High School Application"],
    "fsu-presidential": ["supplemental University Honors Program application essay"],
}


def main():
    chunks = []
    # Group repeated selection rows, keeping source order for multi-section packing.
    grouped = {}
    for row in selections:
        grouped.setdefault((row["program_id"], row["source"]), []).extend(row["spans"])
    selections[:] = [
        {
            "program_id": pid,
            "source": source,
            "spans": sorted(
                spans,
                key=lambda s: (
                    next(
                        i
                        for i, sec in enumerate(DOCS[source].sections)
                        if sec.id == s["section_id"]
                    ),
                    s["start"],
                ),
            ),
        }
        for (pid, source), spans in grouped.items()
    ]
    by_id = {r.id: r for r in records}
    for pid, values in CYCLES.items():
        from nextstep.models import CycleMetadata

        by_id[pid].cycle_metadata = CycleMetadata(**values)
    by_id["gatech-stamps-gold"].name += " — Georgia Resident Route"
    by_id[
        "gatech-stamps-gold"
    ].scope = "Georgia-resident application route. Non-Georgia calendar dates are contextual guidance, not this record's deadline."
    by_id["gatech-stamps-gold"].conditions.append(
        Condition(
            id="gatech-ga-residency",
            kind="state",
            operator="eq",
            value="GA",
            evidence=by_id["gatech-stamps-gold"].evidence,
        )
    )
    by_id["hagan"].name += " — Fall Application"
    by_id[
        "levine"
    ].scope = "New nomination route; deadline is October 15. Already-nominated applicants have separate November 1 and November 15 submission deadlines."
    # Bind catalog evidence to admitted spans, so excluded narrative cannot enter
    # matching explanations through a full-section catalog reference either.
    for record in records:
        refs = []
        for row in selections:
            if row["program_id"] != record.id:
                continue
            doc = DOCS[row["source"]]
            for span in row["spans"]:
                s = next(s for s in doc.sections if s.id == span["section_id"])
                a, z = span["start"], span["end"]
                refs.append(
                    EvidenceRef(
                        id=hashlib.sha256(
                            f"{record.id}:{doc.source_id}:{s.id}:{a}:{z}".encode()
                        ).hexdigest()[:24],
                        source_id=doc.source_id,
                        document_version=doc.content_hash,
                        section_id=s.id,
                        page=s.page,
                        quote=s.text[a:z],
                        start=a,
                        end=z,
                        url=doc.url,
                        fetched_at=doc.fetched_at,
                        title=s.heading,
                        cycle=record.cycle,
                    )
                )
        for condition in record.conditions:
            replacement = [
                r
                for r in refs
                if any(
                    r.source_id == old.source_id
                    and r.section_id == old.section_id
                    and r.start < old.end
                    and old.start < r.end
                    for old in condition.evidence
                )
            ]
            if not replacement:
                raise ValueError(
                    f"Condition evidence excluded: {record.id}/{condition.id}"
                )
            condition.evidence = replacement
            if condition.id == "gatech-ga-residency":
                condition.evidence = [r for r in refs if r.source_id == "exp-gatech-2"]
                assert condition.evidence
        record.evidence = refs
        for field in record.field_evidence:
            record.field_evidence[field] = [r.id for r in refs]
        for field in (
            "deadline",
            "opens",
            "timezone",
            "cycle_metadata",
            "source_checked_at",
        ):
            if getattr(record, field):
                record.field_evidence[field] = [r.id for r in refs]
        if record.id in MATERIALS:
            record.materials = MATERIALS[record.id]
            matches = [
                r.id
                for r in refs
                if any(
                    item.casefold() in r.quote.casefold() for item in record.materials
                )
            ]
            assert all(
                any(item.casefold() in r.quote.casefold() for r in refs)
                for item in record.materials
            ), record.id
            record.field_evidence["materials"] = matches
    for row in selections:
        chunks.extend(
            make_reviewed_chunks(
                DOCS[row["source"]], by_id[row["program_id"]], row["spans"]
            )
        )
    used = {c.source_id for c in chunks}
    families = {
        r.id: "ua-merit"
        if r.id.startswith("ua-")
        else "auburn-merit"
        if r.id.startswith("auburn-")
        else r.id
        for r in records
    }
    families.update(
        {n["program_id"]: n["family"] for n in review_notes if "family" in n}
    )
    bundle = {
        "version": VERSION,
        "status": "inactive_candidate",
        "prior_version": BASE["version"],
        "program_families": families,
        "sources": [DOCS[k].model_dump(mode="json") for k in sorted(used)],
        "records": [r.model_dump(mode="json") for r in records],
        "chunks": [c.model_dump(mode="json") for c in chunks],
        "selections": selections,
        "review_notes": review_notes,
    }
    path = ROOT / "data/expanded-corpus-2026-10-16.json"
    path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n")
    summary = {
        "version": VERSION,
        "records": len(records),
        "families": len(set(families.values())),
        "contributing_documents": len(used),
        "chunks": len(chunks),
        "unique_text_chunks": len({c.text for c in chunks}),
        "tokens": sum(c.token_count for c in chunks),
        "under_75_tokens": sum(c.token_count < 75 for c in chunks),
        "over_500_tokens": sum(c.token_count > 500 for c in chunks),
        "program_chunk_counts": dict(Counter(c.program_id for c in chunks)),
    }
    (RESEARCH / "candidate-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
