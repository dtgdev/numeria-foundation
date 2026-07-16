import type { CanonEntity } from "../../api";

import RelationshipGraph from
  "../../components/RelationshipGraph";

import {
  Badge,
  Card,
} from "../../components/ui";

import {
  useStudio,
} from "../../hooks";

import "./CanonStudio.css";

export default function CanonStudio() {
  const {
    entityTypes,
    filteredEntities,
    neighborData,
    neighborsError,
    neighborsLoading,
    query,
    selectedEntity,
    selectedId,
    selectedType,
    selectEntity,
    setQuery,
    setSelectedType,
  } = useStudio();

  function getEntitySummary(
    entity: CanonEntity,
  ): string {
    const summary =
      entity.data.summary;

    if (
      typeof summary === "string" &&
      summary.trim()
    ) {
      return summary;
    }

    const description =
      entity.data.description;

    if (
      typeof description === "string" &&
      description.trim()
    ) {
      return description;
    }

    return "No canonical summary is available yet.";
  }

  return (
    <div className="canon-studio">
      <aside className="canon-studio-browser">
        <header className="canon-studio-browser-header">
          <p className="canon-studio-eyebrow">
            LIVING CANON
          </p>

          <h2>Canon Explorer</h2>

          <p>
            Search and explore every object in
            the Numeria universe.
          </p>
        </header>

        <input
          className="search-input"
          value={query}
          onChange={(event) =>
            setQuery(event.target.value)
          }
          placeholder="Search by name or ID"
          aria-label="Search canon objects"
        />

        <div
          className="type-filter"
          aria-label="Filter canon objects by type"
        >
          {entityTypes.map((type) => (
            <button
              key={type}
              type="button"
              className={
                selectedType === type
                  ? "active"
                  : ""
              }
              onClick={() =>
                setSelectedType(type)
              }
            >
              {type}
            </button>
          ))}
        </div>

        <div className="canon-studio-list">
          {filteredEntities.map((entity) => (
            <button
              key={entity.id}
              type="button"
              className={[
                "canon-studio-card",
                entity.id === selectedId
                  ? "selected"
                  : "",
              ]
                .filter(Boolean)
                .join(" ")}
              onClick={() =>
                selectEntity(entity.id)
              }
            >
              <div className="canon-studio-card-heading">
                <Badge
                  tone={
                    entity.id === selectedId
                      ? "brand"
                      : "neutral"
                  }
                >
                  {entity.type}
                </Badge>

                {entity.id === selectedId && (
                  <span className="canon-studio-selected-label">
                    Selected
                  </span>
                )}
              </div>

              <strong>{entity.name}</strong>

              <p>
                {getEntitySummary(entity)}
              </p>

              <small>{entity.id}</small>
            </button>
          ))}

          {filteredEntities.length === 0 && (
            <div className="canon-studio-empty">
              <strong>
                No canon objects found
              </strong>

              <p>
                Try another search or entity type.
              </p>
            </div>
          )}
        </div>
      </aside>

      <section className="canon-studio-canvas">
        {selectedEntity ? (
          <>
            <header className="canon-studio-canvas-header">
              <div>
                <Badge tone="brand">
                  {selectedEntity.type}
                </Badge>

                <h2>
                  {selectedEntity.name}
                </h2>

                <p>
                  {selectedEntity.id}
                </p>
              </div>

              <Badge tone="neutral">
                {neighborData?.relationships
                  .length ?? 0}
                {" "}
                relationships
              </Badge>
            </header>

            <Card
              title="Living Knowledge Graph"
              description={
                "Drag nodes, zoom, and select a connected object to navigate the canon."
              }
              padding="small"
            >
              {neighborsLoading ? (
                <div className="canon-studio-loading">
                  Loading relationships...
                </div>
              ) : neighborsError ? (
                <div className="canon-studio-error">
                  {neighborsError}
                </div>
              ) : (
                <RelationshipGraph
                  selectedEntity={
                    selectedEntity
                  }
                  neighbors={
                    neighborData?.neighbors ??
                    []
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

            <Card
              title="Connected Canon Objects"
              description={
                "Every relationship surrounding the selected object."
              }
            >
              <div className="canon-studio-neighbors">
                {neighborData?.neighbors.map(
                  (neighbor) => {
                    const relationship =
                      neighborData.relationships.find(
                        (edge) =>
                          (
                            edge.source ===
                              selectedEntity.id &&
                            edge.target ===
                              neighbor.id
                          ) ||
                          (
                            edge.target ===
                              selectedEntity.id &&
                            edge.source ===
                              neighbor.id
                          ),
                      );

                    const outgoing =
                      relationship?.source ===
                      selectedEntity.id;

                    return (
                      <button
                        key={neighbor.id}
                        type="button"
                        className="canon-neighbor-card"
                        onClick={() =>
                          selectEntity(
                            neighbor.id,
                          )
                        }
                      >
                        <Badge tone="neutral">
                          {neighbor.type}
                        </Badge>

                        <strong>
                          {neighbor.name}
                        </strong>

                        <span>
                          {outgoing ? "→" : "←"}
                          {" "}
                          {relationship?.type
                            .replaceAll(
                              "_",
                              " ",
                            ) ??
                            "CONNECTED"}
                        </span>

                        <small>
                          {neighbor.id}
                        </small>
                      </button>
                    );
                  },
                )}

                {!neighborsLoading &&
                  !neighborsError &&
                  neighborData?.neighbors
                    .length === 0 && (
                    <div className="canon-studio-empty">
                      <strong>
                        No relationships yet
                      </strong>

                      <p>
                        Use Relationship Studio
                        to connect this object.
                      </p>
                    </div>
                  )}
              </div>
            </Card>
          </>
        ) : (
          <Card
            title="Select a Canon Object"
            description={
              "Choose an object from the Canon Explorer to inspect its graph."
            }
          >
            <div className="canon-studio-empty">
              <strong>
                The canvas is waiting
              </strong>

              <p>
                Select a character, concept,
                region, book, or other canon
                object.
              </p>
            </div>
          </Card>
        )}
      </section>
    </div>
  );
}
