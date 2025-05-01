import click
from src.cli.commands import project_create, search, save, project_list
from src.cli.context import IwadiContext


@click.group()
@click.pass_context
def app(ctx: click.Context) -> None:
    """Iwadi CLI: Manage and search research papers."""
    ctx.obj = IwadiContext()


# Register subcommands
app.add_command(project_create.create, name="project-create")
app.add_command(project_list.list, name="project-list")
app.add_command(search.search, name="search")
app.add_command(save.save_papers, name="save")

if __name__ == "__main__":
    app()
