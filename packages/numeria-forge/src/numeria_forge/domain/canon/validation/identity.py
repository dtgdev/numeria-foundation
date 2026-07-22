"""Validate that an entity's ID has the correct shape for its type.

Split from the old combined `NamingValidator`: this validator only
checks ID *format* (does it match `NUM-XXX-######` for its type, or
`NUM-REL-######` for any relationship). Whether the ID, slug, and
containing directory all agree with each other is a separate concern --
see `CanonLawValidator` (Canon Law #1).

Duplicate display-name detection (per type) also lives here, as a
WARNING rather than an ERROR: two entities sharing a display name is a
data-quality smell, not an identity or reference break (references are
ID-based), so it shouldn't block a build the way a bad ID format does.
See `DuplicateIdValidator` for the identity-breaking case (two entities
claiming the same *ID*).
"""

from __future__ import annotations

import re

from numeria_forge.diagnostics import Diagnostic, Severity
from numeria_forge.domain.canon.prefixes import (
    PREFIX_BY_TYPE,
    RELATIONSHIP_PREFIX,
)
from numeria_forge.domain.canon.validation.base import CanonValidator
from numeria_forge.domain.canon.validation.context import ValidationContext
from numeria_forge.domain.canon.validation.result import ValidationResult


class IdentityValidator(CanonValidator):
    """Validate ID format and per-type display-name uniqueness."""

    @property
    def name(self) -> str:
        return "canon.identity"

    def validate(self, context: ValidationContext) -> ValidationResult:
        diagnostics: list[Diagnostic] = []
        names: dict[tuple[str, str], tuple[str, object]] = {}

        for entity in context.canon:
            expected_prefix = (
                RELATIONSHIP_PREFIX
                if entity.is_relationship
                else PREFIX_BY_TYPE.get(entity.type)
            )

            if expected_prefix and not re.fullmatch(
                rf"{re.escape(expected_prefix)}-\d{{6}}",
                entity.id,
            ):
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        code=self.name,
                        message=(
                            f"id '{entity.id}' must match "
                            f"'{expected_prefix}-######'"
                        ),
                        location=entity.source_path,
                    )
                )

            if entity.is_relationship:
                continue

            entity_name = entity.get("name") or entity.get("title")

            if not entity_name:
                continue

            key = (entity.type, entity_name.strip().casefold())

            if key in names:
                previous_id, previous_path = names[key]

                if previous_id != entity.id:
                    diagnostics.append(
                        Diagnostic(
                            severity=Severity.WARNING,
                            code=self.name,
                            message=(
                                f"duplicate {entity.type} name "
                                f"'{entity_name}' also used by "
                                f"{previous_id} in {previous_path}"
                            ),
                            location=entity.source_path,
                        )
                    )
            else:
                names[key] = (entity.id, entity.source_path)

        return ValidationResult(validator=self.name, diagnostics=tuple(diagnostics))
