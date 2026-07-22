"""Deprecated alias kept for backward compatibility.

`SlugValidator` was renamed `DuplicateSlugValidator` to match the
v0.14.0 Core Validators naming exactly.
"""

from __future__ import annotations

from numeria_forge.domain.canon.validation.duplicate_slug import (
    DuplicateSlugValidator as SlugValidator,
)

__all__ = ["SlugValidator"]
