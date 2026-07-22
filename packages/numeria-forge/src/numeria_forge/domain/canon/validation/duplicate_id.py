"""Duplicate ID detection.

Split out from `LoadIntegrityValidator` as its own Core Validator: a
duplicate canonical ID is an identity violation (Canon Law #1), not a
generic "couldn't read this file" problem, even though both are
detected by `CanonLoader` at load time and recorded as `CanonLoadError`
entries.
"""

from __future__ import annotations

from numeria_forge.diagnostics import Diagnostic, Severity
from numeria_forge.domain.canon.canon import CanonLoadErrorCode
from numeria_forge.domain.canon.validation.base import CanonValidator
from numeria_forge.domain.canon.validation.context import ValidationContext
from numeria_forge.domain.canon.validation.result import ValidationResult


class DuplicateIdValidator(CanonValidator):
    """Report every duplicate canonical ID found while loading."""

    @property
    def name(self) -> str:
        return "canon.duplicate-id"

    def validate(self, context: ValidationContext) -> ValidationResult:
        diagnostics = tuple(
            Diagnostic(
                severity=Severity.ERROR,
                code=self.name,
                message=error.message,
                location=error.path,
            )
            for error in context.canon.load_errors
            if error.code is CanonLoadErrorCode.DUPLICATE_ID
        )

        return ValidationResult(validator=self.name, diagnostics=diagnostics)
