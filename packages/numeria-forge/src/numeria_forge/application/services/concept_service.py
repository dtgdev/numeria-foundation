from pathlib import Path

from numeria_forge.domain.generators.concept import ConceptGenerator


class ConceptService:
    """Application service for concept generation."""

    def __init__(self) -> None:
        self.generator = ConceptGenerator()

    def create(
        self,
        output_directory: Path,
        *,
        name: str,
        canonical_id: str,
        domain: str,
    ):
        return self.generator.generate(
            output_directory,
            {
                "name": name,
                "canonical_id": canonical_id,
                "domain": domain,
            },
        )
