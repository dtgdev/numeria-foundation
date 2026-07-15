import { useEffect, useState } from "react";

import { getSummary } from "../api";
import type { CanonSummary } from "../api";

export default function CanonSummaryCard() {
  const [summary, setSummary] = useState<CanonSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getSummary()
      .then(setSummary)
      .catch((err: unknown) => {
        setError(
          err instanceof Error ? err.message : "Failed to load the canon.",
        );
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <main style={{ padding: 40 }}>Loading Numeria canon...</main>;
  }

  if (error) {
    return (
      <main style={{ padding: 40, color: "crimson" }}>
        <h1>Numeria Studio</h1>
        <p>{error}</p>
        <p>Confirm the backend is running on port 8001.</p>
      </main>
    );
  }

  if (!summary) {
    return <main style={{ padding: 40 }}>No summary returned.</main>;
  }

  return (
    <main
      style={{
        maxWidth: 1000,
        margin: "0 auto",
        padding: 40,
        fontFamily: "Arial, sans-serif",
        color: "#172033",
      }}
    >
      <h1>Numeria Studio</h1>
      <p>A live view of the canonical educational universe.</p>

      <div style={{ display: "flex", gap: 20, margin: "30px 0" }}>
        <section style={cardStyle}>
          <span>Entities</span>
          <h2>{summary.entities}</h2>
        </section>

        <section style={cardStyle}>
          <span>Relationships</span>
          <h2>{summary.relationships}</h2>
        </section>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        <section style={cardStyle}>
          <h2>Entity Types</h2>
          {Object.entries(summary.entity_types).map(([name, count]) => (
            <p key={name}>
              {name}: <strong>{count}</strong>
            </p>
          ))}
        </section>

        <section style={cardStyle}>
          <h2>Relationship Types</h2>
          {Object.entries(summary.relationship_types).map(([name, count]) => (
            <p key={name}>
              {name}: <strong>{count}</strong>
            </p>
          ))}
        </section>
      </div>
    </main>
  );
}

const cardStyle = {
  flex: 1,
  padding: 24,
  border: "1px solid #dfe4ec",
  borderRadius: 16,
  background: "white",
  boxShadow: "0 12px 35px rgba(20, 30, 50, 0.08)",
};
