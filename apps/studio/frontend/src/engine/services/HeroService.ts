import { canonService } from "./CanonService";

export const heroService = {
  list: () =>
    canonService.list({
      type: "Character",
    }),

  get: (id: string) =>
    canonService.get(id),

  search: (value: string) =>
    canonService.list({
      type: "Character",
      search: value,
    }),

  relationships: (id: string) =>
    canonService.relationships(id),
};
