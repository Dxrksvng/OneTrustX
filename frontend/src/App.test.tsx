// @vitest-environment jsdom
import { afterEach, expect, test, vi } from "vitest";
import { cleanup, render, screen, fireEvent } from "@testing-library/react";
import App from "./App";
import { api } from "./services/api";
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});
test("main dashboard has a useful loading and failure state", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockRejectedValue(new Error("Feed unavailable")),
  );
  render(<App />);
  expect(screen.getByText("Airport TimeTwin")).toBeTruthy();
  expect(await screen.findByText("Feed unavailable")).toBeTruthy();
  fireEvent.click(screen.getByRole("button", { name: "Retry connection" }));
  expect(fetch).toHaveBeenCalled();
});
test("API uses demo role and propagates validation errors", async () => {
  const fetcher = vi.fn().mockResolvedValue({
    ok: false,
    json: async () => ({ detail: "DATA STALE" }),
  });
  vi.stubGlobal("fetch", fetcher);
  await expect(api("/simulation", { lanes: 5 })).rejects.toThrow("DATA STALE");
  expect(fetcher.mock.calls[0][1].headers["X-Demo-Role"]).toBe(
    "AIRPORT_OPERATOR",
  );
});
