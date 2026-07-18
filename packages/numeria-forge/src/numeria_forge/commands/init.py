from pathlib import Path

import typer
from rich.console import Console

console = Console()


def init_repository(
    path: Path = typer.Argument(
        Path("."),
        help="Directory to initialize as a Numeria repository.",
    ),
) -> None:
    """Initialize or verify a Numeria repository."""

    root = path.resolve()

    required_directories = [
        "docs/foundation",
        "knowledge/concepts",
        "knowledge/graph",
        "characters",
        "stories",
        "lessons",
        "assessments",
        "animation",
        "short-videos",
    ]

    created: list[str] = []

    for relative_directory in required_directories:
        directory = root / relative_directory

        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            created.append(relative_directory)

    marker = root / ".numeria"

    if not marker.exists():
        marker.write_text(
            "version: 0.1.0\n"
            "platform: numeria\n"
            "created_by: numeria-forge\n",
            encoding="utf-8",
        )
        created.append(".numeria")

    console.print()
    console.print("[bold green]Numeria repository is ready.[/bold green]")
    console.print(f"[dim]Location:[/dim] {root}")

    if created:
        console.print()
        console.print("[bold]Created:[/bold]")

        for item in created:
            console.print(f"  [green]+[/green] {item}")
    else:
        console.print(
            "[yellow]No changes were required. The repository is already initialized.[/yellow]"
        )
