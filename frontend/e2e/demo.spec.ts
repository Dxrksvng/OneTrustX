import { test, expect, type Page } from "@playwright/test";
async function event(page: Page, name: string) {
  await page.getByRole("button", { name: "DEMO MODE", exact: false }).click();
  await page
    .locator(".demo-mode-dialog")
    .getByRole("button", { name, exact: true })
    .click();
  await page.keyboard.press("Escape");
}
test("fresh → compare → human approval → measured lifecycle → gate replan", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/overview");
  await expect(page.locator(".metrics")).toContainText("12");
  await event(page, "Reset demo");
  await event(page, "Start peak event");
  await page.goto("/simulator");
  await expect(page.locator(".strategy-comparison")).toContainText("Baseline");
  await page
    .getByRole("button", { name: "Submit recommendation", exact: true })
    .click();
  await expect(page.getByText(/Human decision recorded: accept/)).toBeVisible();
  await page.goto("/app/audit");
  await expect(page.locator(".decision-history")).toContainText("accept");
  const before = await page.locator(".decision-history").innerText();
  await page.reload();
  await expect(page.locator(".decision-history")).toHaveText(before, {
    useInnerText: true,
  });
  await page.goto("/journey");
  await event(page, "Reset demo");
  await expect(page.locator(".safe-time strong")).toHaveText("34");
  await event(page, "Gate C8 → E7");
  await expect(page.locator(".safe-time strong")).toHaveText("11");
  expect(errors).toEqual([]);
});
test("stale is optional and refresh restores action", async ({ page }) => {
  await page.goto("/overview");
  await event(page, "Test stale feed");
  await expect(
    page.getByText("Forecast paused", { exact: true }),
  ).toBeVisible();
  await expect(page.locator(".metrics")).not.toBeVisible();
  await page
    .getByRole("button", { name: "Refresh feed", exact: true })
    .first()
    .click();
  await expect(page.locator(".metrics")).toBeVisible();
});
test("projector story requires explicit approval and completes measurement", async ({
  page,
}) => {
  await page.goto("/demo");
  await page
    .getByRole("button", { name: "Start / restart guided demo" })
    .click();
  for (let i = 0; i < 4; i++)
    await page.getByRole("button", { name: "Next step", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Approve demo intervention" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Approve demo intervention" }).click();
  for (let i = 0; i < 3; i++)
    await page.getByRole("button", { name: "Next step", exact: true }).click();
  await expect(page.locator(".story-stage")).toContainText(
    "Observed simulated mean",
  );
  await expect(page.locator(".story-stage")).toContainText("Forecast error");
});
