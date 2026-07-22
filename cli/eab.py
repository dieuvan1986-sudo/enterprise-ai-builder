from pathlib import Path

import typer
from rich import print

from builder.project import (
    create_project,
    load_project,
    load_workflow,
)
from runtime.engine import RuntimeEngine

app = typer.Typer(
    help="Enterprise AI Builder CLI",
    no_args_is_help=True,
)


@app.command()
def version():
    """Show Enterprise AI Builder version."""
    print("[green]Enterprise AI Builder v0.1.0[/green]")


@app.command()
def init(path: str = "."):
    """Create a new Enterprise AI Builder project."""
    create_project(path)
    print(f"[green]Project initialized:[/green] {path}")


@app.command()
def validate():
    """Validate the current project."""
    print("[yellow]Validate command is not implemented yet.[/yellow]")


@app.command()
def build():
    """Build the current project."""
    print("[yellow]Build command is not implemented yet.[/yellow]")


@app.command()
def run():
    """Run the current project workflow."""

    project = load_project()

    workflow_path = Path(project["workflow"])
    workflow = load_workflow(workflow_path)

    print("[cyan]Enterprise AI Builder[/cyan]")
    print(f"[green]Project:[/green] {project['name']}")
    print()

    RuntimeEngine(project).run(workflow)


def main():
    app()


if __name__ == "__main__":
    main()
