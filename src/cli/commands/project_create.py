from pathlib import Path
from typing import Optional
import typer
from src.cli.utils.error_handler import api_error_handler
from src.cli.project import Project
from src.cli.context import IwadiContext

app = typer.Typer()


@app.command()
@api_error_handler
def create(
    name: str = typer.Argument(..., help="Project name (alphanumeric + underscores)"),
    base_path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        help="Custom parent directory (default: ~/iwadi_projects)",
        file_okay=False,
        dir_okay=True,
        writable=True,
        resolve_path=True,
    ),
    ctx: Optional[typer.Context] = None,
) -> None:
    """
    Create a new research project with organized directory structure.

    Example:
    iwadi project create quantum_ml
    """
    assert ctx is not None
    iwadi_ctx: IwadiContext = ctx.obj

    # Validate project name
    if not name.replace("_", "").isalnum():
        typer.secho(
            "Error: Project name must be alphanumeric (underscores allowed)", fg="red"
        )
        raise typer.Exit(code=1)

    # Set default base path if not provided
    if base_path is None:
        base_path = Path.home() / "iwadi_projects"

    project = Project(name=name, base_path=base_path)
    iwadi_ctx.set_project(project)
    typer.secho(f"Active project set to {name}", fg="green")

    try:
        # Create directory structure
        project.path.mkdir(parents=True, exist_ok=False)
        project.papers_path.mkdir(exist_ok=False)
        project.notes_path.mkdir(exist_ok=False)

        # Save metadata
        project.save_metadata()

        # Output results
        typer.secho(f"Created project '{name}' at: {project.path}", fg="green")
        typer.echo(f"• Papers directory: {project.papers_path}")
        typer.echo(f"• Notes directory: {project.notes_path}")

    except FileExistsError:
        typer.secho(
            f"Error: Project '{name}' already exists at {project.path}", fg="red"
        )
        raise typer.Exit(code=1)
    except PermissionError:
        typer.secho(f"Error: No permission to create project at {base_path}", fg="red")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"Error creating project: {str(e)}", fg="red")
        raise typer.Exit(code=1)
