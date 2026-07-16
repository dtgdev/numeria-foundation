import { useMemo } from "react";

import type { CanonEntity } from "../../api";

import "./WorldMap.css";

interface WorldMapProps {
  world: CanonEntity | null;
  regions: CanonEntity[];
  selectedId: string | null;
  onSelect: (entityId: string) => void;
}

interface RegionPosition {
  x: number;
  y: number;
}

const REGION_POSITIONS: RegionPosition[] = [
  { x: 20, y: 28 },
  { x: 50, y: 18 },
  { x: 80, y: 28 },
  { x: 25, y: 72 },
  { x: 50, y: 82 },
  { x: 75, y: 72 },
  { x: 12, y: 50 },
  { x: 88, y: 50 },
];

function getRegionIcon(index: number): string {
  const icons = [
    "🌲",
    "🌄",
    "🏰",
    "🌊",
    "⛰️",
    "🌻",
    "🌌",
    "🏝️",
  ];

  return icons[index % icons.length];
}

function getRegionDomain(
  region: CanonEntity,
): string {
  const domain = region.data.domain;

  if (
    domain &&
    typeof domain === "object" &&
    "name" in domain &&
    typeof domain.name === "string"
  ) {
    return domain.name;
  }

  return "Mathematical Region";
}

export default function WorldMap({
  world,
  regions,
  selectedId,
  onSelect,
}: WorldMapProps) {
  const positionedRegions = useMemo(
    () =>
      regions.map((region, index) => ({
        region,
        position:
          REGION_POSITIONS[
            index % REGION_POSITIONS.length
          ],
        icon: getRegionIcon(index),
      })),
    [regions],
  );

  return (
    <section className="numeria-world-map">
      <header className="numeria-world-map-header">
        <div>
          <p className="world-studio-eyebrow">
            INTERACTIVE WORLD MAP
          </p>

          <h3>Explore Numeria</h3>

          <p>
            Select a region to inspect its
            landmarks, purpose, and place in the
            living mathematical universe.
          </p>
        </div>

        <div className="numeria-world-map-legend">
          <span>
            <i className="legend-world" />
            World
          </span>

          <span>
            <i className="legend-region" />
            Region
          </span>

          <span>
            <i className="legend-selected" />
            Selected
          </span>
        </div>
      </header>

      <div className="numeria-world-map-canvas">
        <div className="numeria-map-stars" />

        <svg
          className="numeria-world-map-edges"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          aria-hidden="true"
        >
          <defs>
            <linearGradient
              id="world-edge-gradient"
              x1="0"
              y1="0"
              x2="1"
              y2="1"
            >
              <stop
                offset="0%"
                stopColor="#7568f5"
                stopOpacity="0.25"
              />

              <stop
                offset="100%"
                stopColor="#5969d8"
                stopOpacity="0.8"
              />
            </linearGradient>
          </defs>

          {positionedRegions.map(
            ({ region, position }) => (
              <line
                key={region.id}
                x1="50"
                y1="50"
                x2={position.x}
                y2={position.y}
                className={
                  selectedId === region.id
                    ? "selected"
                    : ""
                }
              />
            ),
          )}
        </svg>

        <button
          type="button"
          className={[
            "numeria-map-world-node",
            selectedId === world?.id
              ? "selected"
              : "",
          ]
            .filter(Boolean)
            .join(" ")}
          style={{
            left: "50%",
            top: "50%",
          }}
          onClick={() => {
            if (world) {
              onSelect(world.id);
            }
          }}
        >
          <span className="numeria-map-node-glow" />

          <span className="numeria-map-world-icon">
            🌍
          </span>

          <strong>
            {world?.name ?? "Numeria"}
          </strong>

          <small>
            {world?.id ?? "NUM-WLD-000001"}
          </small>
        </button>

        {positionedRegions.map(
          ({
            region,
            position,
            icon,
          }) => {
            const selected =
              selectedId === region.id;

            return (
              <button
                key={region.id}
                type="button"
                className={[
                  "numeria-map-region-node",
                  selected ? "selected" : "",
                ]
                  .filter(Boolean)
                  .join(" ")}
                style={{
                  left: `${position.x}%`,
                  top: `${position.y}%`,
                }}
                onClick={() =>
                  onSelect(region.id)
                }
              >
                <span className="numeria-map-node-glow" />

                <span className="numeria-map-region-icon">
                  {icon}
                </span>

                <span className="numeria-map-region-domain">
                  {getRegionDomain(region)}
                </span>

                <strong>{region.name}</strong>

                <small>{region.id}</small>
              </button>
            );
          },
        )}

        {regions.length === 0 && (
          <div className="numeria-world-map-empty">
            <span>✨</span>

            <strong>
              The universe is waiting
            </strong>

            <p>
              Create a region to place the first
              destination on the Numeria map.
            </p>
          </div>
        )}
      </div>

      <footer className="numeria-world-map-footer">
        <span>
          {regions.length} canonical region
          {regions.length === 1 ? "" : "s"}
        </span>

        <span>
          Click a destination to update the
          Inspector
        </span>
      </footer>
    </section>
  );
}
