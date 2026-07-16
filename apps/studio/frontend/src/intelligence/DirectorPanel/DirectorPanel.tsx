import type {
  StoryAnalysis,
} from "../../engine";

import {
  Badge,
  Button,
  Card,
} from "../../components/ui";

import "./DirectorPanel.css";

interface DirectorPanelProps {
  analysis: StoryAnalysis | null;
  loading: boolean;
  error: string;
  onAnalyze: () => void;
}

function severityTone(
  severity: "info" | "warning" | "critical",
): "neutral" | "warning" | "danger" {
  if (severity === "critical") {
    return "danger";
  }

  if (severity === "warning") {
    return "warning";
  }

  return "neutral";
}

function scoreLabel(score: number): string {
  if (score >= 85) {
    return "Strong";
  }

  if (score >= 60) {
    return "Developing";
  }

  return "Needs Attention";
}

export default function DirectorPanel({
  analysis,
  loading,
  error,
  onAnalyze,
}: DirectorPanelProps) {
  return (
    <Card
      title="AI Story Director"
      description="Analyze educational alignment, story structure, and canon completeness."
      action={
        <Button
          onClick={onAnalyze}
          disabled={loading}
        >
          {loading
            ? "Analyzing..."
            : "✨ Analyze Story"}
        </Button>
      }
    >
      <div className="director-panel">
        {error && (
          <div className="director-panel-error">
            {error}
          </div>
        )}

        {!analysis && !error && (
          <div className="director-panel-empty">
            <span>✨</span>

            <strong>
              Your creative director is ready
            </strong>

            <p>
              Analyze this story to receive
              structured recommendations.
            </p>
          </div>
        )}

        {analysis && (
          <>
            <section className="director-score">
              <div className="director-score-ring">
                <strong>
                  {analysis.score}
                </strong>

                <span>/ 100</span>
              </div>

              <div>
                <Badge
                  tone={
                    analysis.score >= 85
                      ? "success"
                      : analysis.score >= 60
                        ? "warning"
                        : "danger"
                  }
                >
                  {scoreLabel(
                    analysis.score,
                  )}
                </Badge>

                <h3>Story Health</h3>

                <p>
                  A structured review of this
                  story's current canon state.
                </p>
              </div>
            </section>

            <section className="director-suggestions">
              <div className="director-section-heading">
                <h3>Recommendations</h3>

                <Badge tone="neutral">
                  {
                    analysis.suggestions
                      .length
                  }
                  {" "}
                  findings
                </Badge>
              </div>

              {analysis.suggestions.length ===
              0 ? (
                <div className="director-success">
                  <span>✓</span>

                  <div>
                    <strong>
                      No issues detected
                    </strong>

                    <p>
                      This story currently passes
                      the foundational Director
                      checks.
                    </p>
                  </div>
                </div>
              ) : (
                analysis.suggestions.map(
                  (suggestion) => (
                    <article
                      key={suggestion.id}
                      className={[
                        "director-suggestion",
                        suggestion.severity,
                      ].join(" ")}
                    >
                      <div className="director-suggestion-heading">
                        <Badge
                          tone={severityTone(
                            suggestion.severity,
                          )}
                        >
                          {suggestion.severity}
                        </Badge>

                        <span>
                          {suggestion.category.replaceAll(
                            "-",
                            " ",
                          )}
                        </span>
                      </div>

                      <strong>
                        {suggestion.title}
                      </strong>

                      <p>
                        {suggestion.message}
                      </p>
                    </article>
                  ),
                )
              )}
            </section>
          </>
        )}
      </div>
    </Card>
  );
}
