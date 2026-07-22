from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class Diagnostic:
    severity: str
    code: str
    message: str
    location: str | None = None