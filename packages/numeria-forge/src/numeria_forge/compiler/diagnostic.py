"""Deprecated aliases kept for backward compatibility.

`Diagnostic`/`DiagnosticSeverity` used to be defined here, separately
from the Canon Validation Engine's own `CanonDiagnostic`/`CanonSeverity`
-- as of v0.14.0 there is one shared type in `numeria_forge.diagnostics`,
and both names below are aliases for it.
"""

from __future__ import annotations

from numeria_forge.diagnostics import Diagnostic, Severity as DiagnosticSeverity

__all__ = ["Diagnostic", "DiagnosticSeverity"]
