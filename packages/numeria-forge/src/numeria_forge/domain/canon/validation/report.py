"""The validation report produced by `forge validate` / CanonValidationRunner."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from numeria_forge.diagnostics import Diagnostic, Severity


@dataclass(frozen=True, slots=True)
class CanonValidationReport:
    """Answers: is this canon internally consistent?"""

    knowledge_root: Path
    entity_count: int
    diagnostics: tuple[Diagnostic, ...]

    @property
    def errors(self) -> tuple[Diagnostic, ...]:
        return tuple(
            d for d in self.diagnostics if d.severity is Severity.ERROR
        )

    @property
    def warnings(self) -> tuple[Diagnostic, ...]:
        return tuple(
            d for d in self.diagnostics if d.severity is Severity.WARNING
        )

    @property
    def success(self) -> bool:
        """True when the canon has no ERROR-severity diagnostics.

        Warnings do not block a build -- only errors do.
        """

        return len(self.errors) == 0

    def to_dict(self) -> dict:
        return {
            "knowledge_root": str(self.knowledge_root),
            "entity_count": self.entity_count,
            "success": self.success,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "diagnostics": [
                {
                    "severity": diagnostic.severity.value,
                    "code": diagnostic.code,
                    "message": diagnostic.message,
                    "location": (
                        str(diagnostic.location)
                        if diagnostic.location is not None
                        else None
                    ),
                }
                for diagnostic in self.diagnostics
            ],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def format_human_readable(self) -> str:
        lines = [
            f"Validated {self.entity_count} canonical entities under "
            f"{self.knowledge_root}",
            "",
        ]

        if not self.diagnostics:
            lines.append("Canon is internally consistent. No issues found.")
            return "\n".join(lines)

        for diagnostic in self.diagnostics:
            location = (
                f" ({diagnostic.location})"
                if diagnostic.location is not None
                else ""
            )

            lines.append(
                f"[{diagnostic.severity.value.upper()}] "
                f"{diagnostic.code}: {diagnostic.message}{location}"
            )

        lines.append("")
        lines.append(
            f"{len(self.errors)} error(s), {len(self.warnings)} warning(s)."
        )
        lines.append(
            "Canon is internally consistent."
            if self.success
            else "Canon is NOT internally consistent."
        )

        return "\n".join(lines)
