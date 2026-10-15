import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import { applyScenario } from "../scenarios";
import { PrintPlan } from "../components/PrintPlan";
import type { components } from "../types";

test("scenario keeps original profile and nested values intact", () => {
  const original = {
    grade: 11 as const,
    graduation_year: null,
    gpa: null,
    prospective_colleges: ["UGA"],
  };
  const next = applyScenario(original, { grade: 12 });
  next.prospective_colleges?.push("Other");
  expect(original.grade).toBe(11);
  expect(original.prospective_colleges).toEqual(["UGA"]);
  expect(next.grade).toBe(12);
});
test("print labels hypothetical state and dated source limitations", () => {
  render(
    <PrintPlan
      scholarships={[]}
      matches={[]}
      hypothetical={true}
      generatedAt="2026-10-14"
    />,
  );
  expect(screen.getByText(/Hypothetical/)).toBeVisible();
  expect(screen.getByText(/2026-10-14/)).toBeVisible();
  expect(screen.getByText(/Select scholarships/)).toBeVisible();
});

test("print deduplicates long source excerpts while retaining document sections", () => {
  const ref = {
    id: "a",
    source_id: "official",
    document_version: "hash-version",
    section_id: "s1",
    page: null,
    title: "Official rules",
    cycle: null,
    quote: "Long repeated source quote",
    start: 0,
    end: 26,
    url: "https://example.org/rules",
    fetched_at: "2026-10-14T12:00:00Z",
  };
  const scholarship: components["schemas"]["Scholarship"] = {
    id: "award",
    corpus_version: "v",
    name: "Reviewed award",
    sponsor: null,
    scope: null,
    cycle: null,
    source_checked_at: null,
    deadline: null,
    opens: null,
    timezone: null,
    date_precision: null,
    official_url: ref.url,
    information_status: "source_checked",
    evidence: [ref, { ...ref, id: "b", section_id: "s2" }],
  };
  render(
    <PrintPlan
      scholarships={[scholarship]}
      matches={[]}
      hypothetical={false}
      generatedAt="2026-10-14"
    />,
  );
  expect(screen.getAllByRole("link", { name: ref.url })).toHaveLength(1);
  expect(screen.getByText(/Sections: s1, s2/)).toBeVisible();
  expect(screen.queryByText(ref.quote)).not.toBeInTheDocument();
});
