"""Enforce Compiler Law #1: compilation is deterministic.

    Same Canon + Same Compiler Version = Identical Output

Rather than just asserting this in prose (governance/COMPILER_LAWS.md),
this test proves it: build the same fixture Canon in two independent
directories, compile each, and assert every observable output --
the Compilation Report, every generated artifact's content, and every
byte written under build/ -- is identical between the two. If a future
change introduces a timestamp, a random id, or anything else
non-reproducible, this test is where it would show up as a diff
between `result_a` and `result_b` despite compiling from identical
source content.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from numeria_forge.compiler import FoundationCompiler


def _report_dict_excluding_duration(report) -> dict:
    """The report as a dict, minus `duration_seconds`.

    v0.19.0 -- "Compiler Hardening" -- added wall-clock duration
    timing to `CompilationReport`. It is, by construction, never
    reproducible between two separate compiles (even of byte-identical
    Canon content, the two runs take different amounts of wall-clock
    time) -- so it is deliberately excluded from this determinism
    comparison, exactly as documented in
    `docs/architecture/ADR-0008-compiler-hardening.md`'s "Consequences"
    section. Everything else in the report -- entity counts,
    diagnostics, graph statistics, published/generated asset counts --
    remains part of the byte-identical contract.
    """

    data = json.loads(report.to_json())
    data.pop("duration_seconds", None)
    return data

TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "templates"


def _write_entity(directory: Path, **fields: object) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "entity.yaml").write_text(
        yaml.safe_dump(fields, sort_keys=False), encoding="utf-8"
    )


def build_fixture(root: Path) -> None:
    """A small, deliberately varied Canon: a Character (readme +
    character_card), a Lesson (routed to lessons/), a REQUIRES
    relationship between two Concepts (exercises the dependency graph
    and topological order), and one hand-authored package (exercises
    the per-package manifest pipeline too)."""

    root.mkdir(parents=True, exist_ok=True)

    (root / "numeria.yaml").write_text(
        """
schema_version: "1.0"

foundation:
  id: determinism-fixture
  name: Determinism Fixture
  version: "0.1.0"

knowledge_root: knowledge

workspaces:
  - packages/example
""".strip(),
        encoding="utf-8",
    )

    knowledge_root = root / "knowledge"

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
        knowledge_root / "concepts" / "NUM-CON-000001-limit",
        id="NUM-CON-000001",
        type="Concept",
        status="CANON",
        version="1.0.0",
        name="Limit",
        slug="limit",
    )
    _write_entity(
        knowledge_root / "concepts" / "NUM-CON-000002-derivative",
        id="NUM-CON-000002",
        type="Concept",
        status="CANON",
        version="1.0.0",
        name="Derivative",
        slug="derivative",
    )
    _write_entity(
        knowledge_root / "lessons" / "NUM-LESSON-000001",
        id="NUM-LESSON-000001",
        type="Lesson",
        status="CANON",
        version="1.0.0",
        name="Intro to Derivatives",
        grade_band="6-8",
        primary_concept="derivative",
        primary_learning_objective="understand rate of change",
    )
    _write_entity(
        knowledge_root / "relationships" / "NUM-REL-000001",
        id="NUM-REL-000001",
        type="REQUIRES",
        status="CANON",
        version="1.0.0",
        source={"id": "NUM-CON-000002", "type": "Concept"},
        target={"id": "NUM-CON-000001", "type": "Concept"},
    )

    ontology_dir = knowledge_root / "ontology"
    ontology_dir.mkdir(parents=True, exist_ok=True)
    (ontology_dir / "relationship-types.yaml").write_text(
        """
version: "1.0.0"
status: CANON

relationship_types:
  REQUIRES:
    source: Concept
    target: Concept
    acyclic: true
""".strip(),
        encoding="utf-8",
    )

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


def test_compile_is_deterministic_across_independent_directories(
    tmp_path: Path,
) -> None:
    root_a = tmp_path / "a"
    root_b = tmp_path / "b"
    build_fixture(root_a)
    build_fixture(root_b)

    result_a = FoundationCompiler(template_root=TEMPLATE_ROOT).compile(root_a)
    result_b = FoundationCompiler(template_root=TEMPLATE_ROOT).compile(root_b)

    assert result_a.success is True
    assert result_b.success is True

    # The full Compilation Report must be identical -- except
    # `duration_seconds`, which is wall-clock and never reproducible
    # by construction (see `_report_dict_excluding_duration` above).
    assert _report_dict_excluding_duration(
        result_a.report
    ) == _report_dict_excluding_duration(result_b.report)

    # Every generated (Canon-driven) asset's destination + content.
    generated_a = sorted(
        (str(a.destination), a.content) for a in result_a.context.generated_assets
    )
    generated_b = sorted(
        (str(a.destination), a.content) for a in result_b.context.generated_assets
    )
    assert generated_a == generated_b
    assert len(generated_a) > 0  # sanity: the fixture actually produces output

    # The topological order (node ids only -- ids differ trivially by
    # construction here, but the *ordering logic* must agree).
    assert result_a.context.topological_order == result_b.context.topological_order

    # Every package artifact's destination + content.
    package_artifacts_a = sorted(
        (str(artifact.destination), artifact.content)
        for package_context in result_a.package_results
        for artifact in package_context.artifacts
    )
    package_artifacts_b = sorted(
        (str(artifact.destination), artifact.content)
        for package_context in result_b.package_results
        for artifact in package_context.artifacts
    )
    assert package_artifacts_a == package_artifacts_b
    assert len(package_artifacts_a) > 0

    # Every byte written under build/, relative path and content both.
    def build_tree(root: Path) -> dict[Path, bytes]:
        build_dir = root / "build"
        return {
            path.relative_to(build_dir): path.read_bytes()
            for path in build_dir.rglob("*")
            if path.is_file()
        }

    tree_a = build_tree(root_a)
    tree_b = build_tree(root_b)

    assert set(tree_a.keys()) == set(tree_b.keys())
    assert len(tree_a) > 0

    # build/reports/compile.json embeds duration_seconds -- wall-clock,
    # never reproducible by construction (see
    # _report_dict_excluding_duration above). Compare it with that one
    # field excluded; every other byte under build/, including
    # build/reports/diagnostics.{json,md}, must still match exactly.
    compile_json_path = Path("reports/compile.json")

    for relative_path in tree_a:
        if relative_path == compile_json_path:
            data_a = json.loads(tree_a[relative_path])
            data_b = json.loads(tree_b[relative_path])
            data_a.pop("duration_seconds", None)
            data_b.pop("duration_seconds", None)
            assert data_a == data_b, (
                "build/reports/compile.json differs (beyond duration_seconds) "
                "between two compiles of an identical Canon -- Compiler Law #1 "
                "violation"
            )
            continue

        assert tree_a[relative_path] == tree_b[relative_path], (
            f"build/{relative_path} differs between two compiles of an "
            "identical Canon -- Compiler Law #1 violation"
        )


def test_recompiling_the_same_directory_overwrites_identically(
    tmp_path: Path,
) -> None:
    build_fixture(tmp_path)

    first = FoundationCompiler(template_root=TEMPLATE_ROOT).compile(tmp_path)
    second = FoundationCompiler(template_root=TEMPLATE_ROOT).compile(tmp_path)

    assert _report_dict_excluding_duration(
        first.report
    ) == _report_dict_excluding_duration(second.report)

    build_dir = tmp_path / "build"
    readme = (
        build_dir
        / "canon"
        / "character"
        / "NUM-CHR-000001-derivative"
        / "README.md"
    )
    assert readme.is_file()
