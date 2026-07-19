from .definition import ArtifactDefinition


class ArtifactRegistry:
    """Registry of known artifact definitions."""

    def __init__(self) -> None:
        self._definitions: dict[str, ArtifactDefinition] = {}

    def register(self, definition: ArtifactDefinition) -> None:
        if definition.name in self._definitions:
            raise ValueError(
                f"Artifact '{definition.name}' is already registered."
            )

        self._definitions[definition.name] = definition

    def lookup(self, name: str) -> ArtifactDefinition:
        try:
            return self._definitions[name]
        except KeyError as exc:
            raise KeyError(
                f"Unknown artifact '{name}'."
            ) from exc

    def __contains__(self, name: str) -> bool:
        return name in self._definitions

    def __len__(self) -> int:
        return len(self._definitions)

    def __iter__(self):
        return iter(self._definitions.values())