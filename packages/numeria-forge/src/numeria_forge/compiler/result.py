"""Deprecated alias kept for backward compatibility.

``CompilerResult`` previously duplicated the purpose of
:class:`numeria_forge.compiler.report.CompilationReport` and imported a
nonexistent ``numeria_forge.compiler.diagnostics`` module. New code should
use ``CompilationReport`` directly.
"""

from __future__ import annotations

from numeria_forge.compiler.report import CompilationReport as CompilerResult

__all__ = ["CompilerResult"]
