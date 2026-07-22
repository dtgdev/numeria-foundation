"""The single shared diagnostic type used across Forge.

Both the Canon Validation Engine (`domain.canon.validation`) and the
Compiler (`compiler`) previously had their own, separately-defined
`Diagnostic`/`Severity` pair (`CanonDiagnostic`/`CanonSeverity` and
`compiler.diagnostic.Diagnostic`/`DiagnosticSeverity`), translated into
each other at the `ValidateCanonStage` boundary. As of the v0.14.0
Canonical Validator Framework cleanup, there is exactly one definition,
living here (a neutral module with no dependency on either the domain or
compiler layers), and both layers import it. The old names are kept as
deprecated aliases so existing imports keep working.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class Severity(str, Enum):
    """Severity of a single diagnostic finding."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """A single structured finding: what, how severe, where."""

    severity: Severity
    code: str
    message: str
    location: Path | None = None
