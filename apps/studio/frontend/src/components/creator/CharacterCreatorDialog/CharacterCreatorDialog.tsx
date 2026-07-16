import { useMemo, useState } from "react";

import {
  publishCharacter,
  validateCharacter,
} from "../../../api";

import type {
  CharacterDraft,
  CharacterValidationResult,
  PublishedCharacter,
} from "../../../api";

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

import "./CharacterCreatorDialog.css";

interface CharacterCreatorDialogProps {
  open: boolean;
  onClose: () => void;
  onPublished: (character: PublishedCharacter) => void;
}

const EMPTY_DRAFT: CharacterDraft = {
  name: "",
  nickname: "",
  role: "",
  summary: "",
  personality: [],
  power: "",
  educational_mission: "",
  color_theme: "",
  artwork_prompt: "",
};

export default function CharacterCreatorDialog({
  open,
  onClose,
  onPublished,
}: CharacterCreatorDialogProps) {
  const [draft, setDraft] =
    useState<CharacterDraft>(EMPTY_DRAFT);

  const [personalityText, setPersonalityText] =
    useState("");

  const [validation, setValidation] =
    useState<CharacterValidationResult | null>(null);

  const [published, setPublished] =
    useState<PublishedCharacter | null>(null);

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const normalizedDraft = useMemo<CharacterDraft>(
    () => ({
      ...draft,
      personality: personalityText
        .split(",")
        .map((trait) => trait.trim())
        .filter(Boolean),
    }),
    [draft, personalityText],
  );

  function updateField(
    field: keyof CharacterDraft,
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

  function reset() {
    setDraft(EMPTY_DRAFT);
    setPersonalityText("");
    setValidation(null);
    setPublished(null);
    setError("");
    setBusy(false);
  }

  function closeDialog() {
    reset();
    onClose();
  }

  async function handleValidate() {
    setBusy(true);
    setError("");
    setPublished(null);

    try {
      const result =
        await validateCharacter(normalizedDraft);

      setValidation(result);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Character validation failed.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function handlePublish() {
    setBusy(true);
    setError("");

    try {
      const result =
        await publishCharacter(normalizedDraft);

      setPublished(result);
      onPublished(result);
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : "Character publication failed.",
      );
    } finally {
      setBusy(false);
    }
  }

  const previewName =
    draft.name.trim() || "Unnamed Character";

  const previewMission =
    draft.educational_mission.trim() ||
    "This character's educational mission will appear here.";

  return (
    <Dialog
      open={open}
      title="Create a Canon Character"
      description="Design, validate, and publish a new member of the Numeria universe."
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
            {busy ? "Working..." : "Validate Draft"}
          </Button>

          <Button
            onClick={handlePublish}
            disabled={
              busy ||
              !validation?.valid ||
              Boolean(published)
            }
          >
            Publish to Canon
          </Button>
        </>
      }
    >
      <div className="character-creator-layout">
        <div className="character-form">
          <div className="character-form-grid">
            <FormField
              label="Character name"
              htmlFor="character-name"
              required
            >
              <TextInput
                id="character-name"
                value={draft.name}
                onChange={(event) =>
                  updateField("name", event.target.value)
                }
                placeholder="Captain Chain Rule"
              />
            </FormField>

            <FormField
              label="Nickname"
              htmlFor="character-nickname"
            >
              <TextInput
                id="character-nickname"
                value={draft.nickname ?? ""}
                onChange={(event) =>
                  updateField(
                    "nickname",
                    event.target.value,
                  )
                }
                placeholder="Chain"
              />
            </FormField>

            <FormField
              label="Role"
              htmlFor="character-role"
              required
            >
              <TextInput
                id="character-role"
                value={draft.role}
                onChange={(event) =>
                  updateField("role", event.target.value)
                }
                placeholder="Hero, guide, mentor..."
              />
            </FormField>

            <FormField
              label="Color theme"
              htmlFor="character-color"
            >
              <TextInput
                id="character-color"
                value={draft.color_theme ?? ""}
                onChange={(event) =>
                  updateField(
                    "color_theme",
                    event.target.value,
                  )
                }
                placeholder="Silver, blue, violet"
              />
            </FormField>
          </div>

          <FormField
            label="Summary"
            htmlFor="character-summary"
            required
          >
            <TextArea
              id="character-summary"
              value={draft.summary}
              onChange={(event) =>
                updateField("summary", event.target.value)
              }
              placeholder="Who is this character in the Numeria universe?"
              rows={4}
            />
          </FormField>

          <FormField
            label="Personality traits"
            htmlFor="character-personality"
            description="Separate traits with commas."
          >
            <TextInput
              id="character-personality"
              value={personalityText}
              onChange={(event) => {
                setPersonalityText(event.target.value);
                setValidation(null);
                setPublished(null);
              }}
              placeholder="curious, patient, brave"
            />
          </FormField>

          <FormField
            label="Mathematical power"
            htmlFor="character-power"
            required
          >
            <TextArea
              id="character-power"
              value={draft.power}
              onChange={(event) =>
                updateField("power", event.target.value)
              }
              placeholder="What mathematical ability does this character embody?"
              rows={4}
            />
          </FormField>

          <FormField
            label="Educational mission"
            htmlFor="character-mission"
            required
          >
            <TextArea
              id="character-mission"
              value={draft.educational_mission}
              onChange={(event) =>
                updateField(
                  "educational_mission",
                  event.target.value,
                )
              }
              placeholder="What should children understand after meeting this character?"
              rows={4}
            />
          </FormField>

          <FormField
            label="Artwork prompt"
            htmlFor="character-artwork"
          >
            <TextArea
              id="character-artwork"
              value={draft.artwork_prompt ?? ""}
              onChange={(event) =>
                updateField(
                  "artwork_prompt",
                  event.target.value,
                )
              }
              placeholder="Describe the character's visual identity."
              rows={4}
            />
          </FormField>
        </div>

        <aside className="character-preview-column">
          <Card
            title="Live Preview"
            description="The character comes alive as you type."
          >
            <div className="character-preview">
              <div className="character-preview-symbol">
                ✨
              </div>

              <Badge tone="brand">
                {draft.role.trim() || "Canon Character"}
              </Badge>

              <h3>{previewName}</h3>

              {draft.nickname?.trim() && (
                <p className="character-preview-nickname">
                  “{draft.nickname.trim()}”
                </p>
              )}

              <p>{previewMission}</p>

              {normalizedDraft.personality.length > 0 && (
                <div className="character-traits">
                  {normalizedDraft.personality.map(
                    (trait) => (
                      <Badge key={trait}>
                        {trait}
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
              title="Creator error"
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
                  ? "Draft is ready"
                  : "Draft requires changes"
              }
            >
              {validation.proposed_id && (
                <p>
                  Proposed ID: {validation.proposed_id}
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
