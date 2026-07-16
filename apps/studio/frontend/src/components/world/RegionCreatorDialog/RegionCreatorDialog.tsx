import { useMemo, useState } from "react";

import {
  publishRegion,
  validateRegion,
} from "../../../api/world";

import type {
  PublishedRegion,
  RegionDraft,
  RegionValidationResult,
} from "../../../api/world";

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

import "./RegionCreatorDialog.css";

interface RegionCreatorDialogProps {
  open: boolean;
  onClose: () => void;
  onPublished: (region: PublishedRegion) => void;
}

interface FieldErrors {
  name?: string;
  domain?: string;
  summary?: string;
  educationalMission?: string;
}

const EMPTY_DRAFT: RegionDraft = {
  name: "",
  world_id: "NUM-WLD-000001",
  domain: "",
  summary: "",
  educational_mission: "",
  themes: [],
  atmosphere: [],
  landmark_ideas: [],
};

function splitList(value: string): string[] {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function getFieldErrors(
  draft: RegionDraft,
): FieldErrors {
  const errors: FieldErrors = {};

  if (draft.name.trim().length < 2) {
    errors.name =
      "Region name must contain at least 2 characters.";
  }

  if (draft.domain.trim().length < 2) {
    errors.domain =
      "Domain must contain at least 2 characters.";
  }

  if (draft.summary.trim().length < 10) {
    errors.summary =
      "Summary must contain at least 10 characters.";
  }

  if (
    draft.educational_mission.trim().length < 10
  ) {
    errors.educationalMission =
      "Educational mission must contain at least 10 characters.";
  }

  return errors;
}

export default function RegionCreatorDialog({
  open,
  onClose,
  onPublished,
}: RegionCreatorDialogProps) {
  const [draft, setDraft] =
    useState<RegionDraft>(EMPTY_DRAFT);

  const [themesText, setThemesText] =
    useState("");

  const [atmosphereText, setAtmosphereText] =
    useState("");

  const [landmarksText, setLandmarksText] =
    useState("");

  const [validation, setValidation] =
    useState<RegionValidationResult | null>(null);

  const [published, setPublished] =
    useState<PublishedRegion | null>(null);

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const [showFieldErrors, setShowFieldErrors] =
    useState(false);

  const normalizedDraft = useMemo<RegionDraft>(
    () => ({
      ...draft,
      themes: splitList(themesText),
      atmosphere: splitList(atmosphereText),
      landmark_ideas: splitList(landmarksText),
    }),
    [
      draft,
      themesText,
      atmosphereText,
      landmarksText,
    ],
  );

  const fieldErrors = useMemo(
    () => getFieldErrors(normalizedDraft),
    [normalizedDraft],
  );

  const formIsComplete =
    Object.keys(fieldErrors).length === 0;

  function updateField(
    field: keyof RegionDraft,
    value: string,
  ) {
    setDraft((current) => ({
      ...current,
      [field]: value,
    }));

    setValidation(null);
    setPublished(null);
    setError("");
  }

  function clearResults() {
    setValidation(null);
    setPublished(null);
    setError("");
  }

  function reset() {
    setDraft(EMPTY_DRAFT);
    setThemesText("");
    setAtmosphereText("");
    setLandmarksText("");
    setValidation(null);
    setPublished(null);
    setBusy(false);
    setError("");
    setShowFieldErrors(false);
  }

  function closeDialog() {
    reset();
    onClose();
  }

  async function handleValidate() {
    setShowFieldErrors(true);
    setError("");
    setPublished(null);

    if (!formIsComplete) {
      return;
    }

    setBusy(true);

    try {
      const result =
        await validateRegion(normalizedDraft);

      setValidation(result);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Region validation failed.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function handlePublish() {
    setShowFieldErrors(true);
    setError("");

    if (
      !formIsComplete ||
      !validation?.valid
    ) {
      return;
    }

    setBusy(true);

    try {
      const result =
        await publishRegion(normalizedDraft);

      setPublished(result);
      onPublished(result);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Region publication failed.",
      );
    } finally {
      setBusy(false);
    }
  }

  const previewName =
    draft.name.trim() || "Unnamed Region";

  const previewSummary =
    draft.summary.trim() ||
    "This region's story and mathematical purpose will appear here.";

  return (
    <Dialog
      open={open}
      title="Create a Numeria Region"
      description="Design, validate, and publish a new territory inside the Numeria world."
      width="large"
      onClose={closeDialog}
      footer={
        <>
          <Button
            variant="secondary"
            onClick={closeDialog}
            disabled={busy}
          >
            Close
          </Button>

          <Button
            variant="secondary"
            onClick={handleValidate}
            disabled={busy}
          >
            {busy ? "Working..." : "Validate Region"}
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
            Publish Region
          </Button>
        </>
      }
    >
      <div className="region-creator-layout">
        <div className="region-form">
          {!formIsComplete && showFieldErrors && (
            <StatusMessage
              tone="warning"
              title="Complete the required fields"
            >
              Fix the highlighted fields before validating.
            </StatusMessage>
          )}

          <div className="region-form-grid">
            <FormField
              label="Region name"
              htmlFor="region-name"
              required
              error={
                showFieldErrors
                  ? fieldErrors.name
                  : undefined
              }
            >
              <TextInput
                id="region-name"
                value={draft.name}
                invalid={
                  showFieldErrors &&
                  Boolean(fieldErrors.name)
                }
                onChange={(event) =>
                  updateField(
                    "name",
                    event.target.value,
                  )
                }
                placeholder="Valley of Change"
              />
            </FormField>

            <FormField
              label="Mathematical domain"
              htmlFor="region-domain"
              required
              error={
                showFieldErrors
                  ? fieldErrors.domain
                  : undefined
              }
            >
              <TextInput
                id="region-domain"
                value={draft.domain}
                invalid={
                  showFieldErrors &&
                  Boolean(fieldErrors.domain)
                }
                onChange={(event) =>
                  updateField(
                    "domain",
                    event.target.value,
                  )
                }
                placeholder="Calculus"
              />
            </FormField>
          </div>

          <FormField
            label="Summary"
            htmlFor="region-summary"
            required
            error={
              showFieldErrors
                ? fieldErrors.summary
                : undefined
            }
          >
            <TextArea
              id="region-summary"
              value={draft.summary}
              invalid={
                showFieldErrors &&
                Boolean(fieldErrors.summary)
              }
              onChange={(event) =>
                updateField(
                  "summary",
                  event.target.value,
                )
              }
              placeholder="Describe this region and what makes it memorable."
              rows={4}
            />
          </FormField>

          <FormField
            label="Educational mission"
            htmlFor="region-mission"
            required
            error={
              showFieldErrors
                ? fieldErrors.educationalMission
                : undefined
            }
          >
            <TextArea
              id="region-mission"
              value={draft.educational_mission}
              invalid={
                showFieldErrors &&
                Boolean(
                  fieldErrors.educationalMission,
                )
              }
              onChange={(event) =>
                updateField(
                  "educational_mission",
                  event.target.value,
                )
              }
              placeholder="What should learners understand by exploring this region?"
              rows={4}
            />
          </FormField>

          <FormField
            label="Themes"
            htmlFor="region-themes"
            description="Separate themes with commas."
          >
            <TextInput
              id="region-themes"
              value={themesText}
              onChange={(event) => {
                setThemesText(event.target.value);
                clearResults();
              }}
              placeholder="change, motion, discovery"
            />
          </FormField>

          <FormField
            label="Atmosphere"
            htmlFor="region-atmosphere"
            description="Separate visual qualities with commas."
          >
            <TextInput
              id="region-atmosphere"
              value={atmosphereText}
              onChange={(event) => {
                setAtmosphereText(event.target.value);
                clearResults();
              }}
              placeholder="golden, luminous, adventurous"
            />
          </FormField>

          <FormField
            label="Landmark ideas"
            htmlFor="region-landmarks"
            description="Separate landmarks with commas."
          >
            <TextArea
              id="region-landmarks"
              value={landmarksText}
              onChange={(event) => {
                setLandmarksText(event.target.value);
                clearResults();
              }}
              placeholder="Change River, Slope Hill, Delta Observatory"
              rows={3}
            />
          </FormField>
        </div>

        <aside className="region-preview-column">
          <Card
            title="World Preview"
            description="See how the new region will appear inside Numeria."
          >
            <div className="region-preview">
              <div className="region-preview-world">
                <span>🌍</span>
                <strong>Numeria</strong>
                <small>NUM-WLD-000001</small>
              </div>

              <div className="region-preview-connector">
                ↓ contains
              </div>

              <div className="region-preview-region">
                <span>🌄</span>

                <Badge tone="brand">
                  {draft.domain.trim() || "Region"}
                </Badge>

                <h3>{previewName}</h3>
                <p>{previewSummary}</p>
              </div>

              {normalizedDraft.landmark_ideas.length >
                0 && (
                <div className="region-preview-landmarks">
                  <strong>Landmark Ideas</strong>

                  {normalizedDraft.landmark_ideas.map(
                    (landmark) => (
                      <Badge key={landmark}>
                        {landmark}
                      </Badge>
                    ),
                  )}
                </div>
              )}
            </div>
          </Card>

          {error && (
            <StatusMessage
              tone="danger"
              title="World Studio error"
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
                  ? "Region is ready"
                  : "Region requires changes"
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
              title="Published to Numeria"
            >
              <p>{published.message}</p>
              <p>
                {published.name} — {published.id}
              </p>
              <p>{published.path}</p>
            </StatusMessage>
          )}
        </aside>
      </div>
    </Dialog>
  );
}
