"""Deprecated aliases kept for backward compatibility.

`CanonDiagnostic`/`CanonSeverity` used to be defined here, separately
from the compiler's own `Diagnostic`/`DiagnosticSeverity` -- as of
v0.14.0 there is one shared type in `numeria_forge.diagnostics`, and both
names below are aliases for it.
"""

from __future__ import annotations

from numeria_forge.diagnostics import Diagnostic as CanonDiagnostic
from numeria_forge.diagnostics import Severity as CanonSeverity

__all__ = ["CanonDiagnostic", "CanonSeverity"]
