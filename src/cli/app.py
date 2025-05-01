import click
from src.cli.commands import create_project, list_projects, search, save
from src.cli.context import IwadiContext


# TODO: Add logging
@click.group()
@click.pass_context
def app(ctx: click.Context) -> None:
    """Iwadi CLI: Manage and search research papers."""
    ctx.obj = IwadiContext()


# Register subcommands
app.add_command(create_project.create, name="create-project")
app.add_command(list_projects.list, name="list-projects")
app.add_command(search.search, name="search")
app.add_command(save.save_papers, name="save")

if __name__ == "__main__":
    app()
