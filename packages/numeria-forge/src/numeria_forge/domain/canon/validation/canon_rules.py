"""Business rules that apply across the whole canon.

Severities are a deliberate judgment call, not a mechanical port of the
original script (which treated every failure as fatal): rules that break
structural correctness (self-referential relationships, missing
version, missing Character identity) stay ERROR; rules about content
completeness (Artifact needing a described purpose, Book needing
concepts, FRIEND_OF being marked bidirectional) are downgraded to
WARNING since they don't break identity or references. Reasonable
people could put these lines in different places -- flag if you'd
rather they were stricter or looser.
"""

from __future__ import annotations

from numeria_forge.diagnostics import Diagnostic, Severity
from numeria_forge.domain.canon.validation.base import CanonValidator
from numeria_forge.domain.canon.validation.context import ValidationContext
from numeria_forge.domain.canon.validation.result import ValidationResult


class CanonRulesValidator(CanonValidator):
    """Port of the six rules from the old validate_canon_rules.py."""

    @property
    def name(self) -> str:
        return "canon.business-rules"

    def validate(self, context: ValidationContext) -> ValidationResult:
        canon = context.canon
        diagnostics: list[Diagnostic] = []

        # Rule 1: every canonical entity must declare a version. (ERROR:
        # version is load-bearing for compatibility checks elsewhere.)
        for entity in canon:
            if not entity.get("version"):
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        code=self.name,
                        message=(
                            f"canonical entity {entity.id} is missing "
                            "version"
                        ),
                        location=entity.source_path,
                    )
                )

        # Rule 2: every Character must have a name and mathematical
        # role/domain. (ERROR: name is core identity.)
        for entity in canon.by_type("Character"):
            if not entity.get("name"):
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        code=self.name,
                        message=f"Character {entity.id} is missing name",
                        location=entity.source_path,
                    )
                )

            if not entity.get("role") and not entity.get("mathematical_domain"):
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        code=self.name,
                        message=(
                            f"Character {entity.id} needs role or "
                            "mathematical_domain"
                        ),
                        location=entity.source_path,
                    )
                )

        # Rule 3: every Artifact should define purpose, abilities, or
        # educational meaning. (WARNING: content completeness, not an
        # identity or reference break.)
        for entity in canon.by_type("Artifact"):
            if not any(
                entity.get(field_name)
                for field_name in (
                    "purpose",
                    "abilities",
                    "educational_meaning",
                )
            ):
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.WARNING,
                        code=self.name,
                        message=(
                            f"Artifact {entity.id} needs purpose, "
                            "abilities, or educational_meaning"
                        ),
                        location=entity.source_path,
                    )
                )

        # Rule 4: every Book should reference at least one educational
        # concept. (WARNING: content completeness.)
        for entity in canon.by_type("Book"):
            concepts = (
                entity.get("educational_concepts")
                or entity.get("educational_focus")
                or []
            )

            if not concepts:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.WARNING,
                        code=self.name,
                        message=(
                            f"Book {entity.id} must define educational "
                            "concepts"
                        ),
                        location=entity.source_path,
                    )
                )

        # Rule 5: relationship source and target cannot be identical.
        # (ERROR: structurally invalid.)
        for relationship in canon.relationships():
            source_id = (relationship.get("source") or {}).get("id")
            target_id = (relationship.get("target") or {}).get("id")

            if source_id and source_id == target_id:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        code=self.name,
                        message=(
                            f"relationship cannot connect {source_id} "
                            "to itself"
                        ),
                        location=relationship.source_path,
                    )
                )

        # Rule 6: FRIEND_OF relationships should be marked bidirectional.
        # (WARNING: data-quality, not structurally breaking.)
        for relationship in canon.relationships():
            if relationship.type != "FRIEND_OF":
                continue

            properties = relationship.get("relationship_properties") or {}

            if properties.get("bidirectional") is not True:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.WARNING,
                        code=self.name,
                        message=(
                            "FRIEND_OF must set "
                            "relationship_properties.bidirectional to "
                            "true"
                        ),
                        location=relationship.source_path,
                    )
                )

        return ValidationResult(validator=self.name, diagnostics=tuple(diagnostics))
