"""The Canon Validator contract.

This is deliberately distinct from the generic
`numeria_forge.domain.validators.Validator` extension point (which
returns plain error-message strings and is meant for simple,
general-purpose Forge extensions). The Canon Validation Engine needs
severity-aware, structured diagnostics -- warnings as well as errors,
each with a code and a location -- so canon validators implement this
richer contract instead.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from numeria_forge.domain.canon.validation.context import ValidationContext
from numeria_forge.domain.canon.validation.result import ValidationResult


class CanonValidator(ABC):
    """A single validation concern run against the whole canon."""

    @property
    @abstractmethod
    def name(self) -> str:
        """A short, stable code identifying this validator."""

    @abstractmethod
    def validate(self, context: ValidationContext) -> ValidationResult:
        """Validate `context.canon` and return this validator's result."""
