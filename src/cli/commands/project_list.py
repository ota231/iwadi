from pathlib import Path
import typer

app = typer.Typer()


@app.command()
def list() -> None:
    """List all research projects"""
    base_path = Path.home() / "iwadi_projects"
    if not base_path.exists():
        typer.echo("No projects found")
        return

    typer.echo("Your research projects:")
    for project in sorted(base_path.iterdir()):
        if project.is_dir():
            typer.echo(f"• {project.name}")
