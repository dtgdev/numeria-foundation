from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from app.core import repository_root
from app.models.creator import (
    CharacterDraft,
    CharacterValidationResult,
    PublishedCharacter,
    PublishedRelationship,
    RelationshipDraft,
    RelationshipValidationResult,
)
from app.services import graph_service


CHARACTER_ID_PATTERN = re.compile(r"^NUM-CHR-(\d{6})$")
RELATIONSHIP_ID_PATTERN = re.compile(r"^NUM-REL-(\d{6})$")


def slugify(value: str) -> str:
    slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        value.lower(),
    ).strip("-")

    return slug or "canon-object"


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(
            path.read_text(encoding="utf-8"),
        ) or {}
    except (OSError, yaml.YAMLError):
        return {}

    return data if isinstance(data, dict) else {}


class CharacterCreatorService:
    def _characters_root(self) -> Path:
        return (
            repository_root()
            / "knowledge"
            / "characters"
        )

    def _existing_characters(self) -> list[dict[str, Any]]:
        characters: list[dict[str, Any]] = []

        for path in self._characters_root().rglob(
            "entity.yaml"
        ):
            data = load_yaml_mapping(path)

            if data.get("type") == "Character":
                characters.append(data)

        return characters

    def next_character_id(self) -> str:
        highest_number = 0

        for character in self._existing_characters():
            character_id = str(
                character.get("id", "")
            )

            match = CHARACTER_ID_PATTERN.fullmatch(
                character_id
            )

            if match:
                highest_number = max(
                    highest_number,
                    int(match.group(1)),
                )

        return (
            f"NUM-CHR-{highest_number + 1:06d}"
        )

    def validate(
        self,
        draft: CharacterDraft,
    ) -> CharacterValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        candidate_names = {
            value.strip().casefold()
            for value in (
                draft.name,
                draft.nickname,
            )
            if value and value.strip()
        }

        duplicate = next(
            (
                character
                for character in self._existing_characters()
                if candidate_names
                & {
                    value.strip().casefold()
                    for value in (
                        str(character.get("name", "")),
                        str(
                            character.get(
                                "nickname",
                                "",
                            )
                        ),
                    )
                    if value.strip()
                }
            ),
            None,
        )

        if duplicate:
            errors.append(
                "A character using the name or nickname "
                f"'{draft.name}' already exists with ID "
                f"{duplicate.get('id')}."
            )

        if not draft.personality:
            warnings.append(
                "No personality traits were supplied."
            )

        if not draft.artwork_prompt:
            warnings.append(
                "No artwork prompt was supplied."
            )

        proposed_id = self.next_character_id()

        directory_name = (
            f"{proposed_id}-{slugify(draft.name)}"
        )

        proposed_path = (
            Path("knowledge")
            / "characters"
            / directory_name
            / "entity.yaml"
        )

        return CharacterValidationResult(
            valid=not errors,
            errors=errors,
            warnings=warnings,
            proposed_id=proposed_id,
            proposed_path=str(proposed_path),
        )

    def publish(
        self,
        draft: CharacterDraft,
    ) -> PublishedCharacter:
        validation = self.validate(draft)

        if not validation.valid:
            raise ValueError(
                " ".join(validation.errors)
            )

        character_id = validation.proposed_id

        if character_id is None:
            raise RuntimeError(
                "Unable to generate character ID."
            )

        directory = (
            self._characters_root()
            / (
                f"{character_id}-"
                f"{slugify(draft.name)}"
            )
        )

        if directory.exists():
            raise FileExistsError(
                "Character directory already exists: "
                f"{directory}"
            )

        directory.mkdir(
            parents=True,
            exist_ok=False,
        )

        entity = {
            "id": character_id,
            "name": draft.name,
            "type": "Character",
            "status": "CANON",
            "version": "1.0.0",
            "nickname": draft.nickname,
            "role": draft.role,
            "summary": draft.summary,
            "personality": draft.personality,
            "power": draft.power,
            "educational_mission":
                draft.educational_mission,
            "color_theme": draft.color_theme,
            "artwork_prompt": draft.artwork_prompt,
        }

        entity = {
            key: value
            for key, value in entity.items()
            if value is not None
        }

        entity_path = directory / "entity.yaml"
        readme_path = directory / "README.md"

        try:
            entity_path.write_text(
                yaml.safe_dump(
                    entity,
                    sort_keys=False,
                    allow_unicode=True,
                    width=88,
                ),
                encoding="utf-8",
            )

            readme_path.write_text(
                "\n".join(
                    [
                        f"# {draft.name}",
                        "",
                        f"**Character ID:** "
                        f"{character_id}",
                        "",
                        "## Role",
                        "",
                        draft.role,
                        "",
                        "## Summary",
                        "",
                        draft.summary,
                        "",
                        "## Educational Mission",
                        "",
                        draft.educational_mission,
                        "",
                    ]
                ),
                encoding="utf-8",
            )
        except Exception:
            if entity_path.exists():
                entity_path.unlink()

            if readme_path.exists():
                readme_path.unlink()

            directory.rmdir()
            raise

        graph_service.refresh()

        relative_path = entity_path.relative_to(
            repository_root()
        )

        return PublishedCharacter(
            id=character_id,
            name=draft.name,
            path=str(relative_path),
            message=(
                "Character published to the "
                "Numeria canon."
            ),
        )


