"""Deprecated alias kept for backward compatibility.

This module previously defined a separate ``PipelineStage`` contract that
duplicated (and diverged from) ``CompilerStage``, including a broken
``execute`` method body. All compiler stages now implement the single
``CompilerStage`` contract from :mod:`numeria_forge.compiler.stage`.
"""

from __future__ import annotations

from numeria_forge.compiler.stage import CompilerStage as PipelineStage

__all__ = ["PipelineStage"]
