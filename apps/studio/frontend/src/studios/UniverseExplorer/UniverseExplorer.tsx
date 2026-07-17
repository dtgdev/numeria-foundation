import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Numeria,
  type NumeriaEntity,
} from "../../engine";

import {
  ForgeToolbar,
  SearchBar,
} from "../../shared";

import "./UniverseExplorer.css";

const ENTITY_TYPES = [
  "All",
  "Character",
  "Story",
  "Scene",
  "World",
  "Region",
  "Concept",
  "Lesson",
  "Artifact",
  "Book",
] as const;

type EntityTypeFilter =
  (typeof ENTITY_TYPES)[number];

function entityIcon(type: string): string {
  switch (type) {
    case "Character":
      return "🦸";

    case "Story":
    case "Scene":
      return "📖";

    case "World":
    case "Region":
      return "🌍";

    case "Concept":
      return "∆";

    case "Lesson":
      return "🎓";

    case "Artifact":
      return "✨";

    case "Book":
      return "📚";

    default:
      return "◈";
  }
}

export default function UniverseExplorer() {
  const [entities, setEntities] = useState<
    NumeriaEntity[]
  >([]);

  const [query, setQuery] = useState("");
  const [typeFilter, setTypeFilter] =
    useState<EntityTypeFilter>("All");

  const [selectedId, setSelectedId] =
    useState<string | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState<string | null>(null);

  const [copiedId, setCopiedId] =
    useState(false);

  useEffect(() => {
    let cancelled = false;

    async function loadUniverse() {
      try {
        setLoading(true);
        setError(null);

        const canon =
          await Numeria.canon.list();

        if (!cancelled) {
          setEntities(canon);

          setSelectedId((currentId) =>
            currentId ?? canon[0]?.id ?? null,
          );
        }
      } catch (caughtError) {
        if (!cancelled) {
          setError(
            caughtError instanceof Error
              ? caughtError.message
              : "The Numeria universe could not be loaded.",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadUniverse();

    return () => {
      cancelled = true;
    };
  }, []);

  const filteredEntities =
    useMemo(() => {
      const normalizedQuery =
        query.trim().toLowerCase();

      return entities.filter((entity) => {
        const matchesType =
          typeFilter === "All" ||
          entity.type === typeFilter;

        const matchesQuery =
          !normalizedQuery ||
          entity.id
            .toLowerCase()
            .includes(normalizedQuery) ||
          entity.name
            .toLowerCase()
            .includes(normalizedQuery) ||
          entity.type
            .toLowerCase()
            .includes(normalizedQuery);

        return (
          matchesType &&
          matchesQuery
        );
      });
    }, [
      entities,
      query,
      typeFilter,
    ]);

  const selectedEntity =
    useMemo(
      () =>
        entities.find(
          (entity) =>
            entity.id === selectedId,
        ) ?? null,
      [entities, selectedId],
    );

  async function copySelectedId() {
    if (!selectedEntity) {
      return;
    }

    await navigator.clipboard.writeText(
      selectedEntity.id,
    );

    setCopiedId(true);

    window.setTimeout(() => {
      setCopiedId(false);
    }, 1500);
  }

  return (
    <main className="universe-explorer">
      <section className="universe-explorer-hero">
        <div>
          <p className="universe-explorer-eyebrow">
            NUMERIA CREATIVE OPERATING SYSTEM
          </p>

          <h1>Universe Explorer</h1>

          <p>
            Search, inspect, and navigate every
            character, story, world, concept,
            lesson, and artifact in Numeria.
          </p>
        </div>

        <div className="universe-explorer-count">
          <strong>
            {filteredEntities.length}
          </strong>

          <span>
            visible entities
          </span>
        </div>
      </section>

      <ForgeToolbar
        search={
          <SearchBar
            value={query}
            placeholder="Search the Numeria universe..."
            onChange={setQuery}
          />
        }
        actions={
          <button
            type="button"
            className="universe-explorer-create"
          >
            + New Entity
          </button>
        }
      />

      <section className="universe-explorer-workspace">
        <aside className="universe-explorer-filters">
          <p className="universe-explorer-section-label">
            FILTERS
          </p>

          <div className="universe-explorer-filter-list">
            {ENTITY_TYPES.map(
              (entityType) => (
                <button
                  key={entityType}
                  type="button"
                  className={
                    typeFilter === entityType
                      ? "active"
                      : ""
                  }
                  onClick={() =>
                    setTypeFilter(
                      entityType,
                    )
                  }
                >
                  <span>
                    {entityType}
                  </span>

                  <small>
                    {entityType === "All"
                      ? entities.length
                      : entities.filter(
                          (entity) =>
                            entity.type ===
                            entityType,
                        ).length}
                  </small>
                </button>
              ),
            )}
          </div>
        </aside>

        <section className="universe-explorer-results">
          <div className="universe-explorer-panel-heading">
            <div>
              <p className="universe-explorer-section-label">
                RESULTS
              </p>

              <h2>
                Universe Entities
              </h2>
            </div>

            <span>
              {filteredEntities.length}
            </span>
          </div>

          {loading ? (
            <div className="universe-explorer-state">
              Loading the Numeria universe...
            </div>
          ) : error ? (
            <div className="universe-explorer-state error">
              {error}
            </div>
          ) : filteredEntities.length ===
            0 ? (
            <div className="universe-explorer-state">
              No entities match this search.
            </div>
          ) : (
            <div className="universe-explorer-entity-list">
              {filteredEntities.map(
                (entity) => (
                  <button
                    key={entity.id}
                    type="button"
                    className={
                      selectedId === entity.id
                        ? "selected"
                        : ""
                    }
                    onClick={() =>
                      setSelectedId(
                        entity.id,
                      )
                    }
                  >
                    <span className="universe-explorer-entity-icon">
                      {entityIcon(
                        entity.type,
                      )}
                    </span>

                    <span className="universe-explorer-entity-copy">
                      <strong>
                        {entity.name}
                      </strong>

                      <small>
                        {entity.type}
                        {" · "}
                        {entity.id}
                      </small>
                    </span>

                    <span className="universe-explorer-arrow">
                      →
                    </span>
                  </button>
                ),
              )}
            </div>
          )}
        </section>

        <aside className="universe-explorer-inspector">
          <p className="universe-explorer-section-label">
            INSPECTOR
          </p>

          {selectedEntity ? (
            <>
              <div className="universe-explorer-inspector-icon">
                {entityIcon(
                  selectedEntity.type,
                )}
              </div>

              <span className="universe-explorer-type">
                {selectedEntity.type}
              </span>

              <h2>
                {selectedEntity.name}
              </h2>

              <div className="universe-explorer-id-row">
                <p className="universe-explorer-id">
                  {selectedEntity.id}
                </p>

                <button
                  type="button"
                  className="universe-explorer-copy-id"
                  onClick={() => {
                    void copySelectedId();
                  }}
                >
                  {copiedId ? "Copied" : "Copy ID"}
                </button>
              </div>

              <div className="universe-explorer-inspector-section">
                <strong>
                  Description
                </strong>

                <p>
                  Explore this entity’s canon
                  details, relationships, stories,
                  lessons, and creative history.
                </p>
              </div>

              <div className="universe-explorer-inspector-actions">
                <button type="button">
                  Open Studio
                </button>

                <button type="button">
                  View Relationships
                </button>
              </div>
            </>
          ) : (
            <div className="universe-explorer-state">
              Select an entity to inspect it.
            </div>
          )}
        </aside>
      </section>
    </main>
  );
}
