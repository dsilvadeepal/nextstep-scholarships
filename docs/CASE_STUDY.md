# NextStep Scholarships

**Designing scholarship discovery around evidence and uncertainty**

**Role:** Product owner, working with Codex as an AI implementation partner  
**Scope:** Public course demo for Georgia high-school juniors and seniors  
[Live demo](https://nextstep-scholarships.replit.app/) · [GitHub repository](https://github.com/dsilvadeepal/nextstep-scholarships)

## The problem

A student may know their GPA, interests, and prospective colleges but still struggle to decide which scholarships deserve attention. Requirements can be spread across application pages, FAQs, and PDFs. Missing information makes a confident recommendation particularly risky.

NextStep explores a product hypothesis: a short profile, explained potential matches, visible evidence, and practical next steps can make scholarship discovery more actionable than a list of links. This hypothesis has not yet been validated through student research.

## My contribution

I owned the product direction and reviewed the experience and release scope, working with Codex on implementation and testing. My contribution centered on defining the audience, shaping the discovery journey, setting boundaries for provisional guidance, and reviewing the working demo.

AI-assisted development supported the build. The repository documents the requirements, technical design, evaluation results, and known limitations so the decisions can be inspected alongside the code.

## Key product decisions

| Decision | Reasoning |
| --- | --- |
| **Start with a short, skippable profile.** | Let students explore with the information they have. Keep additional details optional and provide fictional profiles for trying the demo. |
| **Separate eligibility checks from AI explanations.** | Use structured rules to distinguish conditions that are met, unmet, or unknown. Use retrieved evidence to support conversational explanations. |
| **Preserve the meaning of student inputs.** | Considering a college does not establish admission or enrollment. An estimated GPA does not establish the institution’s required GPA calculation. |
| **Make uncertainty actionable.** | Show unresolved conditions and source links so students know what to confirm next. Avoid invented eligibility percentages or award predictions. |
| **Keep the release focused on discovery and preparation.** | Support shortlisting, comparisons, and printable plans. Defer application automation, essay generation, and persistent student accounts. |

## What shipped

A responsive Replit-hosted demo with guided intake, grouped potential matches, cited conversation, source inspection, and printable preparation plans. The documented release contains **39 award records across 31 award families**, supported by **63 official documents**.

The system combines structured matching with retrieval-augmented generation: it retrieves relevant source passages before generating an explanation.

## Evaluation and limitations

Testing exposed a wrong-program substitution when requested scholarship evidence was missing. A coverage guard was added, and the failure became a regression case.

The historical 26-case development suite passed for both semantic and equal-weight hybrid retrieval. These were exposed tuning cases, **not an independent accuracy estimate**. The repository also preserves failures and distinguishes rescoring saved answers from running new evaluations.

The project demonstrates a working discovery flow and documented technical checks. It does not yet establish student adoption, time savings, or improved scholarship outcomes.

## Next step

Test whether students can identify an opportunity worth investigating, explain an unresolved requirement, and leave with a concrete preparation step. Use those observations to improve the experience before expanding its scope.

*Sources: [Product requirements](../PRD.md), [release status](BUILD_STATUS.md), [evaluation report](EVAL_REPORT.md).*
