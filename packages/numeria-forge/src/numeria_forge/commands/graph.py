"""`forge graph` -- build, validate, export, and query the Canonical
Knowledge Graph (v0.16.0/v0.17.0) directly, without running the full
`forge compile` pipeline (no template rendering, no package
generation, no `templates/` directory required -- just
Canon -> SemanticGraph -> CanonicalKnowledgeModel, and the query API
and export formats built on top of it).

    forge graph build       -- load + build the graph, report its shape
    forge graph validate    -- run the two semantics validators
                                (dependency cycles, orphaned entities)
    forge graph export      -- write/print knowledge.{json,yaml,graphml}
    forge graph query ...   -- get / related / prerequisites / traverse
                                / orphans / stats, over KnowledgeQuery
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import typer
from rich.console import Console

from numeria_forge.commands._shared import resolve_knowledge_root

console = Console()

graph_app = typer.Typer(
    help="Build, validate, export, and query the knowledge graph.",
    no_args_is_help=True,
)
query_app = typer.Typer(
    help=(
        "Query the knowledge graph: get / related / prerequisites / "
        "traverse / orphans / stats."
    ),
    no_args_is_help=True,
)
graph_app.add_typer(query_app, name="query")

PATH_HELP = (
    "Foundation root (containing numeria.yaml), a directory containing "
    "knowledge/, or a knowledge root itself. Defaults to the current "
    "directory."
)


def _model(path: Path | None):
    from numeria_forge.knowledge import CanonicalKnowledgeModel

    target = path if path is not None else Path.cwd()
    knowledge_root = resolve_knowledge_root(target)

    return CanonicalKnowledgeModel.build_from_root(knowledge_root)


def _entity_dict(entity: Any) -> dict:
    return {"id": entity.id, "type": entity.type, "name": entity.get("name")}


def _print_entities(entities, as_json: bool) -> None:
    if as_json:
        console.print_json(data=[_entity_dict(entity) for entity in entities])
        return

    if not entities:
        console.print("(none)")
        return

    for entity in entities:
        name = entity.get("name") or ""
        console.print(f"  [bold]{entity.id}[/bold] ({entity.type})  {name}")


# --------------------------------------------------------------- build


@graph_app.command("build")
def build_command(
    path: Path = typer.Argument(None, help=PATH_HELP),
    as_json: bool = typer.Option(False, "--json", help="Emit as JSON."),
) -> None:
    """Build the knowledge graph from the Canon and report its shape.

    Loads the Canon and ontology, builds the SemanticGraph, and checks
    every ontology-declared `acyclic` relationship type for cycles --
    the same graph-building step `forge compile` runs (`DependencyGraphStage`
    + `TopologicalOrderStage` + `BuildKnowledgeModelStage`), without
    also running full Canon validation or generating/publishing
    anything. Exits 1 if a dependency cycle is found.
    """

    from numeria_forge.knowledge.statistics import GraphStatistics
    from numeria_forge.semantics import CycleDetector

    model = _model(path)
    stats = GraphStatistics.from_model(model)
    cycles = CycleDetector(model.graph).find_cycles(
        types=model.ontology.acyclic_type_names()
    )

    if as_json:
        console.print_json(
            data={
                "graph_statistics": stats.to_dict(),
                "cycles": [list(cycle.nodes) for cycle in cycles],
            }
        )
    else:
        console.print()
        console.print("[bold]Knowledge graph[/bold]")
        console.print(f"  {stats.node_count} node(s), {stats.edge_count} edge(s)")
        console.print(
            f"  {stats.orphaned_node_count} orphaned entit"
            f"{'y' if stats.orphaned_node_count == 1 else 'ies'}"
        )

        if stats.edge_type_counts:
            console.print()
            console.print("  Edges by type:")

            for relationship_type, count in sorted(stats.edge_type_counts.items()):
                console.print(f"    {relationship_type}: {count}")

        console.print()

        if cycles:
            console.print(
                f"[bold red]{len(cycles)} dependency cycle(s) found:[/bold red]"
            )

            for cycle in cycles:
                console.print(f"  {cycle}")
        else:
            console.print("[bold green]No dependency cycles.[/bold green]")

    if cycles:
        raise typer.Exit(code=1)


# ------------------------------------------------------------ validate


@graph_app.command("validate")
def validate_command(
    path: Path = typer.Argument(None, help=PATH_HELP),
    as_json: bool = typer.Option(False, "--json", help="Emit as JSON."),
) -> None:
    """Run the graph-specific semantic checks: dependency cycles and
    orphaned entities.

    Distinct from `forge validate`, which runs the full ten-validator
    Canon Validation Engine (schema, identity, relationships, ...).
    This runs only `DependencyGraphValidator` and
    `OrphanedEntityValidator` -- both opt-in, not part of `forge
    validate`'s default set (see `docs/architecture/SEMANTIC_LAYER.md`
    and `CANONICAL_KNOWLEDGE_MODEL.md` for why). This is how you check
    them without changing that default. Exits 1 only on a cycle
    (ERROR); orphans are WARNING and don't fail the exit code.
    """

    from numeria_forge.domain.canon.validation import CanonValidationRunner
    from numeria_forge.semantics import (
        DependencyGraphValidator,
        OrphanedEntityValidator,
    )

    target = path if path is not None else Path.cwd()
    knowledge_root = resolve_knowledge_root(target)

    report = CanonValidationRunner(
        validators=(DependencyGraphValidator(), OrphanedEntityValidator())
    ).run(knowledge_root)

    if as_json:
        console.print_json(report.to_json())
    else:
        console.print(report.format_human_readable())

    if not report.success:
        raise typer.Exit(code=1)


# -------------------------------------------------------------- export


@graph_app.command("export")
def export_command(
    path: Path = typer.Argument(None, help=PATH_HELP),
    output: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="Directory to write export files into. Defaults to <path>/build/graph/.",
    ),
    fmt: str = typer.Option(
        "all",
        "--format",
        "-f",
        help="One of: json, yaml, graphml, all (default).",
    ),
    to_stdout: bool = typer.Option(
        False,
        "--stdout",
        help=(
            "Print to stdout instead of writing a file. Requires "
            "--format to be a single format, not 'all'."
        ),
    ),
) -> None:
    """Export the knowledge graph to JSON, YAML, and/or GraphML.

    Writes the same three files `PublishKnowledgeGraphStage` writes as
    part of `forge compile` (`build/graph/knowledge.{json,yaml,graphml}`),
    but standalone -- no template rendering or package generation
    required, so this works even in a Foundation with no `templates/`
    directory set up yet.
    """

    from numeria_forge.knowledge import export as graph_export

    valid_formats = {"json", "yaml", "graphml", "all"}

    if fmt not in valid_formats:
        console.print(
            f"[bold red]Unknown format '{fmt}'[/bold red] -- choose one "
            f"of {sorted(valid_formats)}."
        )
        raise typer.Exit(code=1)

    renderers = {
        "json": graph_export.to_json,
        "yaml": graph_export.to_yaml,
        "graphml": graph_export.to_graphml,
    }

    if to_stdout:
        if fmt == "all":
            console.print(
                "[bold red]--stdout requires a single --format, not "
                "'all'.[/bold red]"
            )
            raise typer.Exit(code=1)

        model = _model(path)
        print(renderers[fmt](model))
        return

    model = _model(path)
    formats = ("json", "yaml", "graphml") if fmt == "all" else (fmt,)

    target = path if path is not None else Path.cwd()
    output_directory = (
        output if output is not None else (target.resolve() / "build" / "graph")
    )
    output_directory.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []

    for name in formats:
        destination = output_directory / f"knowledge.{name}"
        destination.write_text(renderers[name](model), encoding="utf-8")
        written.append(destination)

    console.print("[bold green]Exported:[/bold green]")

    for destination in written:
        console.print(f"  {destination}")


# --------------------------------------------------------------- query


@query_app.command("get")
def query_get(
    entity_id: str,
    path: Path = typer.Argument(None, help=PATH_HELP),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Look up one entity by canonical id."""

    model = _model(path)
    entity = model.query.get(entity_id)

    if entity is None:
        console.print(f"[bold red]Not found:[/bold red] {entity_id}")
        raise typer.Exit(code=1)

    if as_json:
        console.print_json(data=_entity_dict(entity))
    else:
        name = entity.get("name") or ""
        console.print(f"[bold]{entity.id}[/bold] ({entity.type})  {name}")


