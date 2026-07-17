import type { NumeriaEntity } from "./types";

import { canonService } from "./services/CanonService";
import { heroService } from "./services/HeroService";
import { storyService } from "./services/StoryService";
import { worldService } from "./services/WorldService";

export interface DirectorSuggestion {
  id: string;
  severity: "info" | "warning" | "critical";
  category:
    | "story-structure"
    | "mathematics"
    | "character"
    | "canon";
  title: string;
  message: string;
}

export interface StoryAnalysis {
  storyId: string;
  score: number;
  suggestions: DirectorSuggestion[];
}

function readText(
  entity: NumeriaEntity,
  key: string,
): string {
  const value = entity.data[key];

  return typeof value === "string"
    ? value.trim()
    : "";
}

const directorService = {
  async analyzeStory(
    storyId: string,
  ): Promise<StoryAnalysis> {
    const story =
      await storyService.get(storyId);

    if (!story) {
      throw new Error(
        `Story '${storyId}' could not be found.`,
      );
    }

    const suggestions:
      DirectorSuggestion[] = [];

    if (
      !readText(
        story,
        "educational_mission",
      )
    ) {
      suggestions.push({
        id: `${storyId}-learning-goal`,
        severity: "warning",
        category: "mathematics",
        title: "Learning goal is missing",
        message:
          "Add a clear mathematical learning goal so the story can be reviewed for educational alignment.",
      });
    }

    if (!readText(story, "summary")) {
      suggestions.push({
        id: `${storyId}-summary`,
        severity: "warning",
        category: "story-structure",
        title: "Story summary is missing",
        message:
          "Add a concise summary that explains the beginning, challenge, discovery, and resolution.",
      });
    }

    const relationships =
      await storyService.relationships(
        storyId,
      );

    if (
      relationships.neighbors.length === 0
    ) {
      suggestions.push({
        id: `${storyId}-relationships`,
        severity: "critical",
        category: "canon",
        title: "Story is disconnected",
        message:
          "Connect this story to at least one hero, concept, or location in the Numeria canon.",
      });
    }

    const score = Math.max(
      0,
      100 -
        suggestions.reduce(
          (
            total,
            suggestion,
          ) =>
            total +
            (
              suggestion.severity ===
              "critical"
                ? 35
                : suggestion.severity ===
                    "warning"
                  ? 20
                  : 10
            ),
          0,
        ),
    );

    return {
      storyId,
      score,
      suggestions,
    };
  },
};

export const Numeria = {
  canon: canonService,
  hero: heroService,
  story: storyService,
  world: worldService,
  director: directorService,
} as const;
