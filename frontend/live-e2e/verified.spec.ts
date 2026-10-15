import { test, expect } from "@playwright/test";

const version = "verified-2026-10-14-v2";

test("actual verified corpus, cited live answer and printed plan", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByRole("combobox", { name: "School year", exact: true })
    .selectOption("12");
  const matches = page.waitForResponse("**/api/matches");
  await page.getByRole("button", { name: "Explore scholarships" }).click();
  const catalog = await (await matches).json();
  expect(catalog.corpus_version).toBe(version);
  expect(catalog.scholarships).toHaveLength(18);
  const card = page
    .getByRole("article")
    .filter({
      has: page.getByRole("heading", {
        name: "Chick-fil-A Community Scholars",
        exact: true,
      }),
    });
  await expect(card).toBeVisible();
  await card
    .getByText("Requirements, checklist & sources", { exact: true })
    .click();
  await expect(
    card.getByText(/Be 18 years of age by July 15, 2027/).first(),
  ).toBeVisible();
  await expect(
    card.getByText(/Cycle 2027–2028 academic year/).first(),
  ).toBeVisible();
  await card.getByRole("button", { name: "+ Add to my plan" }).click();
  await page.getByRole("button", { name: "Ask about scholarships" }).click();
  await page
    .getByLabel("Your question")
    .fill("What is the minimum age for Community Scholars in 2027?");
  const chat = page.waitForResponse("**/api/chat");
  await page.getByRole("button", { name: "Ask", exact: true }).click();
  const response = await chat;
  expect(response.status()).toBe(200);
  const answer = await response.json();
  expect(answer.corpus_version).toBe(version);
  expect(
    answer.blocks.map((b: { text: string }) => b.text).join(" "),
  ).toContain("18 years of age by July 15, 2027");
  expect(
    answer.evidence.chunks.every(
      (c: { corpus_version: string; program_id: string }) =>
        c.corpus_version === version && c.program_id === "cfa-community",
    ),
  ).toBe(true);
  await page
    .locator("dialog summary")
    .filter({ hasText: "Source:" })
    .first()
    .click();
  await expect(
    page
      .locator(
        'dialog a[href="https://scholarshipamerica.org/scholarship/cfacommunityscholars/"]',
      )
      .first(),
  ).toBeVisible();
  await page.screenshot({
    path: `/tmp/nextstep-verified-chat-${test.info().project.name}.png`,
    fullPage: true,
  });
  await page.keyboard.press("Escape");
  expect(await page.evaluate(() => Object.keys(localStorage))).toEqual([]);
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.emulateMedia({ media: "print" });
  await expect(page.getByText("My next steps", { exact: true })).toBeVisible();
  await page.pdf({
    path: `/tmp/nextstep-verified-plan-${test.info().project.name}.pdf`,
    format: "A4",
  });
});

test("actual API preserves unknowns, rejects old programs and pins coverage gaps", async ({
  request,
}) => {
  const response = await request.post("/api/matches", {
    data: {
      profile: {
        grade: 12,
        graduation_year: 2027,
        residence: { state: "FL" },
        prospective_colleges: ["Morehouse College"],
      },
    },
  });
  expect(response.status()).toBe(200);
  const catalog = await response.json();
  expect(catalog.corpus_version).toBe(version);
  expect(
    catalog.matches.find(
      (m: { scholarship_id: string }) => m.scholarship_id === "delta-hbcu",
    ).group,
  ).toBe("unmet");
  expect(
    catalog.matches.find(
      (m: { scholarship_id: string }) =>
        m.scholarship_id === "georgia-southern-merit",
    ).group,
  ).toBe("unmet");
  expect(
    catalog.matches.find(
      (m: { scholarship_id: string }) => m.scholarship_id === "coca-cola",
    ).timing,
  ).toBe("closed");
  const invalid = await request.post("/api/chat", {
    data: {
      profile: {},
      request: {
        question: "Rules?",
        program_ids: ["georgias-own"],
        corpus_version: "live-2026-10-14-reviewed-v6",
      },
    },
  });
  expect(invalid.status()).toBe(422);
  const gap = await request.post("/api/chat", {
    data: {
      profile: {},
      request: {
        question: "What are the confirmed 2027–28 HOPE Scholarship rules?",
        corpus_version: "live-2026-10-14-reviewed-v6",
      },
    },
  });
  expect(gap.status()).toBe(200);
  const body = await gap.json();
  expect(body.corpus_version).toBe(version);
  expect(body.blocks).toEqual([]);
  expect(body.gaps.join(" ")).toContain("not in this verified corpus");
  expect((await request.get("/api/admin/runs")).status()).toBe(401);
});
