import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import { applyScenario } from "../scenarios";
import { PrintPlan } from "../components/PrintPlan";

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
