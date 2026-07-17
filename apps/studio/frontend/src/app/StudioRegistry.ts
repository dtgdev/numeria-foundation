export interface StudioDefinition {
  id: string;
  title: string;
  icon: string;
  description: string;
}

export const STUDIOS: StudioDefinition[] = [
  {
    id: "dashboard",
    title: "Dashboard",
    icon: "🏛️",
    description: "Universe Mission Control",
  },
  {
    id: "characters",
    title: "Characters",
    icon: "🦸",
    description: "Hero Forge",
  },
  {
    id: "stories",
    title: "Stories",
    icon: "📖",
    description: "Story Forge",
  },
  {
    id: "world",
    title: "World",
    icon: "🌍",
    description: "World Forge",
  },
  {
    id: "canon",
    title: "Canon",
    icon: "📚",
    description: "Canon Studio",
  },
];
