"""`forge graph build/validate/export/query` -- CLI tests.

Uses `typer.testing.CliRunner` for real CLI invocation (proper
argument parsing, nested `graph query <verb>` subcommands), the same
pattern `tests/test_cli.py` uses for `init`/`validate`/`doctor`.
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


def _seed_foundation(tmp_path: Path) -> None:
    """`forge init`, then a small REQUIRES chain plus one deliberate
    orphan: Function REQUIRES Variable, Isolated connects to nothing.
    Reuses `forge init`'s default ontology, which already marks
    REQUIRES `acyclic: true`.
    """

    init_result = runner.invoke(app, ["init", str(tmp_path)])
    assert init_result.exit_code == 0

    knowledge_root = tmp_path / "knowledge"

    for entity_id, name in (
        ("NUM-CON-000001", "Function"),
        ("NUM-CON-000002", "Variable"),
        ("NUM-CON-000003", "Isolated"),
    ):
        _write_entity(
            knowledge_root / "concepts" / f"{entity_id}-{name.lower()}",
            id=entity_id, type="Concept", status="CANON", version="1.0.0",
            name=name,
        )

    _write_entity(
        knowledge_root / "relationships" / "NUM-REL-000001",
        id="NUM-REL-000001", type="REQUIRES", status="CANON", version="1.0.0",
        source={"id": "NUM-CON-000001", "type": "Concept"},
        target={"id": "NUM-CON-000002", "type": "Concept"},
    )


def test_graph_help_lists_all_four_subcommands() -> None:
    result = runner.invoke(app, ["graph", "--help"])

    assert result.exit_code == 0

    for name in ("build", "validate", "export", "query"):
        assert name in result.stdout


# --------------------------------------------------------------- build


def test_graph_build_reports_shape(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)

    result = runner.invoke(app, ["graph", "build", str(tmp_path)])

    assert result.exit_code == 0
    assert "3 node(s), 1 edge(s)" in result.stdout
    assert "1 orphaned entity" in result.stdout
    assert "No dependency cycles." in result.stdout


def test_graph_build_json(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)

    result = runner.invoke(app, ["graph", "build", str(tmp_path), "--json"])

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["graph_statistics"]["node_count"] == 3
    assert data["cycles"] == []


def test_graph_build_exits_1_on_a_cycle(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)

    _write_entity(
        tmp_path / "knowledge" / "relationships" / "NUM-REL-000002",
        id="NUM-REL-000002", type="REQUIRES", status="CANON", version="1.0.0",
        source={"id": "NUM-CON-000002", "type": "Concept"},
        target={"id": "NUM-CON-000001", "type": "Concept"},
    )

    result = runner.invoke(app, ["graph", "build", str(tmp_path)])

    assert result.exit_code == 1
    assert "dependency cycle" in result.stdout.lower()


# ------------------------------------------------------------ validate


def test_graph_validate_reports_orphan_warning_but_exits_0(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)

    result = runner.invoke(app, ["graph", "validate", str(tmp_path)])

    assert result.exit_code == 0
    assert "canon.semantics.orphaned-entity" in result.stdout
    assert "NUM-CON-000003" in result.stdout


def test_graph_validate_exits_1_on_a_cycle(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)

    _write_entity(
        tmp_path / "knowledge" / "relationships" / "NUM-REL-000002",
        id="NUM-REL-000002", type="REQUIRES", status="CANON", version="1.0.0",
        source={"id": "NUM-CON-000002", "type": "Concept"},
        target={"id": "NUM-CON-000001", "type": "Concept"},
    )

    result = runner.invoke(app, ["graph", "validate", str(tmp_path)])

    assert result.exit_code == 1
    assert "canon.semantics.dependency-cycle" in result.stdout


# -------------------------------------------------------------- export


def test_graph_export_writes_three_files_by_default(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)

    result = runner.invoke(app, ["graph", "export", str(tmp_path)])

    assert result.exit_code == 0
    graph_dir = tmp_path / "build" / "graph"
    assert (graph_dir / "knowledge.json").is_file()
    assert (graph_dir / "knowledge.yaml").is_file()
    assert (graph_dir / "knowledge.graphml").is_file()


def test_graph_export_single_format_to_custom_output(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)
    output_dir = tmp_path / "custom-out"

    result = runner.invoke(
        app,
        [
            "graph", "export", str(tmp_path),
            "--format", "json", "--output", str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert (output_dir / "knowledge.json").is_file()
    assert not (output_dir / "knowledge.yaml").exists()


def test_graph_export_rejects_an_unknown_format(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)

    result = runner.invoke(app, ["graph", "export", str(tmp_path), "--format", "xml"])

    assert result.exit_code == 1
    assert "Unknown format" in result.stdout


def test_graph_export_stdout_requires_a_single_format(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)

    result = runner.invoke(app, ["graph", "export", str(tmp_path), "--stdout"])

    assert result.exit_code == 1
    assert "requires a single --format" in result.stdout


def test_graph_export_stdout_prints_the_requested_format(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)

    result = runner.invoke(
        app, ["graph", "export", str(tmp_path), "--format", "yaml", "--stdout"]
    )

    assert result.exit_code == 0
    data = yaml.safe_load(result.stdout)
    assert data["schema"] == "numeria.knowledge-graph.v1"


# --------------------------------------------------------------- query


def test_graph_query_get(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)

    result = runner.invoke(
        app, ["graph", "query", "get", "NUM-CON-000001", str(tmp_path)]
    )

    assert result.exit_code == 0
    assert "NUM-CON-000001" in result.stdout
    assert "Function" in result.stdout


def test_graph_query_get_unknown_id_exits_1(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)

    result = runner.invoke(app, ["graph", "query", "get", "NOPE", str(tmp_path)])

    assert result.exit_code == 1
    assert "Not found" in result.stdout


def test_graph_query_prerequisites(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)

    result = runner.invoke(
        app, ["graph", "query", "prerequisites", "NUM-CON-000001", str(tmp_path)]
    )

    assert result.exit_code == 0
    assert "NUM-CON-000002" in result.stdout


def test_graph_query_related_with_direction(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)

    result = runner.invoke(
        app,
        [
            "graph", "query", "related", "NUM-CON-000002", "REQUIRES",
            str(tmp_path), "--direction", "incoming",
        ],
    )

    assert result.exit_code == 0
    assert "NUM-CON-000001" in result.stdout


def test_graph_query_traverse_with_max_depth(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)

    result = runner.invoke(
        app,
        [
            "graph", "query", "traverse", "NUM-CON-000001", str(tmp_path),
            "--types", "REQUIRES", "--max-depth", "1",
        ],
    )

    assert result.exit_code == 0
    assert "NUM-CON-000002" in result.stdout


def test_graph_query_orphans(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)

    result = runner.invoke(app, ["graph", "query", "orphans", str(tmp_path)])

    assert result.exit_code == 0
    assert "NUM-CON-000003" in result.stdout


def test_graph_query_stats_json(tmp_path: Path) -> None:
    _seed_foundation(tmp_path)

    result = runner.invoke(
        app, ["graph", "query", "stats", str(tmp_path), "--json"]
    )

    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["node_count"] == 3
    assert data["orphaned_node_count"] == 1
