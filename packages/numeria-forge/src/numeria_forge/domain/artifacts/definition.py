from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ArtifactDefinition:
    """
    Describes how an artifact is produced.
    """

    name: str
    template: str
    media_type: str
    default_destination: str