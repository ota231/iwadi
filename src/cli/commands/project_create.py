import click
from pathlib import Path
from typing import Optional
from src.cli.utils.error_handler import api_error_handler
from src.cli.project import Project
from src.cli.context import IwadiContext


@click.command()
@click.argument("name")
@click.option(
    "--path",
    "-p",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
    help="Custom parent directory (default: ~/iwadi_projects)",
)
@click.pass_context
@api_error_handler
def create(ctx: click.Context, name: str, path: Optional[str]) -> None:
    """
    Create a new research project.
    """
    iwadi_ctx: IwadiContext = ctx.obj

    if not name.replace("_", "").isalnum():
        click.secho(
            "Error: Project name must be alphanumeric (underscores allowed)", fg="red"
        )
        raise click.Abort()

    base_path = Path(path) if path else Path.home() / "iwadi_projects"
    project = Project(name=name, base_path=base_path)
    iwadi_ctx.set_project(project)

    click.secho(f"Active project set to {name}", fg="green")

    try:
        project.path.mkdir(parents=True, exist_ok=False)
        project.papers_path.mkdir(exist_ok=False)
        project.notes_path.mkdir(exist_ok=False)
        project.save_metadata()

        click.secho(f"Created project '{name}' at: {project.path}", fg="green")
        click.echo(f"• Papers directory: {project.papers_path}")
        click.echo(f"• Notes directory: {project.notes_path}")

    except FileExistsError:
        click.secho(
            f"Error: Project '{name}' already exists at {project.path}", fg="red"
        )
        raise click.Abort()
    except PermissionError:
        click.secho(f"Error: No permission to create project at {base_path}", fg="red")
        raise click.Abort()
    except Exception as e:
        click.secho(f"Error creating project: {str(e)}", fg="red")
        raise click.Abort()
