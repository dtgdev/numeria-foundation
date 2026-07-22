"""Deprecated alias kept for backward compatibility.

`NamingValidator` used to bundle ID-format checking, duplicate-name
detection, and the Canon Law #1 (id/slug/directory agreement) check
together. As of the v0.14.0 Canonical Validator Framework cleanup those
are `IdentityValidator` (format + duplicate names) and `CanonLawValidator`
(Law #1) respectively. This alias points at `IdentityValidator` since
that's the closer match to the old name; update call sites to whichever
of the two you actually mean.
"""

from __future__ import annotations

from numeria_forge.domain.canon.validation.identity import (
    IdentityValidator as NamingValidator,
)

__all__ = ["NamingValidator"]
