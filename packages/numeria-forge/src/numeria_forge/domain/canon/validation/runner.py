"""Load a knowledge root and run the full Canon Validation Engine.

This is the domain-level entry point used by both `forge validate`
(validate-only, no compilation) and indirectly by
`ValidateCanonStage`/`FoundationCompiler` (which share the same default
validator set via `create_default_canon_validators`).
"""

from __future__ import annotations

from pathlib import Path

from numeria_forge.diagnostics import Diagnostic
from numeria_forge.domain.canon.loader import CanonLoader
from numeria_forge.domain.canon.validation.base import CanonValidator
from numeria_forge.domain.canon.validation.context import ValidationContext
from numeria_forge.domain.canon.validation.registry import (
    create_default_canon_validators,
)
from numeria_forge.domain.canon.validation.report import CanonValidationReport
from numeria_forge.domain.canon.validation.result import ValidationResult


class CanonValidationRunner:
    """Load a knowledge root and validate it end to end."""

    def __init__(
        self,
        validators: tuple[CanonValidator, ...] | None = None,
        loader: CanonLoader | None = None,
    ) -> None:
        self._validators = validators or create_default_canon_validators()
        self._loader = loader or CanonLoader()

    def run(self, knowledge_root: Path) -> CanonValidationReport:
        canon = self._loader.load(knowledge_root)
        context = ValidationContext(canon=canon)

        results: list[ValidationResult] = [
            validator.validate(context) for validator in self._validators
        ]

        diagnostics: list[Diagnostic] = []

        for result in results:
            diagnostics.extend(result.diagnostics)

        return CanonValidationReport(
            knowledge_root=knowledge_root,
            entity_count=len(canon),
            diagnostics=tuple(diagnostics),
        )
