import "./StudioNavigation.css";

import { STUDIOS } from "../../../app/StudioRegistry";

export type StudioSection =
  | "dashboard"
  | "characters"
  | "stories"
  | "world"
  | "canon"
  | "relationships";

interface StudioNavigationProps {
  activeSection: StudioSection;
  onSelect: (section: StudioSection) => void;
}

export default function StudioNavigation({
  activeSection,
  onSelect,
}: StudioNavigationProps) {
  return (
    <nav className="studio-navigation">
      <header className="studio-navigation-header">
        <h2>Numeria Studio</h2>
        <p>Creative Operating System</p>
      </header>

      <div className="studio-navigation-list">
        {STUDIOS.map((studio) => (
          <button
            key={studio.id}
            type="button"
            className={[
              "studio-navigation-item",
              activeSection === studio.id ? "active" : "",
            ]
              .filter(Boolean)
              .join(" ")}
            onClick={() => onSelect(studio.id as StudioSection)}
          >
            <span className="studio-navigation-icon">
              {studio.icon}
            </span>

            <div>
              <strong>{studio.title}</strong>
              <small>{studio.description}</small>
            </div>
          </button>
        ))}

        <button
          type="button"
          className={[
            "studio-navigation-item",
            activeSection === "relationships" ? "active" : "",
          ]
            .filter(Boolean)
            .join(" ")}
          onClick={() => onSelect("relationships")}
        >
          <span className="studio-navigation-icon">🔗</span>

          <div>
            <strong>Relationships</strong>
            <small>Canon Graph</small>
          </div>
        </button>
      </div>
    </nav>
  );
}
