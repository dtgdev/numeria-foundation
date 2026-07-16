import {
  CanonStudio,
  CharacterStudio,
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

    case "relationships":
    case "canon":
    default:
      return <CanonStudio />;
  }
}
