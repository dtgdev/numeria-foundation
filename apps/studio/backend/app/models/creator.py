from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class CharacterDraft(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    nickname: str | None = Field(default=None, max_length=100)
    role: str = Field(min_length=2, max_length=100)
    summary: str = Field(min_length=10, max_length=2000)
    personality: list[str] = Field(default_factory=list)
    power: str = Field(min_length=5, max_length=1000)
    educational_mission: str = Field(min_length=10, max_length=2000)
    color_theme: str | None = Field(default=None, max_length=100)
    artwork_prompt: str | None = Field(default=None, max_length=3000)

    @field_validator(
        "name",
        "role",
        "summary",
        "power",
        "educational_mission",
    )
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Value cannot be blank.")

        return normalized

    @field_validator(
        "nickname",
        "color_theme",
        "artwork_prompt",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class CharacterValidationResult(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    proposed_id: str | None = None
    proposed_path: str | None = None


class PublishedCharacter(BaseModel):
    id: str
    name: str
    path: str
    message: str


class RelationshipDraft(BaseModel):
    type: str = Field(min_length=2, max_length=100)
    source: str = Field(min_length=3, max_length=100)
    target: str = Field(min_length=3, max_length=100)
    summary: str | None = Field(default=None, max_length=2000)

    @field_validator("type", "source", "target")
    @classmethod
    def normalize_required_relationship_text(
        cls,
        value: str,
    ) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Value cannot be blank.")

        return normalized

    @field_validator("summary")
    @classmethod
    def normalize_relationship_summary(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip()
        return normalized or None


class RelationshipValidationResult(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    proposed_id: str | None = None
    proposed_path: str | None = None


class PublishedRelationship(BaseModel):
    id: str
    type: str
    source: str
    target: str
    path: str
    message: str
