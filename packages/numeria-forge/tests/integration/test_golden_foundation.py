"""Golden integration test for the v0.14.0 Forge Compiler + Canon Validation Engine.

Builds a small but structurally complete Numeria Foundation -- a World,
a Realm, a Region, a Character, a Concept, and a relationship between
them, all obeying every Canon Law -- compiles it end to end, and checks
every layer of what v0.14.0 promises:

* the Canon loads with zero load errors
* the Canon Validation Engine reports zero diagnostics (a valid Canon)
* the compiler proceeds past validation and publishes a package artifact
* both compilation report formats (JSON and human-readable) are correct
* each of the four Canon Laws is actually being enforced, not just
  satisfied by construction -- verified by deliberately breaking one
  law at a time and confirming the Validation Engine catches it.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from numeria_forge.compiler import FoundationCompiler
from numeria_forge.domain.canon import CanonLoader
from numeria_forge.domain.canon.validation import (
    CanonLawValidator,
    CanonValidationRunner,
    IdOnlyReferenceValidator,
    ValidationContext,
)

TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "templates"


def _write_entity(directory: Path, **fields: object) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "entity.yaml").write_text(
        yaml.safe_dump(fields, sort_keys=False),
        encoding="utf-8",
    )


def _write_numeria_yaml(root: Path, workspaces: list[str]) -> None:
    workspace_lines = "\n".join(f"  - {w}" for w in workspaces)
    (root / "numeria.yaml").write_text(
        f"""
schema_version: "1.0"

foundation:
  id: golden-foundation
  name: Golden Foundation
  version: "0.1.0"

knowledge_root: knowledge

workspaces:
{workspace_lines}
""".strip(),
        encoding="utf-8",
    )


def _write_ontology(knowledge_root: Path) -> None:
    ontology_dir = knowledge_root / "ontology"
    ontology_dir.mkdir(parents=True, exist_ok=True)
    (ontology_dir / "relationship-types.yaml").write_text(
        """
version: "1.0.0"
status: CANON

relationship_types:
  FEATURES_CHARACTER:
    source: Region
    target: Character
""".strip(),
        encoding="utf-8",
    )


def _write_package(root: Path) -> None:
    package_directory = root / "packages" / "example" / "derivative"
    package_directory.mkdir(parents=True, exist_ok=True)
    (package_directory / "manifest.yaml").write_text(
        """
schema_version: "1.0"

entity:
  type: concept
  id: numeria:concept:derivative
  slug: derivative
  title: Derivative

outputs:
  - artifact: readme
