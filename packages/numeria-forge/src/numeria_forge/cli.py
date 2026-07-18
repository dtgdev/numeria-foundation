import typer
from rich.console import Console

from numeria_forge import __version__
from numeria_forge.commands.init import init_repository

console = Console()

app = typer.Typer(
    name="forge",
    help="Forge mathematical worlds from canonical knowledge.",
    no_args_is_help=True,
    add_completion=False,
)


@app.command("version")
def version_command() -> None:
    """Display the installed Numeria Forge version."""

    console.print(f"Numeria Forge [bold]{__version__}[/bold]")


app.command("init")(init_repository)


def main() -> None:
    app()


if __name__ == "__main__":
    main()

new_app = typer.Typer(help="Generate new knowledge artifacts.")

app.add_typer(new_app, name="new")

@new_app.command("concept")
def new_concept(
    name: str,
):
    from pathlib import Path

    from rich import print

    from numeria_forge.application.services.concept_service import (
        ConceptService,
    )

    service = ConceptService()

    files = service.create(
        Path.cwd(),
        name=name,
        canonical_id=f"concept.{name.lower()}",
        domain="mathematics",
    )

    print("[green]Created:[/green]")

    for file in files:
        print(f" • {file}")