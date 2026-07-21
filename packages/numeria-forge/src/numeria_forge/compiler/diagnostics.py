"""Structured compiler diagnostics."""

from dataclasses import dataclass
from enum import Enum


class DiagnosticSeverity(str, Enum):
    """Severity assigned to a compiler diagnostic."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class Diagnostic:
    """A structured compiler message."""

    severity: DiagnosticSeverity
    code: str
    message: str
    location: str | None = None
