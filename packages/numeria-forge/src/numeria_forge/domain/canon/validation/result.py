"""The outcome of running a single CanonValidator."""

from __future__ import annotations

from dataclasses import dataclass, field

from numeria_forge.diagnostics import Diagnostic, Severity


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """What one validator found."""

    validator: str
    diagnostics: tuple[Diagnostic, ...] = field(default_factory=tuple)

    @property
    def errors(self) -> tuple[Diagnostic, ...]:
        return tuple(d for d in self.diagnostics if d.severity is Severity.ERROR)

    @property
    def warnings(self) -> tuple[Diagnostic, ...]:
        return tuple(
            d for d in self.diagnostics if d.severity is Severity.WARNING
        )

    @property
    def success(self) -> bool:
        return len(self.errors) == 0
