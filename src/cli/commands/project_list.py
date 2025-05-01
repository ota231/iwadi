from pathlib import Path
import click


@click.command()
def list() -> None:
    """List all research projects"""
    base_path = Path.home() / "iwadi_projects"
    if not base_path.exists() or not any(base_path.iterdir()):
        click.secho("No projects found", fg="yellow")
        return

    click.secho("Your research projects:", fg="cyan", bold=True)
    for project in sorted(base_path.iterdir()):
        if project.is_dir():
            click.echo(f"• {project.name}")
