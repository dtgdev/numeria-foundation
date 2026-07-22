"""Semantic validation: lifecycle rules and prerequisite resolution.

This is where "is this canon internally *meaningful*, not just
internally *shaped correctly*" lives -- e.g. "Derivative requires Limit;
if Limit is missing, that's an error", and "canonical status is part of
an entity's lifecycle, not just a free-text field".
"""

from __future__ import annotations

import re

from numeria_forge.diagnostics import Diagnostic, Severity
from numeria_forge.domain.canon.validation.base import CanonValidator
from numeria_forge.domain.canon.validation.context import ValidationContext
from numeria_forge.domain.canon.validation.result import ValidationResult

# The only status the real knowledge base uses today; kept as an
# explicit, named lifecycle rule (rather than an inline string check)
# so it's easy to extend to a richer lifecycle (draft/review/canon/...)
# without touching every caller.
CANONICAL_STATUS = "CANON"

VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

# Relationship types that express a hard prerequisite: the target must
# exist and (once resolvable) should itself be canonical.
PREREQUISITE_RELATIONSHIP_TYPES = frozenset({"REQUIRES"})


class SemanticValidator(CanonValidator):
    """Lifecycle status, version format, and prerequisite resolution."""

    @property
    def name(self) -> str:
        return "canon.semantic"

    def validate(self, context: ValidationContext) -> ValidationResult:
        canon = context.canon
        diagnostics: list[Diagnostic] = []

        for entity in canon:
            status = entity.get("status")

            if status != CANONICAL_STATUS:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        code=self.name,
                        message=(
                            f"status must be '{CANONICAL_STATUS}' "
                            f"(found '{status}')"
                        ),
                        location=entity.source_path,
                    )
                )

            version = entity.get("version")

            if version and not VERSION_PATTERN.fullmatch(str(version)):
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.WARNING,
                        code=self.name,
                        message=(
                            f"version '{version}' does not look like "
                            "semantic versioning (MAJOR.MINOR.PATCH)"
                        ),
                        location=entity.source_path,
                    )
                )

        for relationship in canon.relationships():
            if relationship.type not in PREREQUISITE_RELATIONSHIP_TYPES:
                continue

            target_id = (relationship.get("target") or {}).get("id")

            if not target_id:
                continue

            target = canon.entities.get(target_id)

            if target is None:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        code=self.name,
                        message=f"Missing prerequisite: {target_id}",
                        location=relationship.source_path,
                    )
                )
            elif target.get("status") != CANONICAL_STATUS:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.WARNING,
                        code=self.name,
                        message=(
                            f"prerequisite {target_id} exists but is "
                            f"not {CANONICAL_STATUS} "
                            f"(status='{target.get('status')}')"
                        ),
                        location=relationship.source_path,
                    )
                )

        return ValidationResult(validator=self.name, diagnostics=tuple(diagnostics))
