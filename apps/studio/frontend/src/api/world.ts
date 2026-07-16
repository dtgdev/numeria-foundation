export interface RegionDraft {
  name: string;
  world_id: string;
  domain: string;
  summary: string;
  educational_mission: string;
  themes: string[];
  atmosphere: string[];
  landmark_ideas: string[];
}

export interface RegionValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  proposed_id: string | null;
  proposed_path: string | null;
}

export interface PublishedRegion {
  id: string;
  name: string;
  world_id: string;
  path: string;
  message: string;
}

const API_BASE_URL = "http://127.0.0.1:8001";

async function postJson<TResponse extends object>(
  path: string,
  body: unknown,
): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  const payload = (await response.json()) as
    | TResponse
    | { detail?: string };

  if (!response.ok) {
    throw new Error(
      "detail" in payload && payload.detail
        ? payload.detail
        : `Request failed: ${response.status} ${response.statusText}`,
    );
  }

  return payload as TResponse;
}

export function validateRegion(
  draft: RegionDraft,
): Promise<RegionValidationResult> {
  return postJson<RegionValidationResult>(
    "/api/creator/world/regions/validate",
    draft,
  );
}

export function publishRegion(
  draft: RegionDraft,
): Promise<PublishedRegion> {
  return postJson<PublishedRegion>(
    "/api/creator/world/regions/publish",
    draft,
  );
}
