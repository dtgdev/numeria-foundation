"""Compiler result."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CompilerResult:
    """Overall compiler execution result."""

    success: bool

    warning_count: int

    error_count: int
