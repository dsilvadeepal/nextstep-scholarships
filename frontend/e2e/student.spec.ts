import { test, expect } from "@playwright/test";
test("skippable profile and honest unavailable catalog", async ({ page }) => {
  await page.route("**/api/matches", (route) =>
    route.fulfill({ status: 503, body: "{}" }),
  );
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Big possibilities/ }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Explore scholarships" }).click();
  await expect(page.getByRole("alert")).toContainText("not available");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  expect(await page.evaluate(() => Object.keys(localStorage))).toEqual([]);
  await page.screenshot({
    path: `/tmp/nextstep-${test.info().project.name}.png`,
    fullPage: true,
  });
});

test("failed reset preserves the label of displayed hypothetical results", async ({
  page,
}) => {
  let calls = 0;
  await page.route("**/api/matches", (route) => {
    calls++;
    return calls === 3
      ? route.fulfill({ status: 503, body: "{}" })
      : route.fulfill({
          json: { corpus_version: "synthetic", scholarships: [], matches: [] },
        });
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Fictional senior" }).click();
  await page.getByText("What if my GPA or college plans change?").click();
  await page.getByRole("button", { name: "Try scenario" }).click();
  await expect(
    page.getByText(
      "Hypothetical results — your original profile is preserved.",
    ),
  ).toBeVisible();
  await page.getByRole("button", { name: "Restore original profile" }).click();
  await expect(page.getByRole("alert")).toBeVisible();
  await expect(
    page.getByText(
      "Hypothetical results — your original profile is preserved.",
    ),
  ).toBeVisible();
});

test("late scenario response cannot replace restored original results", async ({
  page,
}) => {
  let calls = 0;
  let pending: import("@playwright/test").Route | undefined;
  const payload = (name: string) => ({
    corpus_version: "synthetic",
    scholarships: [
      {
        id: "a",
        name,
        information_status: "incomplete",
        materials: [],
        evidence: [],
      },
    ],
    matches: [
      {
        scholarship_id: "a",
        group: "matches",
        fit: "Potential match",
        timing: "unknown",
        evidence_label: "incomplete",
        conditions: [],
        followups: [],
      },
    ],
  });
  await page.route("**/api/matches", (route) => {
    calls++;
    if (calls === 2) {
      pending = route;
      return;
    }
    return route.fulfill({ json: payload("Original award") });
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Fictional senior" }).click();
  await expect(
    page.getByRole("heading", { name: "Original award" }),
  ).toBeVisible();
  await page.getByText("What if my GPA or college plans change?").click();
  await page.getByRole("button", { name: "Try scenario" }).click();
  await expect.poll(() => Boolean(pending)).toBe(true);
  await page.getByRole("button", { name: "Restore original profile" }).click();
  await expect(page.getByRole("status")).toHaveCount(0);
  const responseArrived = page.waitForResponse((response) =>
    response.url().endsWith("/api/matches"),
  );
  await pending!.fulfill({ json: payload("Obsolete scenario award") });
  await responseArrived;
  await expect(
    page.getByRole("heading", { name: "Original award" }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Obsolete scenario award" }),
  ).toHaveCount(0);
});
