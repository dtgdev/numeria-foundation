"""Enforce Canon Law #3: nothing references paths, everything references IDs.

Walks every entity's raw content for ``{id, type}``-shaped reference
objects (the shape used by relationship ``source``/``target``, and
potentially any future reference-like field) and flags any whose ``id``
value looks like a path rather than a bare canonical ID token.

Deliberately narrow: this does NOT scan every string field in an entity
for anything that contains a "/" -- fields like ``source_documents`` (a
list of supporting document paths) are legitimately path-based and are
not entity references, so a blanket scan would be full of false
positives. This only inspects values shaped like ``{"id": ..., "type":
...}``, since that's the established convention for referencing another
canonical entity (see any relationship's ``source``/``target``).
"""

from __future__ import annotations

from typing import Any

from numeria_forge.diagnostics import Diagnostic, Severity
from numeria_forge.domain.canon.validation.base import CanonValidator
from numeria_forge.domain.canon.validation.context import ValidationContext
from numeria_forge.domain.canon.validation.result import ValidationResult


class IdOnlyReferenceValidator(CanonValidator):
    """Require entity-to-entity references to use bare IDs, not paths."""

    @property
    def name(self) -> str:
        return "canon.law-3-id-only-references"

    def validate(self, context: ValidationContext) -> ValidationResult:
        diagnostics: list[Diagnostic] = []

        for entity in context.canon:
            for field_path, reference_id in self._find_references(entity.data):
                if self._looks_like_a_path(reference_id):
                    diagnostics.append(
                        Diagnostic(
                            severity=Severity.ERROR,
                            code=self.name,
                            message=(
                                f"field '{field_path}' references a path "
                                f"('{reference_id}') instead of a bare "
                                "canonical ID (Canon Law #3)"
                            ),
                            location=entity.source_path,
                        )
                    )

        return ValidationResult(validator=self.name, diagnostics=tuple(diagnostics))

    def _find_references(
        self, value: Any, path: str = ""
    ) -> list[tuple[str, str]]:
        """Recursively find every reference-shaped mapping in `value`,
        returning (field_path, id_value) pairs. The entity's own
        top-level id/type (path == "") is its identity, not a reference,
        and is skipped."""

        found: list[tuple[str, str]] = []

        if isinstance(value, dict):
            if (
                path
                and "id" in value
                and "type" in value
                and isinstance(value.get("id"), str)
            ):
                found.append((path, value["id"]))

            for key, child in value.items():
                child_path = f"{path}.{key}" if path else key
                found.extend(self._find_references(child, child_path))

        elif isinstance(value, list):
            for index, child in enumerate(value):
                child_path = f"{path}[{index}]"
                found.extend(self._find_references(child, child_path))

        return found

    @staticmethod
    def _looks_like_a_path(value: str) -> bool:
        return "/" in value or value.startswith("knowledge")
