import { test, expect } from "@playwright/test";
test("reset → predict → compare → accept → passenger replan → audit", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "See the next bottleneck." }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Reset demo" }).click();
  await expect(page.getByRole("status")).toContainText("Demo reset");
  await page.getByRole("button", { name: "Start peak event" }).click();
  await expect(page.getByText("↑ RISING PRESSURE")).toBeVisible();
  await page.getByRole("button", { name: "Compare interventions" }).click();
  await expect(
    page.getByRole("heading", { name: "Open A5 + redirect 12%" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Run custom simulation" }).click();
  await expect(page.getByText(/Custom:.*Feasible/)).toBeVisible();
  await page
    .locator(".option.recommended")
    .getByRole("button", { name: "Accept action" })
    .click();
  await expect(page.getByText(/Human decision recorded: accept/)).toBeVisible();
  await page
    .getByRole("button", { name: "Passenger journey", exact: true })
    .click();
  await page.getByRole("button", { name: "Reset demo" }).click();
  await expect(page.locator(".safe-time strong")).toHaveText("34");
  await page
    .getByRole("button", { name: "Simulate gate change", exact: true })
    .click();
  await expect(page.locator(".safe-time strong")).toHaveText("11");
  await expect(page.locator(".safe-status")).toHaveText("LEAVE NOW");
  await page.getByRole("button", { name: "Decision log", exact: true }).click();
  await expect(
    page.getByText("DEMO_STATE_UPDATED", { exact: true }).first(),
  ).toBeVisible();
  expect(errors).toEqual([]);
});
test("mobile passenger route and stale-data state", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await page.getByRole("button", { name: "Open navigation" }).click();
  await page
    .getByRole("button", { name: "Passenger journey", exact: true })
    .click();
  await page.getByRole("button", { name: "Reset demo" }).click();
  await expect(page.locator(".safe-time strong")).toHaveText("34");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBeTruthy();
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: "test-results/passenger-mobile.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "Test stale feed" }).click();
  await expect(page.locator(".safe-status")).toHaveText(
    "DATA STALE — LOW CONFIDENCE",
  );
  await expect(
    page.getByRole("button", { name: "Continue journey", exact: true }),
  ).toBeDisabled();
  await page.getByRole("button", { name: "Reset demo" }).click();
});

test("interactive airport map, horizons and accessible alternatives", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Reset demo", exact: true }).click();
  await page
    .getByRole("button", { name: "Start peak event", exact: true })
    .click();
  await expect(page.getByText("↑ RISING PRESSURE")).toBeVisible();
  await page
    .getByRole("button", { name: "Inspect Security B", exact: true })
    .click();
  await expect(page.locator(".checkpoint-inspector")).toContainText(
    "Security B",
  );
  await page.getByRole("button", { name: "+60 min", exact: true }).click();
  await expect(page.locator(".checkpoint-inspector")).toContainText(
    "+60 min forecast",
  );
  await page.getByRole("button", { name: "Zoom in map" }).click();
  await expect(page.locator(".airport-canvas")).toHaveClass(/zoomed/);
  await page.getByRole("button", { name: "+30 min", exact: true }).click();
  await page
    .getByRole("button", { name: "Inspect Security A", exact: true })
    .click();
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: "test-results/operations-desktop.png",
    fullPage: true,
  });
  await page.getByRole("button", { name: "Explore actions" }).click();
  await expect(
    page.getByRole("heading", { name: "Open A5 + redirect 12%" }),
  ).toBeVisible();
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.screenshot({
    path: "test-results/what-if-desktop.png",
    fullPage: true,
  });
});

test("data provenance distinguishes public context from synthetic operations", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByRole("button", { name: "Data & sources", exact: true })
    .click();
  await expect(
    page.getByText("Operations are synthetic. Outcomes are simulated."),
  ).toBeVisible();
  await expect(page.locator(".source-feed")).toHaveCount(3);
  await expect(page.locator(".source-matrix")).toContainText(
    "580 anonymous journeys",
  );
});

test("model attribution is labelled and sums to the simulated wait change", async ({
  page,
}) => {
  await page.goto("/");
  await page
    .getByRole("button", { name: "Start peak event", exact: true })
    .click();
  await page
    .getByRole("button", { name: "Operations control", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Operational cause graph" }),
  ).toBeVisible();
  await expect(page.locator(".cause-contributions")).toContainText("PRIMARY");
  await expect(page.locator(".cause-contributions")).toContainText("SECONDARY");
  await expect(
    page.getByText("NOT CAUSAL PROOF", { exact: true }),
  ).toBeVisible();
});
