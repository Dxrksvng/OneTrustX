export async function api(path: string, body?: unknown) {
  const response = await fetch("/api" + path, {
    method: body === undefined ? "GET" : "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Demo-Role": "AIRPORT_OPERATOR",
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
  return response.json();
}
