from pathlib import Path

import yaml

from numeria_forge.compiler import FoundationCompiler
from numeria_forge.compiler.context import CompilerContext
from numeria_forge.compiler.stage import CompilerStage


def write_entity(path: Path, **fields) -> None:
    path.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}: {value}" for key, value in fields.items()]
    (path / "entity.yaml").write_text("\n".join(lines), encoding="utf-8")


def write_numeria_yaml(root: Path, workspaces: list[str]) -> None:
    workspace_lines = "\n".join(f"  - {w}" for w in workspaces)
    (root / "numeria.yaml").write_text(
        f"""
schema_version: "1.0"

foundation:
  id: test-foundation
  name: Test Foundation
  version: "0.1.0"

knowledge_root: knowledge

workspaces:
{workspace_lines}
""".strip(),
        encoding="utf-8",
    )


def test_foundation_compile_fails_on_invalid_canon(tmp_path: Path) -> None:
    write_numeria_yaml(tmp_path, ["packages/example"])

    write_entity(
        tmp_path / "knowledge" / "characters" / "wrong-dir",
        id="NUM-CHR-000001",
        type="Character",
        status="draft",
        version="1.0.0",
        name="Derivative",
    )

    result = FoundationCompiler().compile(tmp_path)

    assert result.success is False
    assert len(result.report.diagnostics) > 0
    assert result.package_results == ()


def test_foundation_compile_generates_packages_when_canon_is_clean(
    tmp_path: Path,
) -> None:
    write_numeria_yaml(tmp_path, ["packages/example"])

    write_entity(
        tmp_path / "knowledge" / "characters" / "NUM-CHR-000001-derivative",
        id="NUM-CHR-000001",
        type="Character",
        status="CANON",
        version="1.0.0",
        name="Derivative",
        role="Detective",
    )

    ontology_dir = tmp_path / "knowledge" / "ontology"
    ontology_dir.mkdir(parents=True, exist_ok=True)
    (ontology_dir / "relationship-types.yaml").write_text(
        "version: 1.0.0\nstatus: CANON\nrelationship_types: {}\n",
        encoding="utf-8",
    )

    package_directory = tmp_path / "packages" / "example" / "derivative"
    package_directory.mkdir(parents=True)
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

    template_root = (
        Path(__file__).resolve().parents[2] / "templates"
    )

    result = FoundationCompiler(template_root=template_root).compile(tmp_path)

    assert result.success is True
    assert len(result.package_results) == 1
    assert result.artifact_count == 1


