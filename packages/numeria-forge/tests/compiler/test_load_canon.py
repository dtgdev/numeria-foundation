from pathlib import Path

from numeria_forge.compiler import CompilerContext
from numeria_forge.compiler.stages import LoadCanonStage


def write_entity(path: Path, **fields) -> None:
    path.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}: {value}" for key, value in fields.items()]
    (path / "entity.yaml").write_text("\n".join(lines), encoding="utf-8")


def test_load_canon_stage_populates_context(tmp_path: Path) -> None:
    write_entity(
        tmp_path / "characters" / "NUM-CHR-000001-derivative",
        id="NUM-CHR-000001",
        type="Character",
        status="CANON",
        version="1.0.0",
    )

    context = CompilerContext(project_root=tmp_path)

    LoadCanonStage(knowledge_root=tmp_path).execute(context)

    assert context.loaded_canon is not None
    assert len(context.loaded_canon) == 1


def test_load_canon_stage_defaults_to_knowledge_subdirectory(tmp_path: Path) -> None:
    write_entity(
        tmp_path / "knowledge" / "characters" / "NUM-CHR-000001-derivative",
        id="NUM-CHR-000001",
        type="Character",
        status="CANON",
        version="1.0.0",
    )

    context = CompilerContext(project_root=tmp_path, source_directory=tmp_path)

    LoadCanonStage().execute(context)

    assert len(context.loaded_canon) == 1
