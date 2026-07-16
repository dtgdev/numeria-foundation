import type { CanonEntity } from "../../api";

import {
  Badge,
  Button,
  Card,
} from "../../components/ui";

import {
  useStudio,
} from "../../hooks";

import WorldMap from "./WorldMap";

import "./WorldStudio.css";

interface WorldStudioProps {
  onCreateRegion: () => void;
}

export default function WorldStudio({
  onCreateRegion,
}: WorldStudioProps) {
  const {
    worlds,
    regions,
    selectedId,
    selectEntity,
  } = useStudio();

  const world = worlds[0] ?? null;

  function readText(
    entity: CanonEntity | null,
    key: string,
    fallback: string,
  ): string {
    const value = entity?.data[key];

    return typeof value === "string" &&
      value.trim()
      ? value
      : fallback;
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

  function getRegionAtmosphere(
    region: CanonEntity,
  ): string[] {
    const visualIdentity =
      region.data.visual_identity;

    if (
      !visualIdentity ||
      typeof visualIdentity !== "object" ||
      !("atmosphere" in visualIdentity) ||
      !Array.isArray(
        visualIdentity.atmosphere,
      )
    ) {
      return [];
    }

    return visualIdentity.atmosphere
      .filter(
        (
          value,
        ): value is string =>
          typeof value === "string",
      )
      .slice(0, 4);
  }

  function getRegionLandmarks(
    region: CanonEntity,
  ): string[] {
    const visualIdentity =
      region.data.visual_identity;

    if (
      !visualIdentity ||
      typeof visualIdentity !== "object" ||
      !("landmarks" in visualIdentity) ||
      !Array.isArray(
        visualIdentity.landmarks,
      )
    ) {
      return [];
    }

    return visualIdentity.landmarks
      .filter(
        (
          value,
        ): value is string =>
          typeof value === "string",
      )
      .slice(0, 3);
  }

  return (
    <div className="world-studio">
      <section className="world-studio-hero">
        <div className="world-studio-orb">
          <div className="world-studio-orb-core">
            🌍
          </div>

          <span className="world-studio-orbit world-studio-orbit-one" />
          <span className="world-studio-orbit world-studio-orbit-two" />
        </div>

        <div className="world-studio-hero-content">
          <Badge tone="brand">
            Living Mathematical Universe
          </Badge>

          <h2>
            {world?.name ?? "Numeria"}
          </h2>

          <p>
            {readText(
              world,
              "summary",
              "A living educational universe where mathematical ideas become characters, places, stories, discoveries, and adventures.",
            )}
          </p>

          <div className="world-studio-hero-metrics">
            <div>
              <strong>
                {regions.length}
              </strong>

              <span>Canonical Regions</span>
            </div>

            <div>
              <strong>
                {world ? "1" : "0"}
              </strong>

              <span>Living World</span>
            </div>

            <div>
              <strong>Genesis</strong>

              <span>Current Era</span>
            </div>
          </div>
        </div>
      </section>

      <section className="world-studio-section">
        <div className="world-studio-section-heading">
          <div>
            <p className="world-studio-eyebrow">
              EXPLORE NUMERIA
            </p>

            <h3>Canonical Regions</h3>

            <p>
              Every region gives mathematical
              ideas a memorable place to live,
              change, and become part of a story.
            </p>
          </div>

          <Button onClick={onCreateRegion}>
            + Create Region
          </Button>
        </div>

        <div className="world-studio-region-grid">
          {regions.map((region, index) => {
            const selected =
              selectedId === region.id;

            const landmarks =
              getRegionLandmarks(region);

            const atmosphere =
              getRegionAtmosphere(region);

            return (
              <button
                key={region.id}
                type="button"
                className={[
                  "world-region-card",
                  selected
                    ? "selected"
                    : "",
                ]
                  .filter(Boolean)
                  .join(" ")}
                onClick={() =>
                  selectEntity(region.id)
                }
              >
                <div className="world-region-visual">
                  <span>
                    {index % 4 === 0
                      ? "🌲"
                      : index % 4 === 1
                        ? "🌄"
                        : index % 4 === 2
                          ? "🏰"
                          : "🌊"}
                  </span>
                </div>

                <div className="world-region-content">
                  <div className="world-region-heading">
                    <Badge
                      tone={
                        selected
                          ? "brand"
                          : "neutral"
                      }
                    >
                      {getRegionDomain(region)}
                    </Badge>

                    {selected && (
                      <span className="world-region-selected">
                        Selected
                      </span>
                    )}
                  </div>

                  <h4>{region.name}</h4>

                  <p>
                    {readText(
                      region,
                      "summary",
                      "A canonical territory within Numeria.",
                    )}
                  </p>

                  {atmosphere.length > 0 && (
                    <div className="world-region-tags">
                      {atmosphere.map(
                        (item) => (
                          <span key={item}>
                            {item}
                          </span>
                        ),
                      )}
                    </div>
                  )}

                  {landmarks.length > 0 && (
                    <div className="world-region-landmarks">
                      <strong>
                        Landmarks
                      </strong>

                      <ul>
                        {landmarks.map(
                          (landmark) => (
                            <li key={landmark}>
                              {landmark}
                            </li>
                          ),
                        )}
                      </ul>
                    </div>
                  )}

                  <small>{region.id}</small>
                </div>
              </button>
            );
          })}

          {regions.length === 0 && (
            <Card
              title="The World Is Waiting"
              description="Create the first canonical region inside Numeria."
            >
              <Button onClick={onCreateRegion}>
                Create the First Region
              </Button>
            </Card>
          )}
        </div>
      </section>

      <WorldMap
        world={world}
        regions={regions}
        selectedId={selectedId}
        onSelect={selectEntity}
      />
    </div>
  );
}
