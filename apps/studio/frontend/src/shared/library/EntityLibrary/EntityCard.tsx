import type { ReactNode } from "react";

import {
  Badge,
} from "../../../components/ui";

interface EntityCardProps {
  id: string;
  name: string;
  type: string;
  selected?: boolean;
  description?: string;
  icon?: ReactNode;
  meta?: ReactNode;
  onSelect: () => void;
}

export default function EntityCard({
  id,
  name,
  type,
  selected = false,
  description,
  icon,
  meta,
  onSelect,
}: EntityCardProps) {
  return (
    <button
      type="button"
      className={[
        "entity-library-card",
        selected ? "selected" : "",
      ]
        .filter(Boolean)
        .join(" ")}
      onClick={onSelect}
    >
      <div className="entity-library-card-icon">
        {icon ?? name.slice(0, 2).toUpperCase()}
      </div>

      <div className="entity-library-card-content">
        <div className="entity-library-card-heading">
          <Badge
            tone={
              selected
                ? "brand"
                : "neutral"
            }
          >
            {type}
          </Badge>

          {selected && (
            <span className="entity-library-selected">
              Selected
            </span>
          )}
        </div>

        <strong>{name}</strong>

        {description && (
          <p>{description}</p>
        )}

        <div className="entity-library-card-footer">
          <small>{id}</small>

          {meta && (
            <span>{meta}</span>
          )}
        </div>
      </div>
    </button>
  );
}
