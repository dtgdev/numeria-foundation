from pathlib import Path

from numeria_forge.domain.canon.validation import CanonValidationRunner


def write_entity(path: Path, **fields) -> None:
    path.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}: {value}" for key, value in fields.items()]
    (path / "entity.yaml").write_text("\n".join(lines), encoding="utf-8")


def write_ontology(knowledge_root: Path) -> None:
    ontology_dir = knowledge_root / "ontology"
    ontology_dir.mkdir(parents=True, exist_ok=True)
    (ontology_dir / "relationship-types.yaml").write_text(
        "version: 1.0.0\nstatus: CANON\nrelationship_types: {}\n",
        encoding="utf-8",
    )


def test_runner_reports_clean_canon(tmp_path: Path) -> None:
    write_entity(
        tmp_path / "characters" / "NUM-CHR-000001-derivative",
        id="NUM-CHR-000001",
        type="Character",
        status="CANON",
        version="1.0.0",
        name="Derivative",
        role="Detective",
        slug="derivative",
    )
    write_ontology(tmp_path)

    report = CanonValidationRunner().run(tmp_path)

    assert report.success is True
    assert report.entity_count == 1
    assert report.diagnostics == ()


def test_runner_reports_issues(tmp_path: Path) -> None:
    write_entity(
        tmp_path / "characters" / "wrong-dir",
        id="NUM-CHR-000001",
        type="Character",
        status="draft",
        version="1.0.0",
        name="Derivative",
    )
    write_ontology(tmp_path)

    report = CanonValidationRunner().run(tmp_path)

    assert report.success is False
    assert len(report.errors) > 0
