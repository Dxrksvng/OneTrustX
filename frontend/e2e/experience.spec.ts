import { test, expect } from "@playwright/test";
const routes = [
  "/",
  "/overview",
  "/future",
  "/operations",
  "/simulator",
  "/flights",
  "/passenger-flow",
  "/journey",
  "/performance",
  "/sources",
  "/app/audit",
  "/demo",
  "/integration",
];
test("all routes render without browser or API errors", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  page.on("response", (r) => {
    if (r.url().includes("/api/") && r.status() >= 400)
      errors.push(r.status() + " " + r.url());
  });
  for (const path of routes) {
    await page.goto(path);
    await expect(page.locator("h1").first()).toBeVisible();
    await expect(page.locator("body")).not.toContainText(
      "Internal Server Error",
    );
  }
  expect(errors).toEqual([]);
});
test("Thai / English persists across every route and reload", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "ไทย", exact: true }).click();
  for (const path of routes) {
    await page.goto(path);
    await expect(page.locator("html")).toHaveAttribute("lang", "th");
    await expect(page.locator("h1").first()).toContainText(/[ก-๙]/);
  }
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("lang", "th");
  await page.getByRole("button", { name: "English", exact: true }).click();
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
});
test("mobile pages retain layout and reduced motion", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  for (const route of ["/", "/overview", "/journey", "/demo", "/sources"]) {
    await page.goto(route);
    await expect(page.locator("h1").first()).toBeVisible();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
      route,
    ).toBeTruthy();
  }
});
test("real cached data is separated from modelled flights", async ({
  page,
}) => {
  await page.goto("/sources");
  await expect(page.locator(".public-context")).toContainText("504,884");
  await page
    .locator(".public-context summary")
    .filter({ hasText: "BTS" })
    .click();
  await expect(page.locator(".public-context")).toContainText("US");
  await page.goto("/flights");
  await expect(page.locator(".data-table")).toContainText("DEMO401");
  await expect(page.locator(".data-table")).toContainText("SIN");
  await page.getByRole("button", { name: "View DEMO401", exact: true }).click();
  await expect(page.locator(".flight-drawer")).toBeVisible();
});
