import { useEffect, useMemo, useState } from "react";

import { getEntities, getSummary } from "./api";

import type { CanonEntity, CanonSummary } from "./api";

export default function App() {

  const [summary, setSummary] = useState<CanonSummary | null>(null);

  const [entities, setEntities] = useState<CanonEntity[]>([]);

  const [selectedId, setSelectedId] = useState<string | null>(null);

  const [selectedType, setSelectedType] = useState("All");

  const [query, setQuery] = useState("");

  const [loading, setLoading] = useState(true);

  const [error, setError] = useState("");

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

        selectedType === "All" || entity.type === selectedType;

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

    return <main className="center-state">Loading Numeria Studio...</main>;

  }

  if (error) {

    return (

      <main className="center-state error-state">

        <div>

          <h1>Numeria Studio</h1>

          <p>{error}</p>

          <p>Confirm the FastAPI backend is running on port 8001.</p>

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

          <span>{summary?.relationships ?? 0} relationships</span>

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

            aria-label="Search canon entities"

          />

          <div className="type-filter">

            {entityTypes.map((type) => (

              <button

                key={type}

                type="button"

                className={type === selectedType ? "active" : ""}

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

                <span className="entity-type">{entity.type}</span>

                <strong>{entity.name}</strong>

                <small>{entity.id}</small>

              </button>

            ))}

            {filteredEntities.length === 0 && (

              <p className="empty-message">

                No matching canon entities.

              </p>

            )}

          </div>

        </aside>

        <main className="detail-panel">

          {selectedEntity ? (

            <>

              <div className="detail-heading">

                <span className="type-badge">

                  {selectedEntity.type}

                </span>

                <h2>{selectedEntity.name}</h2>

                <p>{selectedEntity.id}</p>

              </div>

              <section className="detail-card">

                <h3>Source</h3>

                <code>{selectedEntity.path}</code>

              </section>

              <section className="detail-card">

                <h3>Canonical data</h3>

                <pre>

                  {JSON.stringify(selectedEntity.data, null, 2)}

                </pre>

              </section>

            </>

          ) : (

            <section className="detail-card">

              Select an entity to inspect its canonical data.

            </section>

          )}

        </main>

      </div>

    </div>

  );

}