import click
import subprocess
from src.cli.context import IwadiContext


@click.command()
@click.pass_context
def view(ctx: click.Context) -> None:
    """Launches Datasette for viewing papers metadata in the current project."""

    # Get the active project from the context
    iwadi_ctx: IwadiContext = ctx.obj
    active_project = iwadi_ctx.active_project

    if not active_project:
        click.secho(
            "No active project set. Please create or set a project first.", fg="red"
        )
        ctx.exit(1)

    # Path to the metadata.db (Assumes 'metadata.db' is in the project base directory)
    metadata_db_path = active_project.path / "metadata.db"

    if not metadata_db_path.exists():
        click.secho(
            f"Error: No 'metadata.db' found in the active project directory ({metadata_db_path})",
            fg="red",
        )
        ctx.exit(1)

    # Launch Datasette to view the database
    click.secho(f"Launching Datasette for project: {active_project.name}", fg="green")
    subprocess.run(["datasette", str(metadata_db_path)], check=True)