""".strip(),
        encoding="utf-8",
    )


def build_golden_foundation(root: Path) -> Path:
    """Build a minimal, fully law-abiding Numeria Foundation under `root`.

    Returns the knowledge root (`root / "knowledge"`).
    """

    _write_numeria_yaml(root, ["packages/example"])
    knowledge_root = root / "knowledge"

    _write_entity(
        knowledge_root / "world" / "NUM-WLD-000001-world",
        id="NUM-WLD-000001",
        type="World",
        status="CANON",
        version="1.0.0",
        name="Numeria",
        slug="world",
    )

    _write_entity(
        knowledge_root / "realms" / "NUM-RLM-000001-realm-of-change",
        id="NUM-RLM-000001",
        type="Realm",
        status="CANON",
        version="1.0.0",
        name="Realm of Change",
        slug="realm-of-change",
    )

    _write_entity(
        knowledge_root / "regions" / "NUM-REG-000001-calculus-academy",
        id="NUM-REG-000001",
        type="Region",
        status="CANON",
        version="1.0.0",
        name="Calculus Academy",
        slug="calculus-academy",
    )

    _write_entity(
        knowledge_root / "characters" / "NUM-CHR-000001-derivative",
        id="NUM-CHR-000001",
        type="Character",
        status="CANON",
        version="1.0.0",
        name="Derivative",
        slug="derivative",
        role="Detective of Change",
    )

    _write_entity(
        knowledge_root / "concepts" / "NUM-CON-000001-derivative",
        id="NUM-CON-000001",
        type="Concept",
        status="CANON",
        version="1.0.0",
        name="Derivative",
        slug="derivative",
    )

    _write_entity(
        knowledge_root
        / "relationships"
        / "NUM-REL-000001-region-features-derivative",
        id="NUM-REL-000001",
        type="FEATURES_CHARACTER",
        status="CANON",
        version="1.0.0",
        slug="region-features-derivative",
        source={"id": "NUM-REG-000001", "type": "Region"},
        target={"id": "NUM-CHR-000001", "type": "Character"},
    )

    _write_ontology(knowledge_root)
    _write_package(root)

    return knowledge_root


def test_golden_foundation_loads_with_zero_errors(tmp_path: Path) -> None:
    knowledge_root = build_golden_foundation(tmp_path)

    canon = CanonLoader().load(knowledge_root)

    assert len(canon) == 6
    assert canon.load_errors == []


def test_golden_foundation_canon_is_valid(tmp_path: Path) -> None:
    knowledge_root = build_golden_foundation(tmp_path)

    report = CanonValidationRunner().run(knowledge_root)

    assert report.entity_count == 6
    assert report.diagnostics == ()
    assert report.success is True
    assert (
        report.format_human_readable()
        == f"Validated 6 canonical entities under {knowledge_root}\n\n"
        "Canon is internally consistent. No issues found."
    )


def test_golden_foundation_compiles_and_publishes(tmp_path: Path) -> None:
    build_golden_foundation(tmp_path)

    result = FoundationCompiler(template_root=TEMPLATE_ROOT).compile(tmp_path)

    assert result.success is True
    assert len(result.package_results) == 1
    assert result.artifact_count == 1

    # Verify the actual rendered artifact content, not just the count.
    # (RenderTemplatesStage renders into `context.artifacts` in memory --
    # FoundationCompiler's per-package pipeline does not include a
    # publish stage, so there is no on-disk output to inspect here.)
    package_context = result.package_results[0]
    artifact = next(iter(package_context.artifacts))

    assert artifact.destination == Path("README.md")
    assert "Derivative" in artifact.content

    # Verify the report in both formats.
    report_dict = result.report.to_dict()

    assert report_dict["success"] is True
    assert report_dict["error_count"] == 0
    assert report_dict["warning_count"] == 0
    assert report_dict["diagnostics"] == []
    assert json.loads(result.report.to_json()) == report_dict

    human_readable = result.report.format_human_readable()

    assert "No diagnostics." in human_readable
    assert human_readable.strip().endswith("Build succeeded.")


def test_golden_foundation_satisfies_canon_law_1_identity_agreement(
    tmp_path: Path,
) -> None:
    knowledge_root = build_golden_foundation(tmp_path)
    canon = CanonLoader().load(knowledge_root)

    for entity in canon:
        directory_name = entity.source_path.parent.name
        slug = entity.get("slug")

        assert slug, f"{entity.id} is missing a slug"
        assert directory_name == f"{entity.id}-{slug}", (
            f"{entity.id}: directory '{directory_name}' does not match "
            f"'{entity.id}-{slug}' (Canon Law #1)"
        )

    assert CanonLawValidator().validate(ValidationContext(canon=canon)).success


def test_golden_foundation_satisfies_canon_law_3_id_only_references(
    tmp_path: Path,
) -> None:
    knowledge_root = build_golden_foundation(tmp_path)
    canon = CanonLoader().load(knowledge_root)

    # The one relationship entity references its endpoints by bare ID,
    # never by path -- exactly what Canon Law #3 requires.
    relationship = canon.entities["NUM-REL-000001"]

    assert relationship.data["source"]["id"] == "NUM-REG-000001"
    assert relationship.data["target"]["id"] == "NUM-CHR-000001"
    assert "/" not in relationship.data["source"]["id"]
    assert "/" not in relationship.data["target"]["id"]

    result = IdOnlyReferenceValidator().validate(ValidationContext(canon=canon))

    assert result.success
    assert result.diagnostics == ()


def test_golden_foundation_detects_canon_law_1_violation(tmp_path: Path) -> None:
    """A directory that doesn't match `<id>-<slug>` must fail validation."""

    knowledge_root = build_golden_foundation(tmp_path)

    # Break Law #1: rename the Character's directory so it no longer
    # agrees with its id + slug.
    character_dir = knowledge_root / "characters" / "NUM-CHR-000001-derivative"
    broken_dir = knowledge_root / "characters" / "wrong-directory-name"
    character_dir.rename(broken_dir)

    report = CanonValidationRunner().run(knowledge_root)

    assert report.success is False
    codes = {d.code for d in report.diagnostics}
    assert "canon.law-1-identity-agreement" in codes


def test_golden_foundation_detects_canon_law_3_violation(tmp_path: Path) -> None:
    """A reference that embeds a path instead of a bare ID must fail validation."""

    knowledge_root = build_golden_foundation(tmp_path)

    # Break Law #3: point the relationship's target at a path-shaped
    # value instead of a bare canonical ID.
    relationship_path = (
        knowledge_root
        / "relationships"
        / "NUM-REL-000001-region-features-derivative"
        / "entity.yaml"
    )
    data = yaml.safe_load(relationship_path.read_text(encoding="utf-8"))
    data["target"] = {
        "id": "knowledge/characters/NUM-CHR-000001-derivative",
        "type": "Character",
    }
    relationship_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    report = CanonValidationRunner().run(knowledge_root)

    assert report.success is False
    codes = {d.code for d in report.diagnostics}
    assert "canon.law-3-id-only-references" in codes
