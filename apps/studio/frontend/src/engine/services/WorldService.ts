import { canonService } from "./CanonService";

export const worldService = {
  worlds: () =>
    canonService.list({
      type: "World",
    }),

  regions: () =>
    canonService.list({
      type: "Region",
    }),

  get: (id: string) =>
    canonService.get(id),

  relationships: (id: string) =>
    canonService.relationships(id),
};
