from .definition import ArtifactDefinition
from .registry import ArtifactRegistry


def create_builtin_registry() -> ArtifactRegistry:
    """Create the standard registry shipped with Numeria Forge."""

    registry = ArtifactRegistry()

    registry.register(
        ArtifactDefinition(
            name="readme",
            template="concept/README.md.j2",
            media_type="text/markdown",
            default_destination="README.md",
        )
    )

    registry.register(
        ArtifactDefinition(
            name="character_card",
            template="concept/CHARACTER_CARD.md.j2",
            media_type="text/markdown",
            default_destination="CHARACTER_CARD.md",
        )
    )

    return registry