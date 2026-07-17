import { useState } from "react";
import { searchUniverse, type SearchResult } from "../../engine/search/SearchEngine";

export default function GlobalSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);

  async function handleSearch(value: string) {
    setQuery(value);

    if (!value.trim()) {
      setResults([]);
      return;
    }

    const matches = await searchUniverse(value);
    setResults(matches);
  }

  return (
    <div style={{ padding: 16 }}>
      <input
        type="text"
        placeholder="Search Numeria..."
        value={query}
        onChange={(e) => handleSearch(e.target.value)}
        style={{
          width: "100%",
          padding: "10px",
          fontSize: "16px",
        }}
      />

      <div style={{ marginTop: 16 }}>
        {results.map((r) => (
          <div
            key={r.id}
            style={{
              padding: "10px",
              borderBottom: "1px solid #ddd",
            }}
          >
            <strong>{r.title}</strong>
            <div>{r.type}</div>
            {r.description && <small>{r.description}</small>}
          </div>
        ))}
      </div>
    </div>
  );
}
