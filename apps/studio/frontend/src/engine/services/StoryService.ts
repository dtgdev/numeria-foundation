import { canonService } from "./CanonService";

export const storyService = {
  async list() {
    const entities =
      await canonService.list();

    return entities.filter(
      (entity) =>
        entity.type === "Story" ||
        entity.type === "Scene",
    );
  },

  get: (id: string) =>
    canonService.get(id),

  async search(value: string) {
    const entities =
      await canonService.search(value);

    return entities.filter(
      (entity) =>
        entity.type === "Story" ||
        entity.type === "Scene",
    );
  },

  relationships: (id: string) =>
    canonService.relationships(id),
};
