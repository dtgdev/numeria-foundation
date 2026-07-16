import "./StudioNavigation.css";

export type StudioSection =
  | "world"
  | "characters"
  | "relationships"
  | "canon"
  | "stories"
  | "books"
  | "lessons"
  | "ai";

interface NavigationItem {
  id: StudioSection;
  label: string;
  icon: string;
  available: boolean;
}

interface StudioNavigationProps {
  activeSection: StudioSection;
  onSelect: (section: StudioSection) => void;
}

const NAVIGATION_ITEMS: NavigationItem[] = [
  {
    id: "world",
    label: "World",
    icon: "🌍",
    available: true,
  },
  {
    id: "characters",
    label: "Characters",
    icon: "🎭",
    available: true,
  },
  {
    id: "relationships",
    label: "Relationships",
    icon: "🔗",
    available: true,
  },
  {
    id: "canon",
    label: "Canon Explorer",
    icon: "🕸",
    available: true,
  },
  {
    id: "stories",
    label: "Story Forge",
    icon: "📖",
    available: true,
  },
  {
    id: "books",
    label: "Books",
    icon: "📚",
    available: false,
  },
  {
    id: "lessons",
    label: "Lessons",
    icon: "🎓",
    available: false,
  },
  {
    id: "ai",
    label: "AI Director",
    icon: "✨",
    available: false,
  },
];

export default function StudioNavigation({
  activeSection,
  onSelect,
}: StudioNavigationProps) {
  return (
    <nav
      className="studio-navigation"
      aria-label="Numeria Studio navigation"
    >
      <div className="studio-navigation-brand">
        <div className="studio-navigation-logo">N</div>

        <div>
          <strong>Numeria</strong>
          <span>Studio Genesis</span>
        </div>
      </div>

      <div className="studio-navigation-items">
        {NAVIGATION_ITEMS.map((item) => (
          <button
            key={item.id}
            type="button"
            className={[
              "studio-navigation-item",
              activeSection === item.id ? "active" : "",
              !item.available ? "disabled" : "",
            ]
              .filter(Boolean)
              .join(" ")}
            disabled={!item.available}
            onClick={() => onSelect(item.id)}
          >
            <span
              className="studio-navigation-icon"
              aria-hidden="true"
            >
              {item.icon}
            </span>

            <span className="studio-navigation-label">
              {item.label}
            </span>

            {!item.available && (
              <small>Coming soon</small>
            )}
          </button>
        ))}
      </div>

      <div className="studio-navigation-footer">
        <span className="studio-status-dot" />

        <div>
          <strong>Canon connected</strong>
          <small>Numeria Studio API</small>
        </div>
      </div>
    </nav>
  );
}
