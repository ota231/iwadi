import typer
from .commands import project_create, search, save, project_list
from .context import IwadiContext

# Initialize the main app with context
app = typer.Typer(
    help="Iwadi CLI: A command-line interface for managing and searching research papers."
)
shared_context = IwadiContext()

app.add_typer(search.app, name="search", help="Search for research papers")
app.add_typer(save.app, name="save", help="Save papers to projects")

# Project management commands
project_app = typer.Typer(help="Project management commands")
project_app.command("create")(project_create.create)
project_app.command("list")(project_list.list)
app.add_typer(project_app, name="project")


@app.callback()
def main(ctx: typer.Context) -> None:
    """Inject our context into Typer's context"""
    ctx.obj = shared_context


if __name__ == "__main__":
    app()
