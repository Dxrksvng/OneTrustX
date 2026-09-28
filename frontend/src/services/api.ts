import { registerTranslation } from "../i18n";
let sessionId = "";
try {
  sessionId = sessionStorage.getItem("timetwin-session") || crypto.randomUUID();
  sessionStorage.setItem("timetwin-session", sessionId);
} catch {
  sessionId = crypto.randomUUID();
}

export async function api(path: string, body?: unknown) {
  // Vercel cannot reach a developer's local tunnel reliably. Set
  // VITE_API_BASE_URL to the deployed API origin (including /api) for
  // production builds; local development keeps using Vite's /api proxy.
  const apiBase = (import.meta.env.VITE_API_BASE_URL || "/api").replace(/\/$/, "");
  const response = await fetch(apiBase + path, {
    method: body === undefined ? "GET" : "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Demo-Role": "AIRPORT_OPERATOR",
      "X-Demo-Session": sessionId,
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Service unavailable" }));
    throw new Error(
      typeof error.detail === "string"
        ? error.detail
        : JSON.stringify(error.detail),
    );
  }
  const data = await response.json();
  if (data.answer && data.answer_th)
    registerTranslation(data.answer, data.answer_th);
  return data;
}
