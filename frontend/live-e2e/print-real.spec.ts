import { test, expect } from "@playwright/test";

test("real plan keeps a compact checklist and unique official sources", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByRole("combobox", { name: "School year", exact: true })
    .selectOption("12");
  await page.getByRole("button", { name: "Explore scholarships" }).click();
  const card = page
    .getByRole("article")
    .filter({
      has: page.getByRole("heading", {
        name: "Chick-fil-A Community Scholars",
        exact: true,
      }),
    });
  await card.getByRole("button", { name: "+ Add to my plan" }).click();
  await page.emulateMedia({ media: "print" });
  const plan = page.locator(".print-plan");
  await expect(
    plan.getByRole("heading", { name: "Chick-fil-A Community Scholars" }),
  ).toBeVisible();
  await expect(plan.getByRole("link")).toHaveCount(2);
  await expect(plan.getByText(/age 18 by July 15, 2027/)).toBeVisible();
  await page.pdf({
    path: `/tmp/nextstep-verified-plan-${test.info().project.name}.pdf`,
    format: "A4",
  });
  await page.screenshot({
    path: `/tmp/nextstep-verified-print-${test.info().project.name}.png`,
    fullPage: true,
  });
});
