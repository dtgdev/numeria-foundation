import DashboardStudio from "../studios/DashboardStudio";
import UniverseExplorer from "../studios/UniverseExplorer";
import type { NumeriaEntity } from "../engine";
import { CanonStudio } from "../studios/CanonStudio";
import { CharacterStudio } from "../studios/CharacterStudio";
import { StoryStudio } from "../studios/StoryStudio";
import { WorldStudio } from "../studios/WorldStudio";

interface StudioRouterProps {
  activeSection: string;
  onCreateRegion: () => void;
  onCreateCharacter: () => void;
  onAddRelationship: () => void;
  onOpenEntity: (
    entity: NumeriaEntity,
  ) => void;
  onViewRelationships: (
    entity: NumeriaEntity,
  ) => void;
}

export default function StudioRouter({
  activeSection,
  onCreateRegion,
  onCreateCharacter,
  onAddRelationship,
  onOpenEntity,
  onViewRelationships,
}: StudioRouterProps) {
  switch (activeSection) {
    case "explorer":
      return (
        <UniverseExplorer
          onOpenEntity={onOpenEntity}
          onViewRelationships={
            onViewRelationships
          }
        />
      );

    case "characters":
      return (
        <CharacterStudio
          onCreateCharacter={onCreateCharacter}
          onAddRelationship={onAddRelationship}
        />
      );

    case "stories":
      return <StoryStudio />;

    case "world":
      return (
        <WorldStudio
          onCreateRegion={onCreateRegion}
        />
      );

    case "canon":
      return <CanonStudio />;

    case "dashboard":
    default:
      return <DashboardStudio />;
  }
}
