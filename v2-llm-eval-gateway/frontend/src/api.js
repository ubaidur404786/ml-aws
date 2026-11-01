// All calls to the FastAPI backend. Relative URLs, so the same build works locally and on AWS.

// Example: readError(response) -> "Daily question limit reached. Please try again tomorrow."
async function readError(response) {
  try {
    const data = await response.json();
    return typeof data.detail === "string" ? data.detail : `Request failed (HTTP ${response.status})`;
  } catch {
    return `Request failed (HTTP ${response.status})`;
  }
}

// Example: askQuestion("How long does shipping take?")
//   -> {answer: "3 to 5 business days.", sources: ["shipping_guide.pdf p.1"], model: "amazon.nova-micro-v1:0", latency_ms: 640, ...}
export async function askQuestion(question) {
  const response = await fetch("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

// Example: adminApi("secret", "GET", "/admin/settings") -> {active_model: "...", max_tokens: 300, ...}
//          adminApi("wrong", "GET", "/admin/settings") -> throws Error("Wrong admin password")
export async function adminApi(password, method, path, body) {
  const response = await fetch(path, {
    method,
    headers: { "Content-Type": "application/json", "X-Admin-Password": password },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

// Example: shortModel("amazon.nova-micro-v1:0") -> "Nova Micro"
export function shortModel(modelId) {
  const name = modelId.replace("amazon.", "").replace(/-v\d+:\d+$/, "");
  return name.split("-").map((word) => word[0].toUpperCase() + word.slice(1)).join(" ");
}
