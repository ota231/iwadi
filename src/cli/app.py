import typer
from .commands import project_create, search, save, project_list

app = typer.Typer(
    help="Iwadi CLI: A command-line interface for managing and searching research papers."
)
app.add_typer(search.app, name="search")
app.add_typer(project_create.app, name="project")
app.add_typer(save.app, name="save")
app.add_typer(project_create.app, name="project-create")  # Hidden from help
app.add_typer(project_list.app, name="project-list")

project_app = typer.Typer()
project_app.command("create")(project_create.create)
project_app.command("list")(project_list.list)
app.add_typer(project_app, name="project", help="Project management commands")

if __name__ == "__main__":
    app()
