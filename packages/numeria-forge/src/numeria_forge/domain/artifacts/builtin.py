from .definition import ArtifactDefinition
from .registry import ArtifactRegistry


def create_builtin_registry() -> ArtifactRegistry:
    registry = ArtifactRegistry()

    registry.register(
        ArtifactDefinition(
            name="readme",
            template="concept/README.md.j2",
            media_type="text/markdown",
            default_destination="README.md",
        )
    )

    return registry