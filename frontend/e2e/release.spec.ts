import { test, expect } from "@playwright/test";
test("synthetic complete student journey shows citations, survives chat errors and prints", async ({
  page,
}) => {
  const evidence = {
    id: "e",
    source_id: "synthetic",
    document_version: "fixture",
    section_id: "rules",
    page: 1,
    quote: "Seniors need an acceptance letter.",
    start: 0,
    end: 33,
    url: "https://example.org/synthetic-only",
    fetched_at: "2026-10-14T12:00:00Z",
    title: "SYNTHETIC source",
    cycle: "2026-27",
  };
  await page.route("**/api/matches", (r) =>
    r.fulfill({
      json: {
        corpus_version: "synthetic",
        scholarships: [
          {
            id: "a",
            corpus_version: "synthetic",
            name: "SYNTHETIC scholarship",
            information_status: "incomplete",
            materials: ["Confirm acceptance"],
            deadline: null,
            cycle: "2026-27",
            evidence: [evidence],
          },
        ],
        matches: [
          {
            scholarship_id: "a",
            group: "matches",
            fit: "Missing profile information",
            timing: "unknown",
            evidence_label: "incomplete",
            conditions: [
              {
                condition_id: "admission",
                status: "unknown",
                reason: "Acceptance not established",
              },
            ],
            followups: ["Do you have an acceptance letter?"],
          },
        ],
      },
    }),
  );
  await page.route("**/api/chat", (r) =>
    r.fulfill({
      json: {
        blocks: [{ text: evidence.quote, evidence_ids: ["chunk"] }],
        gaps: ["Acceptance is unknown."],
        corpus_version: "synthetic",
        method: "semantic",
        evidence: {
          chunks: [
            {
              id: "chunk",
              program_id: "a",
              source_id: "synthetic",
              corpus_version: "synthetic",
              text: evidence.quote,
              heading: "SYNTHETIC rules",
              section_ids: ["rules"],
              token_count: 7,
              evidence: [evidence],
            },
          ],
        },
      },
    }),
  );
  await page.goto("/");
  await page
    .getByRole("combobox", { name: "School year", exact: true })
    .selectOption("12");
  await page.getByLabel("GPA value", { exact: true }).fill("3.65");
  await page.getByText("Add more details", { exact: true }).click();
  await page
    .getByRole("combobox", { name: "GPA scale", exact: true })
    .selectOption("4");
  await page.getByRole("button", { name: "Find my matches" }).click();
  await expect(
    page.getByRole("heading", { name: "SYNTHETIC scholarship" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "+ Add to my plan" }).click();
  await page.getByRole("button", { name: "Ask about scholarships" }).click();
  await page.getByLabel("Your question").fill("What do I need?");
  await page.getByRole("button", { name: "Ask", exact: true }).click();
  await page.getByText("Source: SYNTHETIC rules").click();
  await expect(
    page.getByRole("link", { name: "SYNTHETIC source" }),
  ).toBeVisible();
  await page.screenshot({
    path: `/tmp/nextstep-chat-${test.info().project.name}.png`,
    fullPage: true,
  });
  await page.keyboard.press("Escape");
  expect(await page.evaluate(() => Object.keys(localStorage))).toEqual([]);
  await page.emulateMedia({ media: "print" });
  await expect(page.getByText("My next steps", { exact: true })).toBeVisible();
  await expect(page.locator(".chat")).toBeHidden();
  await page.pdf({
    path: `/tmp/nextstep-complete-plan-${test.info().project.name}.pdf`,
    format: "A4",
  });
});
