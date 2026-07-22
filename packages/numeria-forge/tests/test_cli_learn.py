"""`forge learn prerequisites` / `forge learn path` -- CLI tests.

Same `CliRunner` pattern as `tests/test_cli_graph.py`.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from numeria_forge.cli import app

runner = CliRunner()


def _write_entity(directory: Path, **fields: object) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "entity.yaml").write_text(
        yaml.safe_dump(fields, sort_keys=False), encoding="utf-8"
    )


def _seed_derivative_chain(tmp_path: Path) -> None:
    """`forge init`, then Constant/Variable -> Function -> Limit ->
    Derivative, the same chain the real Canon has."""

    init_result = runner.invoke(app, ["init", str(tmp_path)])
    assert init_result.exit_code == 0

    knowledge_root = tmp_path / "knowledge"

    for entity_id, name in (
        ("NUM-CON-000001", "Constant"),
        ("NUM-CON-000002", "Variable"),
        ("NUM-CON-000003", "Function"),
        ("NUM-CON-000004", "Limit"),
        ("NUM-CON-000005", "Derivative"),
    ):
        _write_entity(
            knowledge_root / "concepts" / f"{entity_id}-{name.lower()}",
            id=entity_id, type="Concept", status="CANON", version="1.0.0",
            name=name,
        )

    relationships = (
        ("NUM-REL-000001", "NUM-CON-000003", "NUM-CON-000001"),  # Function requires Constant
        ("NUM-REL-000002", "NUM-CON-000003", "NUM-CON-000002"),  # Function requires Variable
        ("NUM-REL-000003", "NUM-CON-000004", "NUM-CON-000003"),  # Limit requires Function
        ("NUM-REL-000004", "NUM-CON-000005", "NUM-CON-000004"),  # Derivative requires Limit
    )

    for rel_id, source_id, target_id in relationships:
        _write_entity(
            knowledge_root / "relationships" / rel_id,
            id=rel_id, type="REQUIRES", status="CANON", version="1.0.0",
            source={"id": source_id, "type": "Concept"},
            target={"id": target_id, "type": "Concept"},
        )


def test_learn_help_lists_both_subcommands() -> None:
    result = runner.invoke(app, ["learn", "--help"])

    assert result.exit_code == 0
    assert "prerequisites" in result.stdout
    assert "path" in result.stdout


def test_learn_prerequisites(tmp_path: Path) -> None:
    _seed_derivative_chain(tmp_path)

    result = runner.invoke(
        app, ["learn", "prerequisites", "NUM-CON-000005", str(tmp_path)]
    )

    assert result.exit_code == 0
    for entity_id in (
        "NUM-CON-000001", "NUM-CON-000002", "NUM-CON-000003", "NUM-CON-000004",
    ):
        assert entity_id in result.stdout
    assert result.stdout.count("NUM-CON-000005") == 0


def test_learn_path_ends_with_the_target_and_is_numbered(tmp_path: Path) -> None:
    _seed_derivative_chain(tmp_path)

    result = runner.invoke(app, ["learn", "path", "NUM-CON-000005", str(tmp_path)])

    assert result.exit_code == 0
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert lines[-1].strip().startswith("5.")
    assert "NUM-CON-000005" in lines[-1]
    assert "Derivative" in lines[-1]


def test_learn_path_json_is_ordered_and_ends_with_the_target(tmp_path: Path) -> None:
    _seed_derivative_chain(tmp_path)

    result = runner.invoke(
        app, ["learn", "path", "NUM-CON-000005", str(tmp_path), "--json"]
    )

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data[-1]["id"] == "NUM-CON-000005"
    assert [item["step"] for item in data] == list(range(1, len(data) + 1))
    assert {item["id"] for item in data} == {
        "NUM-CON-000001", "NUM-CON-000002", "NUM-CON-000003", "NUM-CON-000004",
        "NUM-CON-000005",
    }


def test_learn_path_for_a_leaf_concept_is_just_itself(tmp_path: Path) -> None:
    _seed_derivative_chain(tmp_path)

    result = runner.invoke(app, ["learn", "path", "NUM-CON-000001", str(tmp_path)])

    assert result.exit_code == 0
    assert "1. " in result.stdout
    assert "NUM-CON-000001" in result.stdout
    assert "NUM-CON-000005" not in result.stdout
