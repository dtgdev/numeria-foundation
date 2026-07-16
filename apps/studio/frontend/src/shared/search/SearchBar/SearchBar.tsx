import "./SearchBar.css";

interface SearchBarProps {
  value: string;
  placeholder?: string;
  onChange: (value: string) => void;
}

export default function SearchBar({
  value,
  placeholder = "Search Numeria...",
  onChange,
}: SearchBarProps) {
  return (
    <div className="search-bar">
      <span className="search-bar-icon">
        🔍
      </span>

      <input
        type="text"
        value={value}
        placeholder={placeholder}
        onChange={(event) =>
          onChange(event.target.value)
        }
      />

      {value && (
        <button
          type="button"
          className="search-bar-clear"
          onClick={() => onChange("")}
        >
          ×
        </button>
      )}

      <kbd>⌘K</kbd>
    </div>
  );
}
