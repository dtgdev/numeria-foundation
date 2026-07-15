export interface CanonSummary {
  entities: number;
  relationships: number;
  entity_types: Record<string, number>;
  relationship_types: Record<string, number>;
}

const API_BASE_URL = "http://127.0.0.1:8001";

export async function getSummary(): Promise<CanonSummary> {
  const response = await fetch(
    `${API_BASE_URL}/api/graph/summary`,
  );

  if (!response.ok) {
    throw new Error(
      `Failed to load graph summary: ${response.status}`,
    );
  }

  return response.json();
}