def test_foundation_compile_fails_on_a_dependency_cycle(tmp_path: Path) -> None:
    write_numeria_yaml(tmp_path, ["packages/example"])

    for entity_id, name in (
        ("NUM-CON-000001", "Limit"),
        ("NUM-CON-000002", "Derivative"),
    ):
        write_entity(
            tmp_path / "knowledge" / "concepts" / f"{entity_id}-{name.lower()}",
            id=entity_id,
            type="Concept",
            status="CANON",
            version="1.0.0",
            name=name,
        )

    # A REQUIRES cycle: Derivative requires Limit requires Derivative.
    for edge_id, source_id, target_id in (
        ("NUM-REL-000001", "NUM-CON-000002", "NUM-CON-000001"),
        ("NUM-REL-000002", "NUM-CON-000001", "NUM-CON-000002"),
    ):
        relationship_dir = tmp_path / "knowledge" / "relationships" / edge_id
        relationship_dir.mkdir(parents=True, exist_ok=True)
        (relationship_dir / "entity.yaml").write_text(
            yaml.safe_dump(
                {
                    "id": edge_id,
                    "type": "REQUIRES",
                    "status": "CANON",
                    "version": "1.0.0",
                    "source": {"id": source_id, "type": "Concept"},
                    "target": {"id": target_id, "type": "Concept"},
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )

    ontology_dir = tmp_path / "knowledge" / "ontology"
    ontology_dir.mkdir(parents=True, exist_ok=True)
    (ontology_dir / "relationship-types.yaml").write_text(
        "version: 1.0.0\nstatus: CANON\nrelationship_types:\n"
        "  REQUIRES:\n    source: Concept\n    target: Concept\n"
        "    acyclic: true\n",
        encoding="utf-8",
    )

    result = FoundationCompiler().compile(tmp_path)

    assert result.success is False
    assert result.package_results == ()
    codes = {d.code for d in result.report.diagnostics}
    assert "canon.semantics.dependency-cycle" in codes


def test_foundation_compile_generates_and_publishes_canon_content(
    tmp_path: Path,
) -> None:
    """End-to-end: real Canon entities (no manifest.yaml at all) produce
    build/ output, routed by type, plus build/reports/*."""

    write_numeria_yaml(tmp_path, ["packages/none"])

    write_entity(
        tmp_path / "knowledge" / "characters" / "NUM-CHR-000001-derivative",
        id="NUM-CHR-000001",
        type="Character",
        status="CANON",
        version="1.0.0",
        name="Derivative",
        slug="derivative",
        role="Detective",
    )
    write_entity(
        tmp_path / "knowledge" / "lessons" / "NUM-LESSON-000001",
        id="NUM-LESSON-000001",
        type="Lesson",
        status="CANON",
        version="1.0.0",
        name="Intro to Derivatives",
        grade_band="6-8",
        primary_concept="derivative",
        primary_learning_objective="understand rate of change",
    )

    ontology_dir = tmp_path / "knowledge" / "ontology"
    ontology_dir.mkdir(parents=True, exist_ok=True)
    (ontology_dir / "relationship-types.yaml").write_text(
        "version: 1.0.0\nstatus: CANON\nrelationship_types: {}\n",
        encoding="utf-8",
    )

    template_root = Path(__file__).resolve().parents[2] / "templates"

    result = FoundationCompiler(template_root=template_root).compile(tmp_path)

    assert result.success is True

    # knowledge_model is a first-class artifact of the result, not
    # something callers should have to dig out of .context (v0.16.0).
    assert result.knowledge_model is not None
    assert result.knowledge_model is result.context.knowledge_model
    assert result.knowledge_model.query.get("NUM-CHR-000001") is not None

    build_directory = tmp_path / "build"

    character_readme = (
        build_directory
        / "canon"
        / "character"
        / "NUM-CHR-000001-derivative"
        / "README.md"
    )
    character_card = (
        build_directory
        / "canon"
        / "character"
        / "NUM-CHR-000001-derivative"
        / "CHARACTER_CARD.md"
    )
    lesson_readme = (
        build_directory / "lessons" / "lesson" / "NUM-LESSON-000001" / "README.md"
    )

    assert character_readme.exists()
    assert character_card.exists()
    assert lesson_readme.exists()
    assert "Derivative" in character_readme.read_text(encoding="utf-8")

    reports_directory = build_directory / "reports"
    assert (reports_directory / "compile.json").exists()
    assert (reports_directory / "diagnostics.json").exists()
    assert (reports_directory / "diagnostics.md").exists()

    import json

    compile_data = json.loads(
        (reports_directory / "compile.json").read_text(encoding="utf-8")
    )
    assert compile_data["success"] is True
    assert compile_data["generated_assets"] == 3  # 2 Character + 1 Lesson



class _RecordingStage(CompilerStage):
    """A minimal custom CompilerStage, standing in for a caller-supplied
    extension -- proves `extra_stages` (v0.19.0 -- "Compiler Hardening")
    actually runs, with access to everything the built-in pipeline has
    already populated on the context by that point."""

    def __init__(self, calls: list[str]) -> None:
        self._calls = calls

    @property
    def name(self) -> str:
        return "test.recording-stage"

    def execute(self, context: CompilerContext) -> None:
        self._calls.append(self.name)
        # Prove this runs *after* the knowledge graph has been built --
        # extra_stages are wired in right after PublishKnowledgeGraphStage.
        assert context.knowledge_model is not None


def test_extra_stages_run_and_are_counted(tmp_path: Path) -> None:
    write_numeria_yaml(tmp_path, ["packages/example"])

    write_entity(
        tmp_path / "knowledge" / "characters" / "NUM-CHR-000001-derivative",
        id="NUM-CHR-000001",
        type="Character",
        status="CANON",
        version="1.0.0",
        name="Derivative",
        role="Detective",
    )

    ontology_dir = tmp_path / "knowledge" / "ontology"
    ontology_dir.mkdir(parents=True, exist_ok=True)
    (ontology_dir / "relationship-types.yaml").write_text(
        "version: 1.0.0\nstatus: CANON\nrelationship_types: {}\n",
        encoding="utf-8",
    )

    package_directory = tmp_path / "packages" / "example" / "derivative"
    package_directory.mkdir(parents=True)
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

    template_root = Path(__file__).resolve().parents[2] / "templates"

    calls: list[str] = []
    without_extra = FoundationCompiler(template_root=template_root).compile(tmp_path)
    with_extra = FoundationCompiler(
        template_root=template_root,
        extra_stages=(_RecordingStage(calls),),
    ).compile(tmp_path)

    assert with_extra.success is True
    assert calls == ["test.recording-stage"]
    # Exactly one more stage ran than the identical compile without
    # extra_stages -- proves the extension point adds work without
    # changing anything else about the pipeline.
    assert (
        with_extra.report.stages_executed
        == without_extra.report.stages_executed + 1
    )


def test_no_extra_stages_by_default(tmp_path: Path) -> None:
    write_numeria_yaml(tmp_path, ["packages/example"])

    write_entity(
        tmp_path / "knowledge" / "characters" / "NUM-CHR-000001-derivative",
        id="NUM-CHR-000001",
        type="Character",
        status="CANON",
        version="1.0.0",
        name="Derivative",
        role="Detective",
    )

    ontology_dir = tmp_path / "knowledge" / "ontology"
    ontology_dir.mkdir(parents=True, exist_ok=True)
    (ontology_dir / "relationship-types.yaml").write_text(
        "version: 1.0.0\nstatus: CANON\nrelationship_types: {}\n",
        encoding="utf-8",
    )

    template_root = Path(__file__).resolve().parents[2] / "templates"

    result = FoundationCompiler(template_root=template_root).compile(tmp_path)

    assert result.success is True
    assert result.report.duration_seconds is not None
    assert result.report.duration_seconds >= 0
