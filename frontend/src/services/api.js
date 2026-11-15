const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "").replace(/\/$/, "");
const ASSISTANT_BASE_URL = (import.meta.env.VITE_ASSISTANT_API_URL || "/assistant-api").replace(/\/$/, "");

async function request(path, options, baseUrl = API_BASE_URL, serviceName = "TerraTwin API") {
  let response;

  try {
    response = await fetch(`${baseUrl}${path}`, {
      headers: { Accept: "application/json", ...options?.headers },
      ...options,
    });
  } catch {
    throw new Error(`Cannot reach the ${serviceName}. Check that its server is running.`);
  }

  const payload = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = payload.detail;
    throw new Error(
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? detail.map((issue) => issue.msg).filter(Boolean).join("; ")
        : payload.message || `TerraTwin API returned HTTP ${response.status}.`,
    );
  }

  return payload;
}

export const api = {
  health: () => request("/health"),
  planets: () => request("/api/planets/"),
  locations: (planet) => request(`/api/locations/planet/${encodeURIComponent(planet)}`),
  datasets: () => request("/api/datasets/"),
  earthCandidates: () => request("/api/analyze/earth-candidates"),
  assistantHealth: () => request("/health", undefined, ASSISTANT_BASE_URL, "TerraTwin AI service"),
  assistantChat: (message, history = []) => request("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  }, ASSISTANT_BASE_URL, "TerraTwin AI service"),
  compare: (targetPlanet, targetLocation) =>
    request("/api/analyze/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        target_planet: targetPlanet,
        target_location: targetLocation,
      }),
    }),
};
