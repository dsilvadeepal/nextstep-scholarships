"""Freeze fictional evaluation references from the second-pass source snapshots."""

import json

from nextstep.models import EvalCase, StudentProfile
from prepare_reviewed_corpus import evidence
from reviewed_runtime import ROOT

cases = []


def case(
    pid,
    question,
    expected,
    source,
    sid,
    quote,
    *,
    profile=None,
    conditions=None,
    critical=True,
):
    ref = evidence(source, sid, quote)
    c = EvalCase(
        id=f"verified-{len(cases) + 1:02}",
        program_ids=[pid],
        question=question,
        profile=StudentProfile.model_validate(
            profile
            or {"grade": 12, "graduation_year": 2027, "residence": {"state": "GA"}}
        ),
        frozen_date="2026-10-14",
        expected_claims=expected,
        expected_evidence=[ref.id],
        checked_sources=[ref],
        expected_conditions=conditions or {},
        critical=critical,
    )
    cases.append(c)


def main():
    archive = ROOT / "artifacts/research/pre-second-pass-evals"
    archive.mkdir(parents=True, exist_ok=True)
    for name in ("cases.jsonl", "heldout.jsonl"):
        dest = archive / name
        if not dest.exists():
            dest.write_bytes((ROOT / "evals" / name).read_bytes())

    case(
        "cfa-community",
        "I will be 17 on July 15, 2027. What minimum age does Community Scholars require?",
        ["Must be 18 by July 15, 2027; do not claim a 17-year-old qualifies."],
        "cfa-community-rules",
        "s5",
        "Be 18 years of age by July 15, 2027.",
    )
    case(
        "cfa-community",
        "What documents and online recommendations must I submit, and when are recommendations due?",
        [
            "Transcript and required tax return pages; at least one online recommendation within three business days after the application deadline; up to three recommenders."
        ],
        "cfa-community-rules",
        "s11",
        "three business days after the application deadline",
    )
    case(
        "delta-hbcu",
        "I am a Georgia senior who has only chosen an HBCU, with no acceptance yet. What acceptance document is required?",
        [
            "Graduating high school seniors need an official HBCU acceptance letter; a college preference does not establish acceptance."
        ],
        "source-15",
        "s4",
        "Graduating high school seniors with an official acceptance letter to an HBCU",
    )
    case(
        "coolidge",
        "I am a current high school senior. Can I apply to the current Coolidge Scholarship cycle?",
        [
            "Current seniors are not eligible; this cycle is for juniors entering college in Fall 2028."
        ],
        "source-22",
        "s1",
        "No, only current high school juniors intending to enroll as undergraduates full-time for the first time in fall 2028 are eligible to apply for the 2026-27 scholarship.",
    )
    case(
        "coolidge",
        "I am a junior planning to start college after fall 2028 following a gap year. Is an exception allowed?",
        [
            "No; current juniors must first enroll full-time in fall 2028, with no exceptions for starting later."
        ],
        "source-22",
        "s1",
        "No, only current high school juniors intending to enroll as full-time undergraduates for the first time in fall 2028 are eligible to apply for the 2026-27 scholarship. No exceptions to this rule can be made.",
        profile={"grade": 11, "graduation_year": 2028},
    )
    case(
        "coolidge",
        "When must all application materials and reference letters arrive, including time zone?",
        ["December 1, 2026 at 5 p.m. Pacific; reference letters are included."],
        "source-23",
        "s1",
        "December 1, 2026 at 5:00 PM Pacific Time",
    )
    case(
        "coca-cola",
        "Is the 2027 Coca-Cola Scholars application still open on October 14, 2026?",
        ["Closed; deadline was September 30, 2026 at 5 p.m. Eastern."],
        "source-21",
        "s10",
        "The deadline for the 2027 Coke Scholars application is 5pm Eastern on September 30, 2026.",
        conditions={"timing": "closed"},
    )
    case(
        "ua-presidential",
        "Can I use my ACT superscore for Alabama automatic merit, and may I only self-report it?",
        [
            "UA does not use superscores; official ACT composite or SAT total from the testing agency is required."
        ],
        "source-45",
        "s11",
        "UA does not use superscores for scholarship purposes.",
    )
    case(
        "ua-presidential",
        "What GPA, ACT or SAT range and yearly value are listed specifically for the 2027 Alabama Presidential automatic merit award?",
        [
            "Presidential: GPA 3.50+, ACT 32–36 or SAT 1420–1600, $28,000 yearly; do not substitute Presidential Elite."
        ],
        "source-45",
        "s4",
        "Presidential | 32–36 | 1420–1600 | 3.50+ | $28,000",
    )
    case(
        "auburn-presidential",
        "Does Auburn competitive merit use ACT/SAT superscores?",
        [
            "Yes, automatic consideration is based on high school GPA and ACT/SAT superscore; official test reports are required."
        ],
        "source-48",
        "s4",
        "Automatic consideration is based on high school GPA and ACT/SAT superscore.",
    )
    case(
        "auburn-presidential",
        "Are the Fall 2027 competitive merit chart amounts a guaranteed award?",
        [
            "No; the chart is a guide, depends on the applicant pool and available funding, and is not a guarantee."
        ],
        "source-48",
        "s10",
        "This chart is a guide and is not a guarantee of future awards.",
    )
    case(
        "georgia-southern-merit",
        "Can I use my cumulative transcript GPA as the Georgia Southern merit admissions GPA?",
        [
            "No; merit uses the university's recalculated core GPA, which may differ from cumulative transcript GPA."
        ],
        "source-32",
        "s7",
        "This calculated GPA focuses on core academic coursework and may differ from the cumulative GPA on your high school transcript.",
    )
    case(
        "georgia-southern-merit",
        "Is Georgia Southern's Fall 2027 first-year merit award renewable?",
        ["No; it is a one-time first-academic-year grant, not renewable."],
        "source-32",
        "s7",
        "and are not renewable for subsequent years.",
    )
    case(
        "uga-foundation-fellowship",
        "What must I do before I can access the UGA Foundation Fellowship application?",
        [
            "First submit UGA first-year admission, then begin Honors/Foundation Fellowship application; November 1 Fellowship deadline."
        ],
        "source-03",
        "s3",
        "Students must first submit a\nFirst-Year Admission application\nto the University of Georgia in order to gain access to the Foundation Fellowship application.",
    )
    case(
        "uga-foundation-fellowship",
        "If I am a UGA Fellowship finalist, when is the mandatory interview weekend, and are alternate dates offered?",
        ["February 26–27, 2027; mandatory and no alternate interview dates."],
        "source-03",
        "s4",
        "we are unable to offer alternate interview dates.",
    )
    case(
        "park",
        "Do I need a school nomination or endorsement to apply for Park?",
        ["No; the endorsement process has been discontinued."],
        "source-56",
        "s12",
        "the Park Scholarships program has discontinued the endorsement process",
    )
    case(
        "park",
        "What is Park's minimum unweighted GPA, and can I round up to it?",
        ["Minimum 3.80 unweighted, non-rounded; do not round a lower GPA upward."],
        "source-56",
        "s4",
        "Have a minimum unweighted GPA of 3.80 (non-rounded).",
    )
    case(
        "vanderbilt-ingram",
        "I am a prospective first-year student, not currently enrolled. Is my Ingram deadline December 1, 2026 or February 28, 2027?",
        [
            "Prospective first-year deadline December 1, 2026; February 28 is the currently enrolled student route."
        ],
        "source-64",
        "s4",
        "Ingram Scholars Program applications for prospective first year students must be submitted electronically via your MyAppVU account by December 1, 2026.",
    )
    tuning = list(cases)
    cases.clear()
    case(
        "cfa-community",
        "I am a Chick-fil-A employee's dependent. What exclusion applies to Community Scholars?",
        [
            "Chick-fil-A employees and dependents/spouses of employees or Operators are not eligible."
        ],
        "cfa-community-rules",
        "s5",
        "Chick-fil-A employees and dependents/spouses of employees or Operators are not eligible to apply.",
    )
    case(
        "park",
        "Can I reuse the letters already sent to NC State, and can a parent write my Park recommendation?",
        [
            "Park cannot see NC State admission recommendations; Park-specific recommendations are needed, and parents/guardians are prohibited."
        ],
        "source-56",
        "s9",
        "permit recommendations from parents/guardians",
    )
    case(
        "ua-presidential",
        "If I miss Alabama's December 4 priority deadline, is there absolutely no possibility of automatic merit?",
        [
            "Later applications may receive funds-available consideration; do not call December 4 an absolute automatic-merit cutoff."
        ],
        "source-45",
        "s13",
        "Students who did not meet the priority deadline may be considered for scholarships on a funds available basis.",
    )
    case(
        "auburn-charter",
        "What GPA and credit requirements renew Auburn's competitive merit award?",
        [
            "Minimum cumulative unadjusted 3.0 Auburn GPA and 24 Auburn credit hours each academic year; up to eight semesters."
        ],
        "source-48",
        "s4",
        "24 Auburn credit hours earned per academic year.",
    )
    case(
        "coolidge",
        "How many reference letters do I need, and can I submit before the writers upload them?",
        [
            "Two letters; students may submit before writers upload, but all materials remain due by the scholarship deadline."
        ],
        "coolidge-faq",
        "s1",
        "Who should I choose to write my two letters of reference?",
        profile={"grade": 11, "graduation_year": 2028},
    )
    case(
        "delta-hbcu",
        "What is the bank routing number for my scholarship payment?",
        [
            "The reviewed scholarship evidence does not establish a routing number; state the evidence gap."
        ],
        "source-15",
        "s4",
        "Students must be Georgia residents",
    )
    # Exercise catalog-wide retrieval as well as explicitly selected awards.
    for c in cases[:3]:
        c.program_ids = []
    cases[
        -1
    ].expected_evidence = []  # An unsupported fact requires a gap, not an arbitrary passage.
    cases[-1].expects_evidence_gap = True
    refs = [
        evidence(
            "source-45", "s11", "UA does not use superscores for scholarship purposes."
        ),
        evidence(
            "source-48",
            "s4",
            "Automatic consideration is based on high school GPA and ACT/SAT superscore.",
        ),
    ]
    cases.append(
        EvalCase(
            id="verified-07",
            program_ids=["ua-presidential", "auburn-presidential"],
            question="Compare Alabama and Auburn: which uses ACT/SAT superscores for these freshman merit awards?",
            profile=StudentProfile(grade=12, graduation_year=2027),
            frozen_date="2026-10-14",
            expected_claims=[
                "Alabama does not use superscores; Auburn uses ACT/SAT superscores. Keep the two policies separate."
            ],
            checked_sources=refs,
            expected_evidence=[r.id for r in refs],
            critical=True,
        )
    )
    cases.append(
        EvalCase(
            id="verified-08",
            program_ids=[],
            question="What are the confirmed 2027–28 Georgia HOPE Scholarship eligibility rules?",
            expects_evidence_gap=True,
            profile=StudentProfile(grade=12, graduation_year=2027),
            frozen_date="2026-10-14",
            expected_claims=[
                "The verified corpus does not contain confirmed 2027–28 HOPE rules. State an evidence gap; do not substitute another university's scholarship rules."
            ],
            checked_sources=[],
            expected_evidence=[],
            critical=True,
        )
    )
    exposed = [c.model_copy(deep=True) for c in cases]
    for c in exposed:
        c.id = c.id.replace("verified-", "verified-exposed-")
    (ROOT / "evals/second-pass-exposed.jsonl").write_text(
        "\n".join(c.model_dump_json() for c in exposed) + "\n"
    )
    tuning.extend(exposed)
    cases.clear()
    case(
        "cfa-community",
        "I previously received a Community Scholars award. May a past recipient apply again?",
        ["No; past recipients may not reapply."],
        "cfa-community-rules",
        "s6",
        "Past recipients may not reapply.",
    )
    case(
        "park",
        "I am neither a U.S. citizen nor a permanent resident, but I will graduate from a high school in Georgia. Does Park publish an alternative citizenship/school route?",
        [
            "Graduating from a U.S.-located high school is an alternative regardless of citizenship; other Park requirements still apply."
        ],
        "source-56",
        "s4",
        "Be a United States citizen, permanent resident of the U.S., or graduating from a high school located in the U.S. (regardless of citizenship status).",
    )
    case(
        "uga-foundation-fellowship",
        "I have already matriculated at another university and would be a transfer applicant. Can I apply for the Foundation Fellowship?",
        ["Transfers and current undergraduate students are not eligible to apply."],
        "source-03",
        "s3",
        "Transfer applicants and current undergraduate students are not eligible to apply.",
    )
    case(
        "coolidge",
        "I am a junior but will graduate early in spring 2027. Can I use the 2026–27 Coolidge cycle?",
        [
            "No; current juniors must graduate in spring 2028 and start college in fall 2028."
        ],
        "source-22",
        "s1",
        "No, only high school juniors graduating in the spring of 2028 and starting college in the fall of 2028 are eligible to apply for the 2026-27 scholarship.",
        profile={"grade": 11, "graduation_year": 2027},
    )
    case(
        "georgia-southern-merit",
        "I am a Florida resident without Georgia in-state tuition status. What residency condition applies to the Fall 2027 first-year merit award?",
        [
            "This merit award requires Georgia residency and in-state tuition status; do not call a Florida resident a qualifying match."
        ],
        "source-32",
        "s5",
        "Georgia residents only\n(in-state tuition status required)",
        profile={"grade": 12, "residence": {"state": "FL"}},
    )
    cases.append(
        EvalCase(
            id="verified-06",
            program_ids=[],
            question="What are the confirmed Fall 2027 Clemson scholarship eligibility rules?",
            expects_evidence_gap=True,
            profile=StudentProfile(grade=12, residence={"state": "GA"}),
            frozen_date="2026-10-14",
            expected_claims=[
                "Clemson is deferred and not included in the verified pilot. State the coverage gap rather than substituting another institution's rules."
            ],
            critical=True,
        )
    )
    for c in cases:
        c.id = c.id.replace("verified-", "verified-heldout-v2-")
    for name, rows in (("cases.jsonl", tuning), ("heldout.jsonl", cases)):
        (ROOT / "evals" / name).write_text(
            "\n".join(c.model_dump_json() for c in rows) + "\n"
        )
    print(json.dumps({"tuning": len(tuning), "heldout": len(cases)}))


if __name__ == "__main__":
    main()
