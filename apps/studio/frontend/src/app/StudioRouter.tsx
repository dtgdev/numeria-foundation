import {
  CanonStudio,
  CharacterStudio,
  StoryStudio,
  WorldStudio,
} from "../studios";

import type {
  StudioSection,
} from "../components/layout";

interface StudioRouterProps {
  activeSection: StudioSection;
  onCreateRegion: () => void;
  onCreateCharacter: () => void;
  onAddRelationship: () => void;
}

export default function StudioRouter({
  activeSection,
  onCreateRegion,
  onCreateCharacter,
  onAddRelationship,
}: StudioRouterProps) {
  switch (activeSection) {
    case "world":
      return (
        <WorldStudio
          onCreateRegion={onCreateRegion}
        />
      );

    case "characters":
      return (
        <CharacterStudio
          onCreateCharacter={
            onCreateCharacter
          }
          onAddRelationship={
            onAddRelationship
          }
        />
      );

    case "stories":
      return <StoryStudio />;

    case "relationships":
    case "canon":
    default:
      return <CanonStudio />;
  }
}
