import type { CanonEntity } from "../../api";

import RelationshipGraph from "../../components/RelationshipGraph";

import {
  Badge,
  Button,
  Card,
} from "../../components/ui";

import { useStudio } from "../../hooks";

import { HeroBanner } from "./components/HeroBanner";

import "./CharacterStudio.css";

interface CharacterStudioProps {
  onCreateCharacter: () => void;
  onAddRelationship: () => void;
}

function readText(
  entity: CanonEntity,
  key: string,
  fallback: string,
): string {
  const value = entity.data[key];

  return typeof value === "string" && value.trim()
    ? value.trim()
    : fallback;
}

function readStringList(
  entity: CanonEntity,
  key: string,
): string[] {
  const value = entity.data[key];

  if (!Array.isArray(value)) {
    return [];
  }

  return value.filter(
    (item): item is string =>
      typeof item === "string" &&
      Boolean(item.trim()),
  );
}

export default function CharacterStudio({
  onCreateCharacter,
  onAddRelationship,
}: CharacterStudioProps) {
  const {
    characters,
    neighborData,
    neighborsError,
    neighborsLoading,
    selectedEntity,
    selectedId,
    selectEntity,
  } = useStudio();

  const selectedCharacter =
    selectedEntity?.type === "Character"
      ? selectedEntity
      : characters.find(
          (character) =>
            character.id === selectedId,
        ) ??
        characters[0] ??
        null;

  return (
    <div className="character-studio">
      <aside className="character-studio-library">
        <header>
          <p className="character-studio-eyebrow">
            HERO FORGE
          </p>

          <h2>Character Library</h2>

          <p>
            Explore and forge the heroes of Numeria.
          </p>
        </header>

        <Button
          fullWidth
          onClick={onCreateCharacter}
        >
          ✨ Forge Hero
        </Button>

        <div className="character-studio-list">
          {characters.map((character) => {
            const selected =
              selectedCharacter?.id ===
              character.id;

            return (
              <button
                key={character.id}
                type="button"
                className={[
                  "character-library-card",
                  selected ? "selected" : "",
                ]
                  .filter(Boolean)
                  .join(" ")}
                onClick={() =>
                  selectEntity(character.id)
                }
              >
                <div className="character-library-avatar">
                  {character.name
                    .split(/\s+/)
                    .slice(0, 2)
                    .map((part) => part[0])
                    .join("")
                    .toUpperCase()}
                </div>

                <div>
                  <Badge
                    tone={
                      selected
                        ? "brand"
                        : "neutral"
                    }
                  >
                    {readText(
                      character,
                      "role",
                      "Canon Hero",
                    )}
                  </Badge>

                  <strong>
                    {character.name}
                  </strong>

                  <small>
                    {character.id}
                  </small>
                </div>
              </button>
            );
          })}
        </div>
      </aside>

      <main className="character-studio-canvas">
        {selectedCharacter ? (
          <>
            <HeroBanner
              character={selectedCharacter}
              onAddRelationship={
                onAddRelationship
              }
              onForgeHero={
                onCreateCharacter
              }
            />

            <section className="character-detail-grid">
              <Card
                title="Mathematical Power"
                description="The mathematical ability this hero embodies."
              >
                <p>
                  {readText(
                    selectedCharacter,
                    "power",
                    "No mathematical power has been documented yet.",
                  )}
                </p>
              </Card>

              <Card
                title="Educational Mission"
                description="What learners should understand after meeting this hero."
              >
                <p>
                  {readText(
                    selectedCharacter,
                    "educational_mission",
                    "No educational mission has been documented yet.",
                  )}
                </p>
              </Card>

              <Card
                title="Personality"
                description="Traits that shape this hero's voice and behavior."
              >
                <div className="character-trait-list">
                  {readStringList(
                    selectedCharacter,
                    "personality",
                  ).map((trait) => (
                    <Badge key={trait}>
                      {trait}
                    </Badge>
                  ))}
                </div>
              </Card>

              <Card
                title="Visual Identity"
                description="The artistic direction for this hero."
              >
                <p>
                  {readText(
                    selectedCharacter,
                    "artwork_prompt",
                    "No artwork prompt has been documented yet.",
                  )}
                </p>
              </Card>
            </section>

            <Card
              title="Hero Relationship Galaxy"
              description="Explore this hero's place in the living Numeria canon."
              action={
                <Badge tone="brand">
                  {neighborData?.relationships
                    .length ?? 0}
                  {" "}
                  relationships
                </Badge>
              }
            >
              {neighborsLoading ? (
                <p>Loading hero graph...</p>
              ) : neighborsError ? (
                <p className="inline-error">
                  {neighborsError}
                </p>
              ) : (
                <RelationshipGraph
                  selectedEntity={
                    selectedCharacter
                  }
                  neighbors={
                    neighborData?.neighbors ?? []
                  }
                  relationships={
                    neighborData
                      ?.relationships ?? []
                  }
                  onSelectEntity={
                    selectEntity
                  }
                />
              )}
            </Card>
          </>
        ) : (
          <Card
            title="Forge the First Hero"
            description="Numeria is waiting for its next mathematical character."
          >
            <Button
              onClick={onCreateCharacter}
            >
              ✨ Forge Hero
            </Button>
          </Card>
        )}
      </main>
    </div>
  );
}
