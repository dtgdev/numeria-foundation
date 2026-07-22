from pathlib import Path

from numeria_forge.domain.canon import CanonLoader


def write_entity(path: Path, **fields) -> None:
    path.mkdir(parents=True, exist_ok=True)
    lines = [f"{key}: {value}" for key, value in fields.items()]
    (path / "entity.yaml").write_text("\n".join(lines), encoding="utf-8")


def test_loads_every_entity(tmp_path: Path) -> None:
    write_entity(
        tmp_path / "characters" / "NUM-CHR-000001-derivative",
        id="NUM-CHR-000001",
        type="Character",
        status="CANON",
        version="1.0.0",
        name="Derivative",
    )

    write_entity(
        tmp_path / "concepts" / "NUM-CON-000001-derivative",
        id="NUM-CON-000001",
        type="Concept",
        status="CANON",
        version="1.0.0",
        name="Derivative",
    )

    canon = CanonLoader().load(tmp_path)

    assert len(canon) == 2
    assert not canon.load_errors
    assert "NUM-CHR-000001" in canon
    assert canon.entities["NUM-CHR-000001"].type == "Character"
    assert len(canon.by_type("Concept")) == 1


def test_missing_knowledge_root_is_a_load_error(tmp_path: Path) -> None:
    canon = CanonLoader().load(tmp_path / "does-not-exist")

    assert len(canon) == 0
    assert len(canon.load_errors) == 1
    assert "does not exist" in canon.load_errors[0].message


def test_invalid_yaml_is_a_load_error_not_a_crash(tmp_path: Path) -> None:
    bad = tmp_path / "characters" / "broken"
    bad.mkdir(parents=True)
    (bad / "entity.yaml").write_text("id: [unterminated", encoding="utf-8")

    canon = CanonLoader().load(tmp_path)

    assert len(canon) == 0
    assert len(canon.load_errors) == 1
    assert "Invalid YAML" in canon.load_errors[0].message


def test_duplicate_id_is_a_load_error(tmp_path: Path) -> None:
    write_entity(
        tmp_path / "characters" / "a",
        id="NUM-CHR-000001",
        type="Character",
        status="CANON",
        version="1.0.0",
    )
    write_entity(
        tmp_path / "characters" / "b",
        id="NUM-CHR-000001",
        type="Character",
        status="CANON",
        version="1.0.0",
    )

    canon = CanonLoader().load(tmp_path)

    assert len(canon) == 1
    assert len(canon.load_errors) == 1
    assert "Duplicate id" in canon.load_errors[0].message


def test_relationship_entities_are_detected_by_directory(tmp_path: Path) -> None:
    write_entity(
        tmp_path / "relationships" / "NUM-REL-000001-a-features-b",
        id="NUM-REL-000001",
        type="FEATURES_CHARACTER",
        status="CANON",
        version="1.0.0",
    )

    canon = CanonLoader().load(tmp_path)
    entity = canon.entities["NUM-REL-000001"]

    assert entity.is_relationship is True
    assert canon.relationships() == (entity,)
    assert canon.non_relationships() == ()
