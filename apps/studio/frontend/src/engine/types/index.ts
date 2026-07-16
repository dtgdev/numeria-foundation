import type {
  CanonEntity,
  CanonSummary,
  EntityNeighbors,
} from "../../api";

export type NumeriaEntity = CanonEntity;
export type NumeriaSummary = CanonSummary;
export type NumeriaNeighbors = EntityNeighbors;

export interface EntityQuery {
  type?: string;
  search?: string;
}

export interface EntityService {
  list(query?: EntityQuery): Promise<NumeriaEntity[]>;
  get(id: string): Promise<NumeriaEntity | null>;
  search(value: string): Promise<NumeriaEntity[]>;
  relationships(id: string): Promise<NumeriaNeighbors>;
}
