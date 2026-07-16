import {
  getEntities,
  getEntityNeighbors,
  getSummary,
} from "../../api";

import type {
  EntityQuery,
  NumeriaEntity,
  NumeriaNeighbors,
  NumeriaSummary,
} from "../types";

function normalize(value: string): string {
  return value.trim().toLowerCase();
}

class CanonService {
  async summary(): Promise<NumeriaSummary> {
    return getSummary();
  }

  async list(
    query: EntityQuery = {},
  ): Promise<NumeriaEntity[]> {
    const entities = await getEntities();

    const type = query.type?.trim();
    const search = normalize(
      query.search ?? "",
    );

    return entities.filter((entity) => {
      const matchesType =
        !type ||
        entity.type === type;

      const matchesSearch =
        !search ||
        normalize(entity.name).includes(search) ||
        normalize(entity.id).includes(search) ||
        normalize(entity.type).includes(search);

      return matchesType && matchesSearch;
    });
  }

  async get(
    id: string,
  ): Promise<NumeriaEntity | null> {
    const entities = await getEntities();

    return (
      entities.find(
        (entity) => entity.id === id,
      ) ?? null
    );
  }

  async search(
    value: string,
  ): Promise<NumeriaEntity[]> {
    return this.list({
      search: value,
    });
  }

  async relationships(
    id: string,
  ): Promise<NumeriaNeighbors> {
    return getEntityNeighbors(id);
  }
}

export const canonService =
  new CanonService();
