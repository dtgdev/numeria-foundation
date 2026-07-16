import type { CanonEntity } from "../../../../api";

import {
  Badge,
  Button,
} from "../../../../components/ui";

import "./HeroBanner.css";

interface HeroBannerProps {
  character: CanonEntity;
  onAddRelationship: () => void;
  onForgeHero: () => void;
}

function readText(
  character: CanonEntity,
  key: string,
  fallback: string,
): string {
  const value = character.data[key];

  return typeof value === "string" &&
    value.trim()
    ? value.trim()
    : fallback;
}

function getInitials(name: string): string {
  const initials = name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");

  return initials || "N";
}

export default function HeroBanner({
  character,
  onAddRelationship,
  onForgeHero,
}: HeroBannerProps) {
  const role = readText(
    character,
    "role",
    "Canon Hero",
  );

  const nickname = readText(
    character,
    "nickname",
    "",
  );

  const summary = readText(
    character,
    "summary",
    "This hero's canonical story is still being written.",
  );

  const signatureQuote = readText(
    character,
    "signature_quote",
    "Every mathematical idea holds a story waiting to be discovered.",
  );

  const colorTheme = readText(
    character,
    "color_theme",
    "Canon Blue and Delta Silver",
  );

  const portraitPath = readText(
    character,
    "portrait_path",
    "",
  );

  return (
    <section className="hero-forge-banner">
      <div className="hero-forge-background-symbol">
        Δ
      </div>

      <div className="hero-forge-portrait-column">
        <div className="hero-forge-portrait-frame">
          <span className="hero-forge-portrait-orbit hero-forge-orbit-one" />
          <span className="hero-forge-portrait-orbit hero-forge-orbit-two" />

          {portraitPath ? (
            <img
              className="hero-forge-portrait-image"
              src={portraitPath}
              alt={`${character.name} portrait`}
            />
          ) : (
            <div
              className="hero-forge-portrait-placeholder"
              aria-label={`${character.name} portrait placeholder`}
            >
              <span>
                {getInitials(character.name)}
              </span>
            </div>
          )}

          <span className="hero-forge-status">
            Canon
          </span>
        </div>

        <p className="hero-forge-color-theme">
          {colorTheme}
        </p>
      </div>

      <div className="hero-forge-content">
        <div className="hero-forge-labels">
          <Badge tone="brand">
            {role}
          </Badge>

          <Badge tone="success">
            Living Canon
          </Badge>
        </div>

        <h2>{character.name}</h2>

        {nickname && (
          <p className="hero-forge-nickname">
            “{nickname}”
          </p>
        )}

        <blockquote>
          “{signatureQuote}”
        </blockquote>

        <p className="hero-forge-summary">
          {summary}
        </p>

        <div className="hero-forge-actions">
          <Button onClick={onAddRelationship}>
            + Forge Relationship
          </Button>

          <Button
            variant="secondary"
            onClick={onForgeHero}
          >
            ✨ Forge Another Hero
          </Button>
        </div>
      </div>
    </section>
  );
}
