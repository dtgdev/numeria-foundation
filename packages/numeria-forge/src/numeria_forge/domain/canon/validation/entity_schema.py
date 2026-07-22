"""Validate that entities declare every field required for their type.

Every non-relationship entity type is checked -- types not explicitly
modeled in `REQUIRED_FIELDS_BY_TYPE` fall back to
`BASELINE_REQUIRED_FIELDS` instead of being silently skipped.
"""

from __future__ import annotations

from numeria_forge.diagnostics import Diagnostic, Severity
from numeria_forge.domain.canon.prefixes import (
    BASELINE_REQUIRED_FIELDS,
    REQUIRED_FIELDS_BY_TYPE,
)
from numeria_forge.domain.canon.validation.base import CanonValidator
from numeria_forge.domain.canon.validation.context import ValidationContext
from numeria_forge.domain.canon.validation.result import ValidationResult


class EntitySchemaValidator(CanonValidator):
    """Require the fields each entity type is documented to need."""

    @property
    def name(self) -> str:
        return "canon.schema"

    def validate(self, context: ValidationContext) -> ValidationResult:
        diagnostics: list[Diagnostic] = []

        for entity in context.canon.non_relationships():
            required_fields = REQUIRED_FIELDS_BY_TYPE.get(
                entity.type, BASELINE_REQUIRED_FIELDS
            )

            for field_name in required_fields:
                field_value = entity.get(field_name)

                if field_value is None or field_value == "" or field_value == []:
                    diagnostics.append(
                        Diagnostic(
                            severity=Severity.ERROR,
                            code=self.name,
                            message=(
                                f"{entity.type} is missing required "
                                f"field '{field_name}'"
                            ),
                            location=entity.source_path,
                        )
                    )

        return ValidationResult(validator=self.name, diagnostics=tuple(diagnostics))
