from pathlib import Path

import pytest

from numeria_forge.compiler import CompilerContext
from numeria_forge.compiler.stages import GenerateMissingAssetsStage, LoadCanonStage

TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "templates"


def write_entity(path: Path, **fields) -> None:
    path.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}: {value}" for key, value in fields.items()]
    (path / "entity.yaml").write_text("\n".join(lines), encoding="utf-8")


def test_requires_loaded_canon(tmp_path: Path) -> None:
    context = CompilerContext(project_root=tmp_path)

    with pytest.raises(RuntimeError):
        GenerateMissingAssetsStage(TEMPLATE_ROOT).execute(context)


def test_renders_readme_for_a_generic_entity(tmp_path: Path) -> None:
    write_entity(
        tmp_path / "concepts" / "NUM-CON-000001-derivative",
        id="NUM-CON-000001",
        type="Concept",
        status="CANON",
        version="1.0.0",
        name="Derivative",
        slug="derivative",
    )

    context = CompilerContext(project_root=tmp_path)
    LoadCanonStage(knowledge_root=tmp_path).execute(context)
    GenerateMissingAssetsStage(TEMPLATE_ROOT).execute(context)

    assert len(context.generated_assets) == 1
    artifact = context.generated_assets[0]
    assert artifact.destination == Path(
        "canon/concept/NUM-CON-000001-derivative/README.md"
    )
    assert "Derivative" in artifact.content
    assert "NUM-CON-000001" in artifact.content


def test_characters_also_get_a_character_card(tmp_path: Path) -> None:
    write_entity(
        tmp_path / "characters" / "NUM-CHR-000001-derivative",
        id="NUM-CHR-000001",
        type="Character",
        status="CANON",
        version="1.0.0",
        name="Derivative",
        slug="derivative",
    )

    context = CompilerContext(project_root=tmp_path)
    LoadCanonStage(knowledge_root=tmp_path).execute(context)
    GenerateMissingAssetsStage(TEMPLATE_ROOT).execute(context)

    destinations = {a.destination.name for a in context.generated_assets}
    assert destinations == {"README.md", "CHARACTER_CARD.md"}


def test_lesson_and_assessment_route_to_dedicated_buckets(tmp_path: Path) -> None:
    write_entity(
        tmp_path / "lessons" / "NUM-LESSON-000001",
        id="NUM-LESSON-000001",
        type="Lesson",
        status="CANON",
        version="1.0.0",
        name="Intro to Derivatives",
    )
    write_entity(
        tmp_path / "assessments" / "NUM-ASMT-000001",
        id="NUM-ASMT-000001",
        type="Assessment",
        status="CANON",
        version="1.0.0",
        name="Derivative Quiz",
    )

    context = CompilerContext(project_root=tmp_path)
    LoadCanonStage(knowledge_root=tmp_path).execute(context)
    GenerateMissingAssetsStage(TEMPLATE_ROOT).execute(context)

    top_level_dirs = {a.destination.parts[0] for a in context.generated_assets}
    assert top_level_dirs == {"lessons", "assessments"}


def test_missing_title_and_slug_fall_back_gracefully(tmp_path: Path) -> None:
    # No `name`, `title`, or `slug` field at all -- must not raise
    # (StrictUndefined would otherwise reject the template render).
    write_entity(
        tmp_path / "concepts" / "NUM-CON-000001",
        id="NUM-CON-000001",
        type="Concept",
        status="CANON",
        version="1.0.0",
    )

    context = CompilerContext(project_root=tmp_path)
    LoadCanonStage(knowledge_root=tmp_path).execute(context)
    GenerateMissingAssetsStage(TEMPLATE_ROOT).execute(context)

    assert len(context.generated_assets) == 1
    assert "NUM-CON-000001" in context.generated_assets[0].content


def test_relationship_entities_are_not_rendered(tmp_path: Path) -> None:
    write_entity(
        tmp_path / "concepts" / "NUM-CON-000001",
        id="NUM-CON-000001",
        type="Concept",
        status="CANON",
        version="1.0.0",
        name="Derivative",
    )
    write_entity(
        tmp_path / "concepts" / "NUM-CON-000002",
        id="NUM-CON-000002",
        type="Concept",
        status="CANON",
        version="1.0.0",
        name="Limit",
    )
    write_entity(
        tmp_path / "relationships" / "NUM-REL-000001",
        id="NUM-REL-000001",
        type="REQUIRES",
        status="CANON",
        version="1.0.0",
    )

    context = CompilerContext(project_root=tmp_path)
    LoadCanonStage(knowledge_root=tmp_path).execute(context)
    GenerateMissingAssetsStage(TEMPLATE_ROOT).execute(context)

    # 2 concepts * 1 readme each == 2, not 3.
    assert len(context.generated_assets) == 2
