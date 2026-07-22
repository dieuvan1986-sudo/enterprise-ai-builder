#!/usr/bin/env python3
"""
Enterprise AI Builder (EAB)
CLI v0.4.0
"""

import typer
from rich import print

from builder.project import create_project

VERSION = "0.4.0"

app = typer.Typer(
    name="eab",
    help="Enterprise AI Builder CLI",
    no_args_is_help=True,
)


@app.command()
def version():
    """Show Enterprise AI Builder version."""
    print(f"[green]Enterprise AI Builder[/green] v{VERSION}")


@app.command()
def init(
    name: str = typer.Argument(..., help="Project name"),
):
    """Create a new Enterprise AI Builder project."""

    try:
        create_project(name)
        print(f"[green]✓ Project '{name}' created successfully![/green]")
    except FileExistsError as exc:
        print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)


@app.command()
def validate():
    """Validate the current project."""
    print("[yellow]Validation is not implemented yet.[/yellow]")


@app.command()
def build():
    """Build the current project."""
    print("[yellow]Build is not implemented yet.[/yellow]")


def main():
    app()


if __name__ == "__main__":
    main()
