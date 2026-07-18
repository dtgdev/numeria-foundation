import { Numeria } from "../NumeriaEngine";

import type {
  NumeriaEntity,
} from "../types";

export interface SearchResult {
  id: string;
  type: string;
  title: string;
  description?: string;
}

function matchesQuery(
  entity: NumeriaEntity,
  query: string,
): boolean {
  return [
    entity.id,
    entity.name,
    entity.type,
  ].some((value) =>
    value
      .toLowerCase()
      .includes(query),
  );
}

export async function searchUniverse(
  query: string,
): Promise<SearchResult[]> {
  const normalizedQuery =
    query.trim().toLowerCase();

  if (!normalizedQuery) {
    return [];
  }

  const canon =
    await Numeria.canon.list();

  return canon
    .filter((entity) =>
      matchesQuery(
        entity,
        normalizedQuery,
      ),
    )
    .map((entity) => ({
      id: entity.id,
      type: entity.type,
      title: entity.name,
    }));
}
