export type StudioSection =
  | "dashboard"
  | "characters"
  | "stories"
  | "world"
  | "canon"
  | "relationships";

export interface StudioDefinition {
  id: StudioSection;
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
  {
    id: "relationships",
    title: "Relationships",
    icon: "🔗",
    description: "Canon Graph",
  },
];

export function getStudio(
  id: StudioSection,
): StudioDefinition | undefined {
  return STUDIOS.find((studio) => studio.id === id);
}
