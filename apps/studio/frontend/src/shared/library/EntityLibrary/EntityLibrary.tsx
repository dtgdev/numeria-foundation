import type {
  ReactNode,
} from "react";

import {
  Button,
} from "../../../components/ui";

import EntityCard from "./EntityCard";

import "./EntityLibrary.css";

export interface EntityLibraryItem {
  id: string;
  name: string;
  type: string;
  description?: string;
}

interface EntityLibraryProps<
  TEntity extends EntityLibraryItem,
> {
  title: string;
  eyebrow?: string;
  description?: string;
  entities: TEntity[];
  selectedId: string | null;
  emptyTitle?: string;
  emptyDescription?: string;
  actionLabel?: string;
  searchValue?: string;
  searchPlaceholder?: string;
  renderIcon?: (
    entity: TEntity,
  ) => ReactNode;
  renderMeta?: (
    entity: TEntity,
  ) => ReactNode;
  onSelect: (
    entityId: string,
  ) => void;
  onAction?: () => void;
  onSearchChange?: (
    value: string,
  ) => void;
}

export default function EntityLibrary<
  TEntity extends EntityLibraryItem,
>({
  title,
  eyebrow = "NUMERIA CANON",
  description,
  entities,
  selectedId,
  emptyTitle = "Nothing here yet",
  emptyDescription =
    "Create the first canon object for this Forge.",
  actionLabel,
  searchValue,
  searchPlaceholder =
    "Search the library...",
  renderIcon,
  renderMeta,
  onSelect,
  onAction,
  onSearchChange,
}: EntityLibraryProps<TEntity>) {
  return (
    <div className="entity-library">
      <header className="entity-library-header">
        <p className="entity-library-eyebrow">
          {eyebrow}
        </p>

        <h2>{title}</h2>

        {description && (
          <p>{description}</p>
        )}
      </header>

      {onAction && actionLabel && (
        <Button
          fullWidth
          onClick={onAction}
        >
          {actionLabel}
        </Button>
      )}

      {onSearchChange && (
        <input
          className="entity-library-search"
          value={searchValue ?? ""}
          onChange={(event) =>
            onSearchChange(
              event.target.value,
            )
          }
          placeholder={searchPlaceholder}
          aria-label={searchPlaceholder}
        />
      )}

      <div className="entity-library-list">
        {entities.map((entity) => (
          <EntityCard
            key={entity.id}
            id={entity.id}
            name={entity.name}
            type={entity.type}
            selected={
              selectedId === entity.id
            }
            description={
              entity.description
            }
            icon={
              renderIcon?.(entity)
            }
            meta={
              renderMeta?.(entity)
            }
            onSelect={() =>
              onSelect(entity.id)
            }
          />
        ))}

        {entities.length === 0 && (
          <div className="entity-library-empty">
            <span>✨</span>

            <strong>
              {emptyTitle}
            </strong>

            <p>
              {emptyDescription}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
