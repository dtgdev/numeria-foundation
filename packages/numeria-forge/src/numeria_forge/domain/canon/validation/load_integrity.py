"""Surface knowledge-load failures as diagnostics.

Covers every load-time problem *except* duplicate IDs, which are their
own dedicated concern -- see `DuplicateIdValidator`.
"""

from __future__ import annotations

from numeria_forge.diagnostics import Diagnostic, Severity
from numeria_forge.domain.canon.canon import CanonLoadErrorCode
from numeria_forge.domain.canon.validation.base import CanonValidator
from numeria_forge.domain.canon.validation.context import ValidationContext
from numeria_forge.domain.canon.validation.result import ValidationResult


class LoadIntegrityValidator(CanonValidator):
    """Report every file the CanonLoader could not read, parse, or
    otherwise make sense of (missing id/type, wrong shape, ...)."""

    @property
    def name(self) -> str:
        return "canon.load-integrity"

    def validate(self, context: ValidationContext) -> ValidationResult:
        diagnostics = tuple(
            Diagnostic(
                severity=Severity.ERROR,
                code=self.name,
                message=error.message,
                location=error.path,
            )
            for error in context.canon.load_errors
            if error.code is not CanonLoadErrorCode.DUPLICATE_ID
        )

        return ValidationResult(validator=self.name, diagnostics=diagnostics)
