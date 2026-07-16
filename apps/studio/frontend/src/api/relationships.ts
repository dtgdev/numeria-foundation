export interface RelationshipDraft {
  type: string;
  source: string;
  target: string;
  summary?: string;
}

export interface RelationshipValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  proposed_id: string | null;
  proposed_path: string | null;
}

export interface PublishedRelationship {
  id: string;
  type: string;
  source: string;
  target: string;
  path: string;
  message: string;
}

const API_BASE_URL = "http://127.0.0.1:8001";

async function postJson<TResponse>(
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

export function validateRelationship(
  draft: RelationshipDraft,
): Promise<RelationshipValidationResult> {
  return postJson<RelationshipValidationResult>(
    "/api/creator/relationships/validate",
    draft,
  );
}

export function publishRelationship(
  draft: RelationshipDraft,
): Promise<PublishedRelationship> {
  return postJson<PublishedRelationship>(
    "/api/creator/relationships/publish",
    draft,
  );
}