class RelationshipCreatorService:
    def _relationships_root(self) -> Path:
        return (
            repository_root()
            / "knowledge"
            / "relationships"
        )

    def _existing_relationships(
        self,
    ) -> list[dict[str, Any]]:
        relationships: list[dict[str, Any]] = []
        root = self._relationships_root()

        if not root.exists():
            return relationships

        for path in root.rglob("entity.yaml"):
            data = load_yaml_mapping(path)

            if data.get("source") and data.get("target"):
                relationships.append(data)

        return relationships

    def _entity_ids(self) -> set[str]:
        return {
            entity.id
            for entity in graph_service.get_entities()
        }

    def next_relationship_id(self) -> str:
        highest_number = 0

        for relationship in (
            self._existing_relationships()
        ):
            relationship_id = str(
                relationship.get("id", "")
            )

            match = (
                RELATIONSHIP_ID_PATTERN.fullmatch(
                    relationship_id
                )
            )

            if match:
                highest_number = max(
                    highest_number,
                    int(match.group(1)),
                )

        return (
            f"NUM-REL-{highest_number + 1:06d}"
        )

    def validate(
        self,
        draft: RelationshipDraft,
    ) -> RelationshipValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        entity_ids = self._entity_ids()

        if draft.source not in entity_ids:
            errors.append(
                f"Source entity '{draft.source}' "
                "does not exist."
            )

        if draft.target not in entity_ids:
            errors.append(
                f"Target entity '{draft.target}' "
                "does not exist."
            )

        if draft.source == draft.target:
            errors.append(
                "A relationship cannot connect "
                "an entity to itself."
            )

        duplicate = next(
            (
                relationship
                for relationship
                in self._existing_relationships()
                if (
                    str(
                        relationship.get(
                            "type",
                            "",
                        )
                    ).casefold()
                    == draft.type.casefold()
                    and str(
                        (
                            relationship.get("source")
                            or {}
                        ).get("id", "")
                    )
                    == draft.source
                    and str(
                        (
                            relationship.get("target")
                            or {}
                        ).get("id", "")
                    )
                    == draft.target
                )
            ),
            None,
        )

        if duplicate:
            errors.append(
                "This relationship already exists "
                f"with ID {duplicate.get('id')}."
            )

        if not draft.summary:
            warnings.append(
                "No relationship summary was "
                "supplied."
            )

        proposed_id = (
            self.next_relationship_id()
        )

        relationship_slug = slugify(
            (
                f"{draft.source}-"
                f"{draft.type}-"
                f"{draft.target}"
            )
        )

        proposed_path = (
            Path("knowledge")
            / "relationships"
            / (
                f"{proposed_id}-"
                f"{relationship_slug}"
            )
            / "entity.yaml"
        )

        return RelationshipValidationResult(
            valid=not errors,
            errors=errors,
            warnings=warnings,
            proposed_id=proposed_id,
            proposed_path=str(proposed_path),
        )

    def publish(
        self,
        draft: RelationshipDraft,
    ) -> PublishedRelationship:
        validation = self.validate(draft)

        if not validation.valid:
            raise ValueError(
                " ".join(validation.errors)
            )

        relationship_id = validation.proposed_id

        if relationship_id is None:
            raise RuntimeError(
                "Unable to generate relationship ID."
            )

        relationship_slug = slugify(
            (
                f"{draft.source}-"
                f"{draft.type}-"
                f"{draft.target}"
            )
        )

        directory = (
            self._relationships_root()
            / (
                f"{relationship_id}-"
                f"{relationship_slug}"
            )
        )

        if directory.exists():
            raise FileExistsError(
                "Relationship directory already "
                f"exists: {directory}"
            )

        directory.mkdir(
            parents=True,
            exist_ok=False,
        )

        entity = {
            "id": relationship_id,
            "type": draft.type,
            "status": "CANON",
            "version": "1.0.0",
            "source": {
                "id": draft.source,
            },
            "target": {
                "id": draft.target,
            },
            "summary": draft.summary,
        }

        entity = {
            key: value
            for key, value in entity.items()
            if value is not None
        }

        entity_path = directory / "entity.yaml"

        try:
            entity_path.write_text(
                yaml.safe_dump(
                    entity,
                    sort_keys=False,
                    allow_unicode=True,
                    width=88,
                ),
                encoding="utf-8",
            )
        except Exception:
            if entity_path.exists():
                entity_path.unlink()

            directory.rmdir()
            raise

        graph_service.refresh()

        relative_path = entity_path.relative_to(
            repository_root()
        )

        return PublishedRelationship(
            id=relationship_id,
            type=draft.type,
            source=draft.source,
            target=draft.target,
            path=str(relative_path),
            message=(
                "Relationship published to the "
                "Numeria canon."
            ),
        )


character_creator_service = (
    CharacterCreatorService()
)

relationship_creator_service = (
    RelationshipCreatorService()
)
