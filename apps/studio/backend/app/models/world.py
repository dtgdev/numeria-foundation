from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class RegionDraft(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    world_id: str = Field(default="NUM-WLD-000001")
    domain: str = Field(min_length=2, max_length=120)
    summary: str = Field(min_length=10, max_length=3000)
    educational_mission: str = Field(min_length=10, max_length=3000)
    themes: list[str] = Field(default_factory=list)
    atmosphere: list[str] = Field(default_factory=list)
    landmark_ideas: list[str] = Field(default_factory=list)

    @field_validator(
        "name",
        "world_id",
        "domain",
        "summary",
        "educational_mission",
    )
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        normalized = value.strip()

        if not normalized:
            raise ValueError("Value cannot be blank.")

        return normalized

    @field_validator(
        "themes",
        "atmosphere",
        "landmark_ideas",
    )
    @classmethod
    def normalize_lists(cls, values: list[str]) -> list[str]:
        return [
            value.strip()
            for value in values
            if value.strip()
        ]


class RegionValidationResult(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    proposed_id: str | None = None
    proposed_path: str | None = None


class PublishedRegion(BaseModel):
    id: str
    name: str
    world_id: str
    path: str
    message: str
