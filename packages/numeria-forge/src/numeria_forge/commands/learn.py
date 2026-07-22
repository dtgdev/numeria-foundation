"""`forge learn` -- the Learning Graph (v0.18.0), on top of the same
`CanonicalKnowledgeModel` `forge graph` already builds.

    forge learn prerequisites   -- everything required before a Concept
    forge learn path            -- the ordered sequence to learn it in

Deliberately narrow. `forge learn` answers questions about the
*content graph* (what depends on what, what order to learn it in) --
it does not track, store, or reason about any individual learner's
progress, mastery, or state. See
`docs/architecture/ADR-0007-learner-state-excluded.md` for why: Canon
is versioned, immutable, authored content (Canon Law #2); a learner's
progress is mutable, per-person, and not canonical in that sense. A
`forge learn next` / `forge learn competency` command, if built, would
need a Learner concept this codebase does not have -- not something
to invent unprompted alongside the two commands that *are* pure
functions of the Canon.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from numeria_forge.commands._shared import resolve_knowledge_root

console = Console()

learn_app = typer.Typer(
    help="Query the Learning Graph: prerequisites and ordered learning paths.",
    no_args_is_help=True,
)

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


def _entity_dict(entity) -> dict:
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


@learn_app.command("prerequisites")
def prerequisites_command(
    entity_id: str,
    path: Path = typer.Argument(None, help=PATH_HELP),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """Everything ENTITY_ID transitively requires, nearest first.

    Same data as `forge graph query prerequisites` -- `forge learn` is
    a learner-facing entry point over the same `KnowledgeQuery`, not a
    second implementation.
    """

    model = _model(path)
    _print_entities(model.query.prerequisites_of(entity_id), as_json)


@learn_app.command("path")
def path_command(
    entity_id: str,
    path: Path = typer.Argument(None, help=PATH_HELP),
    as_json: bool = typer.Option(False, "--json"),
) -> None:
    """The ordered sequence to learn before (and including) ENTITY_ID,
    prerequisites first.

    Unlike `prerequisites`, this is a *sequence*, not just a set --
    `KnowledgeQuery.learning_path()` (v0.18.0). Empty if ENTITY_ID is
    unknown, if the ontology declares no `acyclic` relationship type,
    or if the graph has an actual dependency cycle (run `forge graph
    build` to find it first).
    """

    model = _model(path)
    entities = model.query.learning_path(entity_id)

    if not entities and entity_id in model.graph.nodes:
        console.print(
            "[yellow]No learning path could be computed[/yellow] -- either "
            "no relationship type is declared `acyclic` in the ontology, or "
            "the graph has a dependency cycle. Run [bold]forge graph "
            "build[/bold] to check."
        )

        if as_json:
            console.print_json(data=[])

        return

    if as_json:
        console.print_json(
            data=[dict(_entity_dict(entity), step=index) for index, entity in enumerate(entities, start=1)]
        )
        return

    if not entities:
        console.print("(none)")
        return

    for index, entity in enumerate(entities, start=1):
        name = entity.get("name") or ""
        console.print(f"  {index}. [bold]{entity.id}[/bold] ({entity.type})  {name}")
