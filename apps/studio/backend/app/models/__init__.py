from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CanonEntity(BaseModel):
    id: str
    type: str
    name: str
    path: str
    data: dict[str, Any] = Field(default_factory=dict)


class CanonRelationship(BaseModel):
    id: str
    type: str
    source: str
    target: str
    path: str
    data: dict[str, Any] = Field(default_factory=dict)


class CanonSummary(BaseModel):
    entities: int
    relationships: int
    entity_types: dict[str, int]
    relationship_types: dict[str, int]


class CanonGraph(BaseModel):
    entities: list[CanonEntity]
    relationships: list[CanonRelationship]
    summary: CanonSummary
