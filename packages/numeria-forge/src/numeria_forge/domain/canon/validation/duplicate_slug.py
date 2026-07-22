"""Duplicate slug detection.

Slugs are scoped per entity type -- the real knowledge base legitimately
reuses a slug across types (e.g. the Concept `derivative` and its
embodying Character both use the slug `detective-derivative`), so
uniqueness is checked within a type, not globally.
"""

from __future__ import annotations

from pathlib import Path

from numeria_forge.diagnostics import Diagnostic, Severity
from numeria_forge.domain.canon.validation.base import CanonValidator
from numeria_forge.domain.canon.validation.context import ValidationContext
from numeria_forge.domain.canon.validation.result import ValidationResult


class DuplicateSlugValidator(CanonValidator):
    """Require slugs to be unique within their entity type."""

    @property
    def name(self) -> str:
        return "canon.duplicate-slug"

    def validate(self, context: ValidationContext) -> ValidationResult:
        diagnostics: list[Diagnostic] = []
        slugs: dict[tuple[str, str], tuple[str, Path]] = {}

        for entity in context.canon.non_relationships():
            slug = entity.get("slug")

            if not slug:
                continue

            key = (entity.type, str(slug).strip().casefold())

            if key in slugs:
                previous_id, previous_path = slugs[key]

                if previous_id != entity.id:
                    diagnostics.append(
                        Diagnostic(
                            severity=Severity.ERROR,
                            code=self.name,
                            message=(
                                f"duplicate {entity.type} slug '{slug}' "
                                f"also used by {previous_id} in "
                                f"{previous_path}"
                            ),
                            location=entity.source_path,
                        )
                    )
            else:
                slugs[key] = (entity.id, entity.source_path)

        return ValidationResult(validator=self.name, diagnostics=tuple(diagnostics))
