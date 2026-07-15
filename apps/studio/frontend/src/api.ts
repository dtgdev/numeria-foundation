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
