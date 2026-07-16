import { canonService } from "./services/CanonService";
import { heroService } from "./services/HeroService";
import { storyService } from "./services/StoryService";
import { worldService } from "./services/WorldService";

export const Numeria = {
  canon: canonService,
  hero: heroService,
  story: storyService,
  world: worldService,
} as const;
