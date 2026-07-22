"""Compiler stage: the Validation Engine."""

from __future__ import annotations

from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stage import CompilerStage
from numeria_forge.domain.canon.validation import (
    CanonValidator,
    ValidationContext,
    create_default_canon_validators,
)


class ValidateCanonStage(CompilerStage):
    """Run every canon validator and record diagnostics.

    Requires ``context.loaded_canon`` to already be set (run
    :class:`~numeria_forge.compiler.stages.load_canon.LoadCanonStage`
    first).
    """

    def __init__(
        self,
        validators: tuple[CanonValidator, ...] | None = None,
    ) -> None:
        self._validators = validators or create_default_canon_validators()

    @property
    def name(self) -> str:
        return "validate-canon"

    def execute(self, context: CompilerContext) -> CompilerContext:
        if context.loaded_canon is None:
            raise RuntimeError(
                "ValidateCanonStage requires context.loaded_canon to be "
                "set; run LoadCanonStage first."
            )

        validation_context = ValidationContext(canon=context.loaded_canon)

        for validator in self._validators:
            result = validator.validate(validation_context)
            context.diagnostics.extend(result.diagnostics)

        return context
