# Source inspection — October 14, 2026

> Historical evidence: dated checkpoints below are not current setup instructions. The published release is summarized in [build status](BUILD_STATUS.md). Local artifact paths are evidence references, not files distributed with this repository.


16 public candidate documents were downloaded and parsed; **this is not 16 verified scholarships**. No paid extraction, embeddings or real answer generation has run. Source register: `data/sources.yaml`; original/normalized files and processing report: ignored `artifacts/`. Download hashes and fetch times are recorded in `artifacts/reports/collection.json`.

| Category | Documents | Inspection outcome |
|---|---:|---|
| State | 2 | HOPE/regulation landing pages are discovery leads, not complete rulebooks. Follow linked regulations before claiming complete coverage. |
| Institutional | 2 | UGA redirect lands on a general aid page; Georgia Tech is an aid overview. Individual award conditions remain incomplete. |
| Foundation | 3 | Atlanta page contains multiple programs. Central Georgia is an application gateway. Jones County PDF is a real multi-award table requiring program partitioning and footnote review. |
| Utility | 1 | Amicalola is an award announcement; it does not establish complete current application rules. |
| Credit union | 3 | Delta annual/HBCU pages contain useful eligibility/FAQ evidence. Georgia's Own PDF is explicitly 2025 and must remain historical. |
| Employer/family | 2 | Chick-fil-A overview and criteria overlap. Criteria contain distinct $1,500/$25,000 awards and shared rules; mixed sections must be partitioned before publication. |
| Corporate | 2 | Coca-Cola has eligibility exclusions and a closed application notice. Chick-fil-A community page is a separate program, not the team-member award. |
| National | 1 | Coolidge overview supports junior timing and senior exclusion; it does not establish an exact next deadline. |

Representative checks completed:

- HTML: Coolidge's junior/senior distinction checked against downloaded original HTML and normalized text.
- Multi-program HTML: Chick-fil-A criteria distinguish GPA thresholds and the larger award's employment-tenure requirement. Unspecified weighted/unweighted type remains unknown. Older cycle headings coexist with forward-looking terms; no automatic date rollover.
- Text PDF: Georgia's Own page 1 visually inspected at `/tmp/nextstep-georgias-own.png`; 2025 title, membership/age/grade/major restrictions and June 13, 2025 deadline are present.
- Table PDF: Jones County page 1 visually inspected at `/tmp/nextstep-jones-county.png`. Rows have award-specific purpose/GPA, a cumulative-GPA footnote and an application window without an explicit year on that page. Layout extraction is not certification of column relationships. Full page text is retained; inferred tables carry warnings.
- Incomplete leads: institutional/state gateways and utility announcement cannot supply complete eligibility merely because parsing succeeded.

15 short reference excerpts were compared with downloaded originals, including PDF text extraction, to prepare 24 fictional evaluation cases. This is bounded reference checking, not a full audit of all source content. The heldout set has not been run against a model.

Remaining source work depends on the first live extraction: inspect generated partitions/conditions, resolve aliases and conflicts, follow discovery links where the initial extraction establishes gaps, and expand geographically. Collection is not exhaustive; no arbitrary program-count cap is being claimed.
