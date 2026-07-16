export interface CanonSummary {
  entities: number;
  relationships: number;
  entity_types: Record<string, number>;
  relationship_types: Record<string, number>;
}

export interface CanonEntity {
  id: string;
  type: string;
  name: string;
  path: string;
  data: Record<string, unknown>;
}

export interface CanonRelationship {
  id: string;
  type: string;
  source: string;
  target: string;
  path: string;
  data: Record<string, unknown>;
}

export interface EntityNeighbors {
  entity_id: string;
  neighbors: CanonEntity[];
  relationships: CanonRelationship[];
}

export interface CharacterDraft {
  name: string;
  nickname?: string;
  role: string;
  summary: string;
  personality: string[];
  power: string;
  educational_mission: string;
  color_theme?: string;
  artwork_prompt?: string;
}

export interface CharacterValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  proposed_id: string | null;
  proposed_path: string | null;
}

export interface PublishedCharacter {
  id: string;
  name: string;
  path: string;
  message: string;
}

const API_BASE_URL = "http://127.0.0.1:8001";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    throw new Error(
      `Request failed: ${response.status} ${response.statusText}`,
    );
  }

  return response.json() as Promise<T>;
}

export function getSummary(): Promise<CanonSummary> {
  return getJson<CanonSummary>("/api/graph/summary");
}

export function getEntities(): Promise<CanonEntity[]> {
  return getJson<CanonEntity[]>("/api/graph/entities");
}

export function getEntityNeighbors(
  entityId: string,
): Promise<EntityNeighbors> {
  return getJson<EntityNeighbors>(
    `/api/graph/entity/${encodeURIComponent(entityId)}/neighbors`,
  );
}

export async function validateCharacter(
  draft: CharacterDraft,
): Promise<CharacterValidationResult> {
  const response = await fetch(
    `${API_BASE_URL}/api/creator/characters/validate`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(draft),
    },
  );

  if (!response.ok) {
    throw new Error(
      `Character validation failed: ${response.status} ${response.statusText}`,
    );
  }

  return response.json() as Promise<CharacterValidationResult>;
}

export async function publishCharacter(
  draft: CharacterDraft,
): Promise<PublishedCharacter> {
  const response = await fetch(
    `${API_BASE_URL}/api/creator/characters/publish`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(draft),
    },
  );

  const payload = (await response.json()) as
    | PublishedCharacter
    | { detail?: string };

  if (!response.ok) {
    throw new Error(
      "detail" in payload && payload.detail
        ? payload.detail
        : `Character publication failed: ${response.status}`,
    );
  }

  return payload as PublishedCharacter;
}
