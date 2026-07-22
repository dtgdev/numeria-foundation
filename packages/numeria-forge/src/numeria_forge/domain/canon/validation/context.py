"""The context passed to every CanonValidator."""

from __future__ import annotations

from dataclasses import dataclass

from numeria_forge.domain.canon.canon import Canon


@dataclass(frozen=True, slots=True)
class ValidationContext:
    """Everything a CanonValidator needs to do its job.

    Deliberately minimal today (just the loaded canon) -- the point of a
    dedicated context object, rather than passing `Canon` directly, is
    that future validators can need more (workspace config, a
    strict/lenient flag, ...) without changing every validator's
    signature again.
    """

    canon: Canon
