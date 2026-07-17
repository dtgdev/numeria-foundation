import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Numeria,
} from "../../engine";

import type {
  CanonValidation,
} from "../../engine";

import "./DashboardStudio.css";

type CanonEntities =
  Awaited<
    ReturnType<typeof Numeria.canon.list>
  >;

function healthLabel(score: number): string {
  if (score >= 90) {
    return "Excellent";
  }

  if (score >= 75) {
    return "Healthy";
  }

  if (score >= 50) {
    return "Needs Attention";
  }

  return "Critical";
}

function severityClass(
  severity: "info" | "warning" | "critical",
): string {
  return `dashboard-issue-severity ${severity}`;
}

export default function DashboardStudio() {
  const [entities, setEntities] =
    useState<CanonEntities>([]);

  const [validation, setValidation] =
    useState<CanonValidation | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [validating, setValidating] =
    useState(false);

  const [error, setError] =
    useState("");

  const loadDashboard =
    useCallback(async () => {
      setLoading(true);
      setError("");

      try {
        const [
          canonEntities,
          canonValidation,
        ] = await Promise.all([
          Numeria.canon.list(),
          Numeria.director.validateUniverse(),
        ]);

        setEntities(canonEntities);
        setValidation(canonValidation);
      } catch (caughtError) {
        setError(
          caughtError instanceof Error
            ? caughtError.message
            : "The Numeria universe could not be loaded.",
        );
      } finally {
        setLoading(false);
      }
    }, []);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  const counts = useMemo(() => {
    return entities.reduce<
      Record<string, number>
    >((result, entity) => {
      result[entity.type] =
        (result[entity.type] ?? 0) + 1;

      return result;
    }, {});
  }, [entities]);

  async function validateUniverse() {
    setValidating(true);
    setError("");

    try {
      const result =
        await Numeria.director.validateUniverse();

      setValidation(result);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Universe validation failed.",
      );
    } finally {
      setValidating(false);
    }
  }

  const score = validation?.score ?? 0;

  return (
    <main className="dashboard-studio">
      <header className="dashboard-hero">
        <div>
          <span className="dashboard-eyebrow">
            Numeria Mission Control
          </span>

          <h1>
            Universe Dashboard
          </h1>

          <p>
            Monitor the health, structure,
            and educational integrity of the
            Numeria universe.
          </p>
        </div>

        <button
          type="button"
          className="dashboard-primary-action"
          onClick={() =>
            void validateUniverse()
          }
          disabled={validating}
        >
          {validating
            ? "Validating..."
            : "Validate Universe"}
        </button>
      </header>

      {error && (
        <div className="dashboard-error">
          {error}
        </div>
      )}

      {loading ? (
        <div className="dashboard-loading">
          Loading the Numeria universe...
        </div>
      ) : (
        <>
          <section className="dashboard-overview">
            <article className="dashboard-health-card">
              <div
                className="dashboard-health-ring"
                aria-label={`Universe health ${score} out of 100`}
              >
                <strong>{score}</strong>
                <span>/ 100</span>
              </div>

              <div>
                <span className="dashboard-card-label">
                  Universe Health
                </span>

                <h2>
                  {healthLabel(score)}
                </h2>

                <p>
                  {validation?.connectedEntities ?? 0}
                  {" of "}
                  {validation?.totalEntities ?? 0}
                  {" canon entities are connected."}
                </p>
              </div>
            </article>

            <article className="dashboard-summary-card">
              <span className="dashboard-card-label">
                Canon Overview
              </span>

              <strong>
                {entities.length}
              </strong>

              <p>
                Total entities currently
                registered in Numeria canon.
              </p>
            </article>

            <article className="dashboard-summary-card">
              <span className="dashboard-card-label">
                Open Issues
              </span>

              <strong>
                {validation?.issues.length ?? 0}
              </strong>

              <p>
                Canon and educational findings
                requiring creator review.
              </p>
            </article>
          </section>

          <section className="dashboard-section">
            <div className="dashboard-section-heading">
              <div>
                <span className="dashboard-eyebrow">
                  Canon Statistics
                </span>

                <h2>
                  Universe Composition
                </h2>
              </div>
            </div>

            <div className="dashboard-stat-grid">
              {[
                ["character", "Heroes"],
                ["story", "Stories"],
                ["region", "Regions"],
                ["concept", "Concepts"],
                ["lesson", "Lessons"],
                ["artifact", "Artifacts"],
                ["relationship", "Relationships"],
                ["book", "Books"],
              ].map(([type, label]) => (
                <article
                  key={type}
                  className="dashboard-stat-card"
                >
                  <span>{label}</span>

                  <strong>
                    {counts[type] ?? 0}
                  </strong>
                </article>
              ))}
            </div>
          </section>

          <section className="dashboard-section">
            <div className="dashboard-section-heading">
              <div>
                <span className="dashboard-eyebrow">
                  Intelligence
                </span>

                <h2>
                  Canon Findings
                </h2>
              </div>

              <span className="dashboard-issue-count">
                {validation?.issues.length ?? 0}
                {" findings"}
              </span>
            </div>

            {!validation ||
            validation.issues.length === 0 ? (
              <div className="dashboard-success">
                <span>✓</span>

                <div>
                  <strong>
                    No foundational issues found
                  </strong>

                  <p>
                    The current universe passes
                    all available canon checks.
                  </p>
                </div>
              </div>
            ) : (
              <div className="dashboard-issue-list">
                {validation.issues.map(
                  (issue) => (
                    <article
                      key={issue.id}
                      className="dashboard-issue-card"
                    >
                      <div className="dashboard-issue-heading">
                        <span
                          className={severityClass(
                            issue.severity,
                          )}
                        >
                          {issue.severity}
                        </span>

                        <span className="dashboard-issue-entity">
                          {issue.entityType}
                          {" · "}
                          {issue.entityId}
                        </span>
                      </div>

                      <strong>
                        {issue.title}
                      </strong>

                      <p>
                        {issue.message}
                      </p>
                    </article>
                  ),
                )}
              </div>
            )}
          </section>
        </>
      )}
    </main>
  );
}
