// All backend calls go to a relative "/api" URL.
// Locally, Vite forwards it to FastAPI; in Docker, nginx does.

export async function predictChurn(customer) {
  let response;
  try {
    response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(customer),
    });
  } catch {
    throw new Error("Cannot reach the server. Is the backend running?");
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    // 422 = validation error from FastAPI: show which fields are wrong
    if (response.status === 422 && Array.isArray(data.detail)) {
      const fields = data.detail.map((err) => err.loc.at(-1)).join(", ");
      throw new Error(`Invalid values for: ${fields}`);
    }
    throw new Error(data.detail || `Server error (${response.status})`);
  }
  return data;
}
