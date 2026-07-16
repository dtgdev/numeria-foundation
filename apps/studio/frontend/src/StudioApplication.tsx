import { useState } from "react";

import type {
  PublishedCharacter,
} from "./api";

import type {
  PublishedRelationship,
} from "./api/relationships";

import type {
  PublishedRegion,
} from "./api/world";

import {
  CharacterCreatorDialog,
  RelationshipCreatorDialog,
} from "./components/creator";

import {
  StudioShell,
} from "./components/layout";

import {
  Badge,
  Button,
  Card,
} from "./components/ui";

import {
  RegionCreatorDialog,
} from "./components/world";

import {
  useStudio,
} from "./hooks";

import StudioRouter from "./app/StudioRouter";

export default function StudioApplication() {
  const {
    activeSection,
    setActiveSection,
    entities,
    selectedEntity,
    neighborData,
    loading,
    error,
    loadStudio,
    refreshStudio,
  } = useStudio();

  const [
    characterCreatorOpen,
    setCharacterCreatorOpen,
  ] = useState(false);

  const [
    relationshipCreatorOpen,
    setRelationshipCreatorOpen,
  ] = useState(false);

  const [
    regionCreatorOpen,
    setRegionCreatorOpen,
  ] = useState(false);

  async function handleCharacterPublished(
    character: PublishedCharacter,
  ) {
    await refreshStudio(character.id);

    setCharacterCreatorOpen(false);
  }

  async function handleRelationshipPublished(
    relationship: PublishedRelationship,
  ) {
    await refreshStudio(
      relationship.source,
    );

    setRelationshipCreatorOpen(false);
  }

  async function handleRegionPublished(
    region: PublishedRegion,
  ) {
    await refreshStudio(region.id);

    setRegionCreatorOpen(false);
  }

  function renderToolbar() {
    if (activeSection === "world") {
      return (
        <Button
          onClick={() =>
            setRegionCreatorOpen(true)
          }
        >
          + Create Region
        </Button>
      );
    }

    if (
      activeSection ===
      "relationships"
    ) {
      return (
        <Button
          onClick={() =>
            setRelationshipCreatorOpen(
              true,
            )
          }
          disabled={!selectedEntity}
        >
          + Add Relationship
        </Button>
      );
    }

    if (
      activeSection ===
      "characters"
    ) {
      return (
        <Button
          onClick={() =>
            setCharacterCreatorOpen(
              true,
            )
          }
        >
          + Create Character
        </Button>
      );
    }

    return (
      <>
        <Button
          variant="secondary"
          onClick={() =>
            setRelationshipCreatorOpen(
              true,
            )
          }
          disabled={!selectedEntity}
        >
          + Add Relationship
        </Button>

        <Button
          onClick={() =>
            setCharacterCreatorOpen(
              true,
            )
          }
        >
          + Create Character
        </Button>
      </>
    );
  }

  const inspectorTitle =
    selectedEntity?.name ??
    "Nothing Selected";

  const inspectorDescription =
    selectedEntity
      ? `${selectedEntity.type} · ${selectedEntity.id}`
      : "Select a canon object to inspect it.";

  const inspectorContent =
    selectedEntity ? (
      <>
        <Badge tone="brand">
          {selectedEntity.type}
        </Badge>

        <Card
          title="Source"
          padding="small"
        >
          <code>
            {selectedEntity.path}
          </code>
        </Card>

        <Card
          title="Relationships"
          padding="small"
        >
          <p>
            {neighborData
              ?.relationships.length ??
              0}
            {" "}
            connected edges
          </p>
        </Card>

        <Card
          title="Canonical Data"
          padding="small"
        >
          <pre className="studio-inspector-json">
            {JSON.stringify(
              selectedEntity.data,
              null,
              2,
            )}
          </pre>
        </Card>
      </>
    ) : (
      <p className="empty-message">
        Select an object from Canon Studio.
      </p>
    );

  const inspectorActions =
    selectedEntity ? (
      <>
        <Button
          fullWidth
          onClick={() =>
            setRelationshipCreatorOpen(
              true,
            )
          }
        >
          + Add Relationship
        </Button>

        <Button
          fullWidth
          variant="secondary"
          onClick={() =>
            setActiveSection("canon")
          }
        >
          Open in Canon Explorer
        </Button>
      </>
    ) : undefined;

  if (loading) {
    return (
      <main className="center-state">
        Loading Numeria Studio Genesis...
      </main>
    );
  }

  if (error) {
    return (
      <main className="center-state error-state">
        <div>
          <h1>Numeria Studio</h1>

          <p>{error}</p>

          <Button
            onClick={() =>
              void loadStudio()
            }
          >
            Try Again
          </Button>
        </div>
      </main>
    );
  }

  return (
    <>
      <StudioShell
        activeSection={activeSection}
        onSectionChange={
          setActiveSection
        }
        inspectorTitle={
          inspectorTitle
        }
        inspectorDescription={
          inspectorDescription
        }
        inspectorContent={
          inspectorContent
        }
        inspectorActions={
          inspectorActions
        }
        toolbar={renderToolbar()}
      >
        <StudioRouter
          activeSection={activeSection}
          onCreateRegion={() =>
            setRegionCreatorOpen(true)
          }
          onCreateCharacter={() =>
            setCharacterCreatorOpen(true)
          }
          onAddRelationship={() =>
            setRelationshipCreatorOpen(true)
          }
        />
      </StudioShell>

      <CharacterCreatorDialog
        open={characterCreatorOpen}
        onClose={() =>
          setCharacterCreatorOpen(
            false,
          )
        }
        onPublished={
          handleCharacterPublished
        }
      />

      <RelationshipCreatorDialog
        open={
          relationshipCreatorOpen
        }
        sourceEntity={selectedEntity}
        entities={entities}
        onClose={() =>
          setRelationshipCreatorOpen(
            false,
          )
        }
        onPublished={
          handleRelationshipPublished
        }
      />

      <RegionCreatorDialog
        open={regionCreatorOpen}
        onClose={() =>
          setRegionCreatorOpen(false)
        }
        onPublished={
          handleRegionPublished
        }
      />
    </>
  );
}
