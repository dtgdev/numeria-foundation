from pathlib import Path

import pytest

from numeria_forge.compiler import CompilerContext
from numeria_forge.compiler.stages import LoadCanonStage, ValidateCanonStage


def write_entity(path: Path, **fields) -> None:
    path.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}: {value}" for key, value in fields.items()]
    (path / "entity.yaml").write_text("\n".join(lines), encoding="utf-8")


def test_validate_canon_stage_requires_loaded_canon(tmp_path: Path) -> None:
    context = CompilerContext(project_root=tmp_path)

    with pytest.raises(RuntimeError):
        ValidateCanonStage().execute(context)


def test_validate_canon_stage_records_diagnostics(tmp_path: Path) -> None:
    write_entity(
        tmp_path / "characters" / "wrong-dir",
        id="NUM-CHR-000001",
        type="Character",
        status="draft",
        version="1.0.0",
        name="Derivative",
    )

    context = CompilerContext(project_root=tmp_path)
    LoadCanonStage(knowledge_root=tmp_path).execute(context)
    ValidateCanonStage().execute(context)

    assert context.success is False
    assert len(context.diagnostics) > 0
    codes = {d.code for d in context.diagnostics}
    assert "canon.law-1-identity-agreement" in codes  # directory doesn't match id
    assert "canon.semantic" in codes  # status must be CANON


def write_ontology(tmp_path: Path) -> None:
    ontology_dir = tmp_path / "ontology"
    ontology_dir.mkdir(parents=True, exist_ok=True)
    (ontology_dir / "relationship-types.yaml").write_text(
        "version: 1.0.0\nstatus: CANON\nrelationship_types: {}\n",
        encoding="utf-8",
    )


def test_validate_canon_stage_passes_clean_canon(tmp_path: Path) -> None:
    write_entity(
        tmp_path / "characters" / "NUM-CHR-000001-derivative",
        id="NUM-CHR-000001",
        type="Character",
        status="CANON",
        version="1.0.0",
        name="Derivative",
        role="Detective",
    )
    write_ontology(tmp_path)

    context = CompilerContext(project_root=tmp_path)
    LoadCanonStage(knowledge_root=tmp_path).execute(context)
    ValidateCanonStage().execute(context)

    assert context.success is True
    assert context.diagnostics == []
