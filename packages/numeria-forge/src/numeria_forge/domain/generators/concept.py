from pathlib import Path

from numeria_forge.domain.generators.base import BaseGenerator
from numeria_forge.domain.models.concept import Concept
from numeria_forge.infrastructure.renderer import TemplateRenderer
from numeria_forge.infrastructure.repository import RepositoryWriter


class ConceptGenerator(BaseGenerator):
    """Generates a canonical concept package."""

    name = "concept"

    def __init__(self) -> None:
        self.renderer = TemplateRenderer()
        self.writer = RepositoryWriter()

    def generate(
        self,
        output_directory: Path,
        context: dict,
    ) -> list[Path]:

        concept = Concept(**context)

        destination = (
            output_directory
            / "knowledge"
            / "concepts"
            / concept.slug
        )

        rendered = self.renderer.render(
            "concept/README.md.j2",
            {
                "title": concept.name,
                "canonical_id": concept.canonical_id,
                "domain": concept.domain,
                "version": concept.version,
                "status": concept.status,
            },
        )

        created = self.writer.write(
            destination / "README.md",
            rendered,
        )

        return [created]
