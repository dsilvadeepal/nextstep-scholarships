import { test, expect } from "@playwright/test";
test("short intake confirms named plans before matching", async ({ page }) => {
  let submitted: Record<string, unknown> | null = null;
  await page.route("**/api/matches", (route) => {
    submitted = route.request().postDataJSON().profile;
    return route.fulfill({
      json: { corpus_version: "synthetic", scholarships: [], matches: [] },
    });
  });
  await page.goto("/");
  await page.getByRole("combobox", { name: "School year" }).selectOption("11");
  await page.getByRole("combobox", { name: "Georgia resident?" }).selectOption("yes");
  await page.getByLabel(/Tell us a little about your plans/).fill(
    "I am considering Auburn for engineering, but I have not been accepted.",
  );
  await expect(page.getByText(/Detected mentions: Auburn; engineering/)).toBeVisible();
  await page.getByRole("button", { name: "Find my matches" }).click();
  expect(submitted).toMatchObject({ prospective_colleges: [], interests: [] });
  await page.getByLabel("Use these reviewed details in my matches").check();
  await page.getByRole("button", { name: "Find my matches" }).click();
  expect(submitted).toMatchObject({
    residence: { state: "GA" },
    prospective_colleges: ["Auburn"],
    interests: ["engineering"],
  });
  expect((submitted as { context: Record<string, unknown> }).context.accepted_colleges).toBeUndefined();
});
test("skippable profile and honest unavailable catalog", async ({ page }) => {
  await page.route("**/api/matches", (route) =>
    route.fulfill({ status: 503, body: "{}" }),
  );
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Big possibilities/ }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Find my matches" }).click();
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

test("results use the shorter planning experience", async ({ page }) => {
  await page.route("**/api/matches", (route) =>
    route.fulfill({
      json: { corpus_version: "synthetic", scholarships: [], matches: [] },
    }),
  );
  await page.goto("/");
  await page.getByRole("button", { name: "Fictional senior" }).click();
  await expect(page.getByText("What if my GPA or college plans change?")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Edit details" })).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Ask about scholarships" }),
  ).toBeVisible();
});

test("chat is keyboard accessible and service failure preserves catalog", async ({
  page,
}) => {
  await page.route("**/api/matches", (r) =>
    r.fulfill({
      json: { corpus_version: "fixture", scholarships: [], matches: [] },
    }),
  );
  await page.route("**/api/chat", (r) =>
    r.fulfill({ status: 503, body: "{}" }),
  );
  await page.goto("/");
  await page.getByRole("button", { name: "Fictional junior" }).click();
  await page.getByRole("button", { name: "Ask about scholarships" }).click();
  await expect(page.getByRole("dialog")).toBeVisible();
  await page.getByLabel("Your question").fill("What can I prepare?");
  await page.getByRole("button", { name: "Ask", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("still browse");
  await page.keyboard.press("Escape");
  await expect(
    page.getByRole("button", { name: "Ask about scholarships" }),
  ).toBeFocused();
  await expect(
    page.getByRole("heading", { name: "Your scholarship starting point" }),
  ).toBeVisible();
});

test("new corpus replaces shortlist records and announces source changes", async ({
  page,
}) => {
  let n = 0;
  await page.route("**/api/matches", (r) =>
    r.fulfill({
      json: {
        corpus_version: ++n === 1 ? "old" : "new",
        scholarships: [],
        matches: [],
      },
    }),
  );
  await page.goto("/");
  await page.getByRole("button", { name: "Fictional senior" }).click();
  await page.getByRole("button", { name: "Find my matches" }).click();
  await expect(page.getByText(/Sources changed from old to new/)).toBeVisible();
});

test('cards and chat receive the same confirmed profile', async ({page}) => {
  let matched: unknown;
  let chatted: unknown;
  await page.route('**/api/matches', route => {
    matched = route.request().postDataJSON().profile;
    return route.fulfill({json:{corpus_version:'fixture',scholarships:[],matches:[]}});
  });
  await page.route('**/api/chat', route => {
    chatted = route.request().postDataJSON().profile;
    return route.fulfill({status:503,body:'{}'});
  });
  await page.goto('/');
  await page.getByLabel(/Tell us a little/).fill('I am a Georgia resident and a United States citizen. I want Georgia Tech and Kennesaw State.');
  await page.getByLabel('Use these reviewed details in my matches').check();
  await page.getByRole('button',{name:'Find my matches'}).click();
  await page.getByRole('button',{name:'Ask about scholarships'}).click();
  await page.getByLabel('Your question').fill('What should I prepare?');
  await page.getByRole('button',{name:'Ask',exact:true}).click();
  await expect(page.getByRole('alert')).toBeVisible();
  expect(chatted).toEqual(matched);
  expect(matched).toMatchObject({residence:{state:'GA'},context:{citizenship:'US citizen'}});
});
