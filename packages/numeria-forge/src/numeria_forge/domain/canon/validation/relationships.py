"""Validate relationship entities against the ontology and against the
canon's actual entities.

Does not hardcode a fixed list of relationship type names -- every
entity found under the `relationships/` directory is checked against
whatever `knowledge/ontology/relationship-types.yaml` declares, so newly
introduced relationship types are covered automatically.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from numeria_forge.diagnostics import Diagnostic, Severity
from numeria_forge.domain.canon.validation.base import CanonValidator
from numeria_forge.domain.canon.validation.context import ValidationContext
from numeria_forge.domain.canon.validation.result import ValidationResult


class RelationshipValidator(CanonValidator):
    """Validate every relationship entity's type, endpoints, and types."""

    def __init__(self, ontology_path: Path | None = None) -> None:
        self._ontology_path = ontology_path

    @property
    def name(self) -> str:
        return "canon.relationships"

    def validate(self, context: ValidationContext) -> ValidationResult:
        canon = context.canon

        ontology_path = self._ontology_path or (
            canon.root / "ontology" / "relationship-types.yaml"
        )

        if not ontology_path.is_file():
            return ValidationResult(
                validator=self.name,
                diagnostics=(
                    Diagnostic(
                        severity=Severity.ERROR,
                        code=self.name,
                        message="relationship ontology file not found",
                        location=ontology_path,
                    ),
                ),
            )

        try:
            ontology = (
                yaml.safe_load(ontology_path.read_text(encoding="utf-8"))
                or {}
            )
        except yaml.YAMLError as exc:
            return ValidationResult(
                validator=self.name,
                diagnostics=(
                    Diagnostic(
                        severity=Severity.ERROR,
                        code=self.name,
                        message=f"invalid YAML: {exc}",
                        location=ontology_path,
                    ),
                ),
            )

        rules = ontology.get("relationship_types", {})
        diagnostics: list[Diagnostic] = []

        for relationship in canon.relationships():
            rel_type = relationship.type

            if rel_type not in rules:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        code=self.name,
                        message=f"unknown relationship type '{rel_type}'",
                        location=relationship.source_path,
                    )
                )
                continue

            rule = rules[rel_type]

            source = relationship.get("source") or {}
            target = relationship.get("target") or {}

            source_id = source.get("id")
            target_id = target.get("id")
            source_type = source.get("type")
            target_type = target.get("type")

            allowed_source = rule.get("source")
            allowed_target = rule.get("target")

            if isinstance(allowed_source, str):
                allowed_source = [allowed_source]

            if isinstance(allowed_target, str):
                allowed_target = [allowed_target]

            if source_type not in (allowed_source or []):
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        code=self.name,
                        message=(
                            f"invalid source type '{source_type}' for "
                            f"{rel_type}; expected one of {allowed_source}"
                        ),
                        location=relationship.source_path,
                    )
                )

            if target_type not in (allowed_target or []):
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        code=self.name,
                        message=(
                            f"invalid target type '{target_type}' for "
                            f"{rel_type}; expected one of {allowed_target}"
                        ),
                        location=relationship.source_path,
                    )
                )

            if source_id not in canon:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        code=self.name,
                        message=(
                            f"source entity '{source_id}' does not exist"
                        ),
                        location=relationship.source_path,
                    )
                )
            else:
                actual_source_type = canon.entities[source_id].type

                if source_type != actual_source_type:
                    diagnostics.append(
                        Diagnostic(
                            severity=Severity.ERROR,
                            code=self.name,
                            message=(
                                f"source '{source_id}' is declared as "
                                f"'{source_type}' but actual type is "
                                f"'{actual_source_type}'"
                            ),
                            location=relationship.source_path,
                        )
                    )

            if target_id not in canon:
                diagnostics.append(
                    Diagnostic(
                        severity=Severity.ERROR,
                        code=self.name,
                        message=(
                            f"target entity '{target_id}' does not exist"
                        ),
                        location=relationship.source_path,
                    )
                )
            else:
                actual_target_type = canon.entities[target_id].type

                if target_type != actual_target_type:
                    diagnostics.append(
                        Diagnostic(
                            severity=Severity.ERROR,
                            code=self.name,
                            message=(
                                f"target '{target_id}' is declared as "
                                f"'{target_type}' but actual type is "
                                f"'{actual_target_type}'"
                            ),
                            location=relationship.source_path,
                        )
                    )

        return ValidationResult(validator=self.name, diagnostics=tuple(diagnostics))
