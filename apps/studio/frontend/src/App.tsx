import { useEffect, useMemo, useState } from "react";
import RelationshipGraph from "./components/RelationshipGraph";

import {
  getEntities,
  getEntityNeighbors,
  getSummary,
} from "./api";

import type {
  CanonEntity,
  CanonSummary,
  EntityNeighbors,
} from "./api";

export default function App() {
  const [summary, setSummary] = useState<CanonSummary | null>(null);
  const [entities, setEntities] = useState<CanonEntity[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedType, setSelectedType] = useState("All");
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [neighborData, setNeighborData] =
    useState<EntityNeighbors | null>(null);

  const [neighborsLoading, setNeighborsLoading] =
    useState(false);

  const [neighborsError, setNeighborsError] = useState("");

  useEffect(() => {
    Promise.all([getSummary(), getEntities()])
      .then(([summaryData, entityData]) => {
        setSummary(summaryData);
        setEntities(entityData);
        setSelectedId(entityData[0]?.id ?? null);
      })
      .catch((caughtError: unknown) => {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "Failed to load the Numeria canon.",
        );
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setNeighborData(null);
      return;
    }

    setNeighborsLoading(true);
    setNeighborsError("");

    getEntityNeighbors(selectedId)
      .then(setNeighborData)
      .catch((caughtError: unknown) => {
        setNeighborsError(
          caughtError instanceof Error
            ? caughtError.message
            : "Failed to load relationships.",
        );
      })
      .finally(() => setNeighborsLoading(false));
  }, [selectedId]);

  const entityTypes = useMemo(() => {
    return [
      "All",
      ...Array.from(
        new Set(entities.map((entity) => entity.type)),
      ).sort(),
    ];
  }, [entities]);

  const filteredEntities = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();

    return entities.filter((entity) => {
      const matchesType =
        selectedType === "All" ||
        entity.type === selectedType;

      const matchesQuery =
        normalizedQuery.length === 0 ||
        entity.name.toLowerCase().includes(normalizedQuery) ||
        entity.id.toLowerCase().includes(normalizedQuery);

      return matchesType && matchesQuery;
    });
  }, [entities, query, selectedType]);

  const selectedEntity =
    entities.find((entity) => entity.id === selectedId) ?? null;

  if (loading) {
    return (
      <main className="center-state">
        Loading Numeria Studio...
      </main>
    );
  }

  if (error) {
    return (
      <main className="center-state error-state">
        <div>
          <h1>Numeria Studio</h1>
          <p>{error}</p>
        </div>
      </main>
    );
  }

  return (
    <div className="studio-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">NUMERIA FOUNDATION</p>
          <h1>Numeria Studio</h1>
        </div>

        <div className="topbar-metrics">
          <span>{summary?.entities ?? 0} entities</span>
          <span>
            {summary?.relationships ?? 0} relationships
          </span>
        </div>
      </header>

      <div className="workspace">
        <aside className="sidebar">
          <div className="sidebar-heading">
            <h2>Canon Explorer</h2>
            <p>Browse the live educational universe.</p>
          </div>

          <input
            className="search-input"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search by name or ID"
          />

          <div className="type-filter">
            {entityTypes.map((type) => (
              <button
                key={type}
                type="button"
                className={
                  type === selectedType ? "active" : ""
                }
                onClick={() => setSelectedType(type)}
              >
                {type}
              </button>
            ))}
          </div>

          <div className="entity-list">
            {filteredEntities.map((entity) => (
              <button
                key={entity.id}
                type="button"
                className={`entity-row ${
                  entity.id === selectedId ? "selected" : ""
                }`}
                onClick={() => setSelectedId(entity.id)}
              >
                <span className="entity-type">
                  {entity.type}
                </span>

                <strong>{entity.name}</strong>
                <small>{entity.id}</small>
              </button>
            ))}
          </div>
        </aside>

        <main className="detail-panel">
          {selectedEntity && (
              <>
                <div className="detail-heading">
                <span className="type-badge">
                  {selectedEntity.type}
                </span>

                  <h2>{selectedEntity.name}</h2>
                  <p>{selectedEntity.id}</p>
                </div>

                <section className="detail-card graph-card">
                  <div className="card-heading-row">
                    <div>
                      <h3>Knowledge Graph</h3>
                      <p>
                        Drag nodes, zoom, and click a connected entity
                        to navigate.
                      </p>
                    </div>

                    <span className="relationship-count">
      {neighborData?.neighbors.length ?? 0} nodes
    </span>
                  </div>

                  {neighborsLoading ? (
                      <p>Loading graph...</p>
                  ) : (
                      <RelationshipGraph
                          selectedEntity={selectedEntity}
                          neighbors={neighborData?.neighbors ?? []}
                          relationships={
                              neighborData?.relationships ?? []
                          }
                          onSelectEntity={setSelectedId}
                      />
                  )}
                </section>

                <section className="detail-card">
                  <div className="card-heading-row">
                    <div>
                      <h3>Relationship Navigation</h3>
                      <p>
                        Click a connected entity to navigate to it.
                      </p>
                    </div>

                    <span className="relationship-count">
                    {neighborData?.relationships.length ?? 0} edges
                  </span>
                  </div>

                  {neighborsLoading && (
                      <p>Loading relationships...</p>
                  )}

                  {neighborsError && (
                      <p className="inline-error">
                        {neighborsError}
                      </p>
                  )}

                  <div className="neighbor-grid">
                    {neighborData?.neighbors.map((neighbor) => {
                      const relationship =
                          neighborData.relationships.find(
                              (edge) =>
                                  (edge.source === selectedEntity.id &&
                                      edge.target === neighbor.id) ||
                                  (edge.target === selectedEntity.id &&
                                      edge.source === neighbor.id),
                          );

                      const direction =
                          relationship?.source === selectedEntity.id
                              ? "outgoing"
                              : "incoming";

                      return (
                          <button
                              key={neighbor.id}
                              type="button"
                              className="neighbor-card"
                              onClick={() =>
                                  setSelectedId(neighbor.id)
                              }
                          >
                        <span className="neighbor-type">
                          {neighbor.type}
                        </span>

                            <strong>{neighbor.name}</strong>
                            <small>{neighbor.id}</small>

                            <span
                                className={`edge-label ${direction}`}
                            >
                          {relationship?.type.replaceAll(
                              "_",
                              " ",
                          ) ?? "CONNECTED"}
                        </span>
                          </button>
                      );
                    })}
                  </div>

                  {!neighborsLoading &&
                      !neighborsError &&
                      neighborData?.neighbors.length === 0 && (
                          <p>No connected entities yet.</p>
                      )}
                </section>

                <section className="detail-card">
                  <h3>Source</h3>
                  <code>{selectedEntity.path}</code>
                </section>

                <section className="detail-card">
                  <h3>Canonical Data</h3>
                  <pre>
                  {JSON.stringify(
                      selectedEntity.data,
                      null,
                      2,
                  )}
                </pre>
                </section>
              </>
          )}
        </main>
      </div>
    </div>
  );
}
