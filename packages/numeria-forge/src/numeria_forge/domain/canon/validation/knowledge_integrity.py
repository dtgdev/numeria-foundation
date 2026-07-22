"""Deprecated alias kept for backward compatibility.

`KnowledgeIntegrityValidator` used to bundle load-error reporting and
the CANON-status lifecycle check together. As of v0.14 those are two
separate concerns: load errors are `LoadIntegrityValidator`, and the
status/lifecycle check moved to `SemanticValidator` (status is a
lifecycle rule, not a load-integrity one).
"""

from __future__ import annotations

from numeria_forge.domain.canon.validation.load_integrity import (
    LoadIntegrityValidator as KnowledgeIntegrityValidator,
)

__all__ = ["KnowledgeIntegrityValidator"]
