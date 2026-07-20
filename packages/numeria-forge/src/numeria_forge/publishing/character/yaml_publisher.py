"""Publish canonical characters as YAML files."""

from __future__ import annotations

import yaml

from numeria_forge.domain import Character
from numeria_forge.publishing.context import PublishContext
from numeria_forge.publishing.publisher import Publisher
from numeria_forge.publishing.result import PublishResult
from numeria_forge.publishing.serializers import (
    CharacterYamlSerializer,
)


class CharacterYamlPublisher(Publisher[Character]):
    """Publish a canonical character as character.yaml."""

    def __init__(
        self,
        serializer: CharacterYamlSerializer | None = None,
    ) -> None:
        self._serializer = (
            serializer or CharacterYamlSerializer()
        )

    @property
    def name(self) -> str:
        """Return the stable publisher identifier."""

        return "character-yaml"

    def publish(
        self,
        value: Character,
        context: PublishContext,
    ) -> PublishResult:
        """Write a character beneath its canonical slug directory."""

        if not isinstance(value, Character):
            raise TypeError(
                "Character YAML publisher requires a Character."
            )

        if not isinstance(context, PublishContext):
            raise TypeError(
                "Character YAML publisher requires a PublishContext."
            )

        output_path = (
            context.output_directory
            / value.slug
            / "character.yaml"
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        document = self._serializer.to_dict(value)

        yaml_content = yaml.safe_dump(
            document,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
        )

        output_path.write_text(
            yaml_content,
            encoding="utf-8",
        )

        return PublishResult(
            publisher=self.name,
            path=output_path,
            media_type="application/yaml",
        )
