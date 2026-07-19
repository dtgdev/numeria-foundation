from pathlib import Path

from numeria_forge.domain import Artifact, ArtifactCollection


def test_artifact_collection():
    collection = ArtifactCollection()

    collection.add(
        Artifact(
            destination=Path("README.md"),
            content="# Derivative",
        )
    )

    assert len(collection) == 1