@query_app.command("related")
def query_related(
    entity_id: str,
    relationship_type: str,
    path: Path = typer.Argument(None, help=PATH_HELP),
    direction: str = typer.Option(
        "outgoing", "--direction", help="outgoing or incoming."
    ),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Entities directly connected to ENTITY_ID by one relationship type.

    E.g. `forge graph query related NUM-CON-000001 REPRESENTED_BY` --
    the Character representing a Concept; add `--direction incoming`
    to ask the reverse ("which Lessons TEACHES_CONCEPT this Concept").
    """

    model = _model(path)
    entities = model.query.related(entity_id, relationship_type, direction=direction)
    _print_entities(entities, as_json)


@query_app.command("prerequisites")
def query_prerequisites(
    entity_id: str,
    path: Path = typer.Argument(None, help=PATH_HELP),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Everything ENTITY_ID transitively requires, nearest first."""

    model = _model(path)
    entities = model.query.prerequisites_of(entity_id)
    _print_entities(entities, as_json)


@query_app.command("traverse")
def query_traverse(
    entity_id: str,
    path: Path = typer.Argument(None, help=PATH_HELP),
    types: str = typer.Option(
        None,
        "--types",
        help="Comma-separated relationship types. Default: every type.",
    ),
    direction: str = typer.Option(
        "outgoing", "--direction", help="outgoing or incoming."
    ),
    max_depth: int = typer.Option(
        None, "--max-depth", help="Limit how many hops to walk."
    ),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Breadth-first walk from ENTITY_ID, nearest first."""

    model = _model(path)
    type_tuple = (
        tuple(t.strip() for t in types.split(",") if t.strip()) if types else None
    )
    ids = model.query.traverse(
        entity_id, types=type_tuple, direction=direction, max_depth=max_depth
    )

    if as_json:
        console.print_json(data={"ids": list(ids)})
        return

    if not ids:
        console.print("(none)")
        return

    for found_id in ids:
        entity = model.query.get(found_id)
        name = entity.get("name") if entity is not None else ""
        console.print(f"  {found_id}  {name or ''}")


@query_app.command("orphans")
def query_orphans(
    path: Path = typer.Argument(None, help=PATH_HELP),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Entities touched by zero relationships in either direction."""

    model = _model(path)
    _print_entities(model.query.orphaned_entities(), as_json)


@query_app.command("stats")
def query_stats(
    path: Path = typer.Argument(None, help=PATH_HELP),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Graph statistics: node/edge counts, per-type breakdown, orphans."""

    from numeria_forge.knowledge.statistics import GraphStatistics

    model = _model(path)
    stats = GraphStatistics.from_model(model)

    if as_json:
        console.print_json(data=stats.to_dict())
        return

    console.print(f"Nodes: {stats.node_count}")
    console.print(f"Edges: {stats.edge_count}")
    console.print(f"Orphaned: {stats.orphaned_node_count}")
    console.print(
        "Acyclic relationship types: "
        + (", ".join(stats.acyclic_relationship_types) or "(none)")
    )

    if stats.edge_type_counts:
        console.print()
        console.print("Edges by type:")

        for relationship_type, count in sorted(stats.edge_type_counts.items()):
            console.print(f"  {relationship_type}: {count}")
