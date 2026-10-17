import { test, expect } from "@playwright/test";
test("anonymous admin sees sign in boundary and never requests runs", async ({
  page,
}) => {
  let reads = 0;
  await page.route("**/api/auth/status", (r) =>
    r.fulfill({ json: { configured: false, authenticated: false } }),
  );
  await page.route("**/api/admin/**", (r) => {
    reads++;
    return r.fulfill({ status: 401, body: "{}" });
  });
  await page.goto("/?admin=1");
  await expect(page.getByText("Admin sign-in is not configured")).toBeVisible();
  expect(reads).toBe(0);
});
test("saved completed cases are inspected without replay after refresh", async ({
  page,
}) => {
  let executions = 0;
  const config = {
    corpus_version: "fixture-v",
    cases: ["one"],
    methods: ["semantic", "hybrid"],
    split: "tuning",
    suite_hash: "fixture-only",
  };
  const run = {
    id: "run1",
    status: "active",
    config,
    results: [
      {
        case_id: "one",
        method: "semantic",
        status: "completed",
        result: {
          scores: { passed: true, support_rate: null, checked_claims: 0 },
          expected: { expected_claims: ["Fixture"], expected_evidence: [] },
        },
      },
    ],
    historical: true,
  };
  await page.route("**/api/auth/status", (r) =>
    r.fulfill({ json: { configured: true, authenticated: true } }),
  );
  await page.route("**/api/admin/runs", (r) =>
    r.fulfill({ json: [{ id: "run1", status: "active", config }] }),
  );
  await page.route("**/api/admin/runs/run1", (r) => r.fulfill({ json: run }));
  await page.route("**/api/admin/ingestion", (r) =>
    r.fulfill({ json: { reports: [] } }),
  );
  await page.route("**/api/admin/runs/run1/cases/**", (r) => {
    executions++;
    return r.fulfill({ json: {} });
  });
  await page.goto("/?admin=1");
  await page.getByRole("button", { name: /Inspect run1/ }).click();
  await expect(page.getByText(/Historical corpus/)).toBeVisible();
  await page.getByText("one · semantic · completed").click();
  await expect(page.getByText(/Expected claims/)).toBeVisible();
  await page.reload();
  await page.getByRole("button", { name: /Inspect run1/ }).click();
  expect(executions).toBe(0);
});
