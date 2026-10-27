import {
  CitizenProfile,
  MultiAgentWorkflowResponse,
  SchemeRecommendation,
  SimplifiedSchemeOutput,
  SupportedLanguage,
  SchemeDetail
} from "./types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

export async function checkHealth() {
  const res = await fetch(`${BASE_URL}/api/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function fetchDatasetStatus() {
  const res = await fetch(`${BASE_URL}/api/dataset/status`);
  if (!res.ok) throw new Error("Failed to fetch dataset status");
  return res.json();
}

export async function fetchSupportedLanguages(): Promise<SupportedLanguage[]> {
  const res = await fetch(`${BASE_URL}/api/languages`);
  if (!res.ok) throw new Error("Failed to fetch languages");
  return res.json();
}

export async function sendChatMessage(
  sessionId: string,
  message: string,
  language: string = "en",
  profileOverride?: CitizenProfile
): Promise<MultiAgentWorkflowResponse> {
  const res = await fetch(`${BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      language,
      profile_override: profileOverride,
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || "Error communicating with AI agents");
  }
  return res.json();
}

export async function resetSession(sessionId: string) {
  const res = await fetch(`${BASE_URL}/api/session/reset`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
  if (!res.ok) throw new Error("Failed to reset session");
  return res.json();
}

export async function localizeRecommendations(
  sessionId: string,
  language: string,
  schemeIds: string[]
): Promise<SimplifiedSchemeOutput[]> {
  const res = await fetch(`${BASE_URL}/api/localize-recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      language,
      scheme_ids: schemeIds,
    }),
  });
  if (!res.ok) throw new Error("Failed to localize recommendations");
  return res.json();
}

export async function searchSchemes(params: {
  query?: string;
  state?: string;
  category?: string;
  benefit_type?: string;
  limit?: number;
  offset?: number;
}) {
  const searchParams = new URLSearchParams();
  if (params.query) searchParams.append("query", params.query);
  if (params.state) searchParams.append("state", params.state);
  if (params.category) searchParams.append("category", params.category);
  if (params.benefit_type) searchParams.append("benefit_type", params.benefit_type);
  searchParams.append("limit", String(params.limit || 20));
  searchParams.append("offset", String(params.offset || 0));

  const res = await fetch(`${BASE_URL}/api/schemes?${searchParams.toString()}`);
  if (!res.ok) throw new Error("Failed to search schemes");
  return res.json();
}

export async function fetchSchemeDetail(schemeId: string): Promise<SchemeDetail> {
  const res = await fetch(`${BASE_URL}/api/schemes/${encodeURIComponent(schemeId)}`);
  if (!res.ok) throw new Error(`Failed to load details for scheme: ${schemeId}`);
  return res.json();
}
