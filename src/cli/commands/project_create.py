from pathlib import Path
from typing import Optional
import typer
from src.cli.utils.error_handler import api_error_handler
from datetime import datetime
import json

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
) -> None:
    """
    Create a new research project with organized directory structure.

    Example:
    iwadi project create quantum_ml
    """
    # Validate project name
    if not name.replace("_", "").isalnum():
        typer.secho(
            "Error: Project name must be alphanumeric (underscores allowed)", fg="red"
        )
        raise typer.Exit(code=1)

    # Set default base path if not provided
    if base_path is None:
        base_path = Path.home() / "iwadi_projects"

    project_path = base_path / name
    papers_path = project_path / "papers"
    notes_path = project_path / "notes"

    try:
        # Create directory structure
        papers_path.mkdir(parents=True, exist_ok=False)
        notes_path.mkdir(exist_ok=False)

        # Create basic metadata file
        metadata = {
            "project_name": name,
            "created": datetime.now().isoformat(),
            "papers": [],
        }
        (project_path / "project_meta.json").write_text(json.dumps(metadata, indent=2))

        typer.secho(f"Created project '{name}' at: {project_path}", fg="green")
        typer.echo(f"• Papers directory: {papers_path}")
        typer.echo(f"• Notes directory: {notes_path}")

    except FileExistsError:
        typer.secho(
            f"Error: Project '{name}' already exists at {project_path}", fg="red"
        )
        raise typer.Exit(code=1)
    except PermissionError:
        typer.secho(f"Error: No permission to create project at {base_path}", fg="red")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"Error creating project: {str(e)}", fg="red")
        raise typer.Exit(code=1)
