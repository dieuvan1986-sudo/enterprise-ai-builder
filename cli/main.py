from pathlib import Path

import typer
from rich import print

from builder.project import create_project

app = typer.Typer(
    help="Enterprise AI Builder",
    no_args_is_help=True,
)


@app.command()
def version():
    """Show application version."""
    print("[green]Enterprise AI Builder v0.1.0[/green]")


@app.command()
def init(path: str = "."):
    """Initialize a new Enterprise AI Builder project."""
    create_project(Path(path))
    print(f"[green]Project initialized at:[/green] {Path(path).resolve()}")


@app.command()
def validate():
    """Validate project configuration."""
    print("[yellow]Validate command is not implemented yet.[/yellow]")


@app.command()
def build():
    """Build project artifacts."""
    print("[yellow]Build command is not implemented yet.[/yellow]")


@app.command()
def run():
    """Run the project workflow."""
    print("[cyan]Enterprise AI Builder[/cyan]")
    print("[green]Starting workflow...[/green]")
    print("[yellow]Run engine is not implemented yet.[/yellow]")


def main():
    app()


if __name__ == "__main__":
    main()
