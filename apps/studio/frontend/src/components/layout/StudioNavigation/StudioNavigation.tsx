import "./StudioNavigation.css";

import {
  STUDIOS,
  type StudioSection,
} from "../../../app/StudioRegistry";

export type { StudioSection };

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
            onClick={() => onSelect(studio.id)}
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
      </div>
    </nav>
  );
}
