"""Enforce Canon Law #1: ID, slug, and directory must always agree.

    ID:        NUM-CHR-000001
    Slug:      detective-derivative
    Directory: NUM-CHR-000001-detective-derivative

No entity type is exempt. Enforced as an exact match once an entity has
a `slug` -- until then it falls back to the older, looser "directory
starts with the id" check, so this doesn't retroactively fail every
entity that predates the slug field. See the migration note in
governance/CANON_LAWS.md.
"""

from __future__ import annotations

from numeria_forge.diagnostics import Diagnostic, Severity
from numeria_forge.domain.canon.validation.base import CanonValidator
from numeria_forge.domain.canon.validation.context import ValidationContext
from numeria_forge.domain.canon.validation.result import ValidationResult


class CanonLawValidator(CanonValidator):
    """Validate the ID/slug/directory identity triple (Canon Law #1)."""

    @property
    def name(self) -> str:
        return "canon.law-1-identity-agreement"

    def validate(self, context: ValidationContext) -> ValidationResult:
        diagnostics: list[Diagnostic] = []

        for entity in context.canon:
            directory_name = entity.source_path.parent.name
            slug = entity.get("slug")

            if slug:
                expected_directory_name = f"{entity.id}-{slug}"

                if directory_name != expected_directory_name:
                    diagnostics.append(
                        Diagnostic(
                            severity=Severity.ERROR,
                            code=self.name,
                            message=(
                                f"directory '{directory_name}' must be "
                                f"named exactly "
                                f"'{expected_directory_name}' (Canon Law "
                                "#1: <canonical-id>-<slug>)"
                            ),
                            location=entity.source_path,
                        )
                    )
            elif not directory_name.startswith(entity.id):
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        code=self.name,
                        message=(
                            f"directory '{directory_name}' must begin "
                            f"with entity id '{entity.id}'"
                        ),
                        location=entity.source_path,
                    )
                )

        return ValidationResult(validator=self.name, diagnostics=tuple(diagnostics))
