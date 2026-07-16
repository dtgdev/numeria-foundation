import { useEffect, useMemo, useState } from "react";

import type { CanonEntity } from "../../../api";

import {
  publishRelationship,
  validateRelationship,
} from "../../../api/relationships";

import type {
  PublishedRelationship,
  RelationshipDraft,
  RelationshipValidationResult,
} from "../../../api/relationships";

import {
  Badge,
  Button,
  Card,
  Dialog,
  FormField,
  StatusMessage,
  TextArea,
  TextInput,
} from "../../ui";

import "./RelationshipCreatorDialog.css";

interface RelationshipCreatorDialogProps {
  open: boolean;
  sourceEntity: CanonEntity | null;
  entities: CanonEntity[];
  onClose: () => void;
  onPublished: (
    relationship: PublishedRelationship,
  ) => void;
}

const RELATIONSHIP_TYPES = [
  "TEACHES",
  "EXPLAINS",
  "APPEARS_IN",
  "FRIEND_OF",
  "MENTORS",
  "USES",
  "OWNS",
  "DISCOVERS",
  "LIVES_IN",
  "PART_OF",
  "RELATED_TO",
];

export default function RelationshipCreatorDialog({
  open,
  sourceEntity,
  entities,
  onClose,
  onPublished,
}: RelationshipCreatorDialogProps) {
  const [relationshipType, setRelationshipType] =
    useState("TEACHES");

  const [targetId, setTargetId] = useState("");
  const [targetQuery, setTargetQuery] = useState("");
  const [summary, setSummary] = useState("");

  const [validation, setValidation] =
    useState<RelationshipValidationResult | null>(null);

  const [published, setPublished] =
    useState<PublishedRelationship | null>(null);

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [showErrors, setShowErrors] = useState(false);

  useEffect(() => {
    if (!open) {
      return;
    }

    setRelationshipType("TEACHES");
    setTargetId("");
    setTargetQuery("");
    setSummary("");
    setValidation(null);
    setPublished(null);
    setBusy(false);
    setError("");
    setShowErrors(false);
  }, [open, sourceEntity?.id]);

  const availableTargets = useMemo(() => {
    const normalizedQuery =
      targetQuery.trim().toLowerCase();

    return entities
      .filter(
        (entity) =>
          entity.id !== sourceEntity?.id,
      )
      .filter((entity) => {
        if (!normalizedQuery) {
          return true;
        }

        return (
          entity.name
            .toLowerCase()
            .includes(normalizedQuery) ||
          entity.id
            .toLowerCase()
            .includes(normalizedQuery) ||
          entity.type
            .toLowerCase()
            .includes(normalizedQuery)
        );
      })
      .slice(0, 30);
  }, [entities, sourceEntity?.id, targetQuery]);

  const selectedTarget =
    entities.find((entity) => entity.id === targetId) ??
    null;

  const draft: RelationshipDraft | null =
    sourceEntity && targetId
      ? {
          type: relationshipType,
          source: sourceEntity.id,
          target: targetId,
          summary: summary.trim() || undefined,
        }
      : null;

  const typeError =
    relationshipType.trim().length < 2
      ? "Choose a relationship type."
      : undefined;

  const targetError = !targetId
    ? "Choose a target canon entity."
    : undefined;

  const formIsComplete =
    !typeError &&
    !targetError &&
    Boolean(sourceEntity);

  function clearResult() {
    setValidation(null);
    setPublished(null);
    setError("");
  }

  async function handleValidate() {
    setShowErrors(true);
    setError("");
    setPublished(null);

    if (!formIsComplete || !draft) {
      return;
    }

    setBusy(true);

    try {
      const result =
        await validateRelationship(draft);

      setValidation(result);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Relationship validation failed.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function handlePublish() {
    setShowErrors(true);
    setError("");

    if (
      !draft ||
      !formIsComplete ||
      !validation?.valid
    ) {
      return;
    }

    setBusy(true);

    try {
      const result =
        await publishRelationship(draft);

      setPublished(result);
      onPublished(result);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Relationship publication failed.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <Dialog
      open={open}
      title="Relationship Studio"
      description="Connect canon objects and grow the living Numeria universe."
      width="large"
      onClose={onClose}
      footer={
        <>
          <Button
            variant="secondary"
            onClick={onClose}
            disabled={busy}
          >
            Close
          </Button>

          <Button
            variant="secondary"
            onClick={handleValidate}
            disabled={busy}
          >
            {busy ? "Working..." : "Validate Relationship"}
          </Button>

          <Button
            onClick={handlePublish}
            disabled={
              busy ||
              !formIsComplete ||
              !validation?.valid ||
              Boolean(published)
            }
          >
            Publish Relationship
          </Button>
        </>
      }
    >
      <div className="relationship-studio-layout">
        <div className="relationship-editor-column">
          <Card
            title="Source"
            description="The selected canon object where this relationship begins."
          >
            {sourceEntity ? (
              <div className="relationship-source-card">
                <Badge tone="brand">
                  {sourceEntity.type}
                </Badge>

                <strong>{sourceEntity.name}</strong>
                <small>{sourceEntity.id}</small>
              </div>
            ) : (
              <StatusMessage
                tone="warning"
                title="No source selected"
              >
                Select an entity in Canon Explorer first.
              </StatusMessage>
            )}
          </Card>

          <FormField
            label="Relationship type"
            htmlFor="relationship-type"
            required
            error={
              showErrors ? typeError : undefined
            }
          >
            <select
              id="relationship-type"
              className="numeria-select"
              value={relationshipType}
              onChange={(event) => {
                setRelationshipType(event.target.value);
                clearResult();
              }}
            >
              {RELATIONSHIP_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type.replaceAll("_", " ")}
                </option>
              ))}
            </select>
          </FormField>

          <FormField
            label="Find target"
            htmlFor="relationship-target-search"
            description="Search by name, ID, or canon type."
            required
            error={
              showErrors ? targetError : undefined
            }
          >
            <TextInput
              id="relationship-target-search"
              value={targetQuery}
              invalid={
                showErrors && Boolean(targetError)
              }
              onChange={(event) => {
                setTargetQuery(event.target.value);
              }}
              placeholder="Search characters, concepts, books, scenes..."
            />
          </FormField>

          <div className="relationship-target-grid">
            {availableTargets.map((entity) => {
              const summary =
                typeof entity.data.summary === "string"
                  ? entity.data.summary
                  : typeof entity.data.description === "string"
                    ? entity.data.description
                    : "No summary available yet.";

              return (
                <button
                  key={entity.id}
                  type="button"
                  className={`relationship-target-card ${
                    entity.id === targetId
                      ? "selected"
                      : ""
                  }`}
                  onClick={() => {
                    setTargetId(entity.id);
                    setTargetQuery(entity.name);
                    clearResult();
                  }}
                >
                  <div className="relationship-target-card-heading">
                    <Badge
                      tone={
                        entity.id === targetId
                          ? "brand"
                          : "neutral"
                      }
                    >
                      {entity.type}
                    </Badge>

                    {entity.id === targetId && (
                      <span className="relationship-selected-label">
                        Selected
                      </span>
                    )}
                  </div>

                  <strong>{entity.name}</strong>
                  <p>{summary}</p>
                  <small>{entity.id}</small>
                </button>
              );
            })}

            {availableTargets.length === 0 && (
              <p className="relationship-empty-state">
                No matching canon objects.
              </p>
            )}
          </div>

          <FormField
            label="Relationship summary"
            htmlFor="relationship-summary"
            description="Explain why this relationship belongs in the canon."
          >
            <TextArea
              id="relationship-summary"
              value={summary}
              onChange={(event) => {
                setSummary(event.target.value);
                clearResult();
              }}
              placeholder="Captain Chain Rule teaches composition because connected functions create connected change."
              rows={4}
            />
          </FormField>
        </div>

        <aside className="relationship-preview-column">
          <Card
            title="Relationship Preview"
            description="Review the new canon connection before publishing."
          >
            <div className="relationship-preview">
              <div className="relationship-preview-node">
                <Badge tone="brand">
                  {sourceEntity?.type ?? "Source"}
                </Badge>

                <strong>
                  {sourceEntity?.name ??
                    "Select a source"}
                </strong>

                <small>
                  {sourceEntity?.id ?? "—"}
                </small>
              </div>

              <div className="relationship-preview-edge">
                <span>
                  {relationshipType.replaceAll(
                    "_",
                    " ",
                  )}
                </span>
                <div aria-hidden="true">↓</div>
              </div>

              <div className="relationship-preview-node">
                <Badge
                  tone={
                    selectedTarget
                      ? "success"
                      : "neutral"
                  }
                >
                  {selectedTarget?.type ?? "Target"}
                </Badge>

                <strong>
                  {selectedTarget?.name ??
                    "Choose a target"}
                </strong>

                <small>
                  {selectedTarget?.id ?? "—"}
                </small>
              </div>
            </div>
          </Card>

          {error && (
            <StatusMessage
              tone="danger"
              title="Relationship Studio error"
            >
              {error}
            </StatusMessage>
          )}

          {validation && (
            <StatusMessage
              tone={
                validation.valid
                  ? "success"
                  : "danger"
              }
              title={
                validation.valid
                  ? "Relationship is ready"
                  : "Relationship requires changes"
              }
            >
              {validation.proposed_id && (
                <p>
                  Proposed ID:{" "}
                  {validation.proposed_id}
                </p>
              )}

              {validation.proposed_path && (
                <p>{validation.proposed_path}</p>
              )}

              {validation.errors.map((message) => (
                <p key={message}>{message}</p>
              ))}

              {validation.warnings.map((message) => (
                <p key={message}>
                  Warning: {message}
                </p>
              ))}
            </StatusMessage>
          )}

          {published && (
            <StatusMessage
              tone="success"
              title="Published to Canon"
            >
              <p>{published.message}</p>
              <p>
                {published.source}
                {" → "}
                {published.type}
                {" → "}
                {published.target}
              </p>
              <p>{published.path}</p>
            </StatusMessage>
          )}
        </aside>
      </div>
    </Dialog>
  );
}
