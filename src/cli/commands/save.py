from typing import Optional, List
import click
from src.api.base_api import Paper
from src.cli.utils.interactive import prompt_paper_selection
from src.cli.utils.error_handler import api_error_handler
from src.api.arxiv_api import ArxivAPI
from src.api.ieee_api import IEEEAPI
from src.cli.context import IwadiContext
from src.storage.db import save_paper_in_db
from src.cli.project import Project
from pathlib import Path

API_MAP = {
    "arxiv": ArxivAPI(),
    "ieee": IEEEAPI(),
}


@click.command()
@click.argument("paper_ids", nargs=-1)
@click.option(
    "--project", "-p", help="Project to save to (uses active project if not specified)"
)
@click.option("--interactive", "-i", is_flag=True, help="Select papers interactively")
@click.pass_context
@api_error_handler
def save_papers(
    ctx: click.Context, paper_ids: List[str], project: Optional[str], interactive: bool
) -> None:
    """Save papers to a project."""
    iwadi_ctx: IwadiContext = ctx.obj

    if not project and not iwadi_ctx.active_project:
        click.secho(
            "No project specified and no active project set. "
            "Use --project or set an active project.",
            fg="red",
        )
        ctx.exit(1)

    target_project_name = (
        project if not iwadi_ctx.active_project else iwadi_ctx.active_project.name
    )

    assert target_project_name is not None

    papers_dir = (
        iwadi_ctx.get_papers_path()
        if not project
        else Path(f"projects/{target_project_name}/papers")
    )

    if not paper_ids and not interactive:
        click.secho("Must specify either paper IDs or use --interactive", fg="red")
        ctx.exit(1)

    available_papers = get_recent_papers()

    if interactive:
        selected_papers = prompt_paper_selection(available_papers)
    else:
        selected_papers = [p for p in available_papers if p.id in paper_ids]

    if not selected_papers:
        click.secho("No papers selected to save.", fg="yellow")
        return

    for paper in selected_papers:
        if not paper.source:
            click.secho(f"Skipping {paper.id}: No source available", fg="yellow")
            continue
        source_api = API_MAP.get(paper.source.lower())
        if not source_api:
            click.secho(
                f"Skipping {paper.id}: Unsupported source {paper.source}", fg="yellow"
            )
            continue

        try:
            source_api.download_paper(paper.id, dirpath=str(papers_dir))
            # metadata saving in DB
            pdf_path = papers_dir / f"{paper.id}.pdf"
            save_paper_in_db(
                paper,
                iwadi_ctx.active_project
                or Project(name=target_project_name, base_path=Path("projects")),
                pdf_path,
            )

            click.secho(f"✓ Saved {paper.title[:50]}...", fg="green")
        except Exception as e:
            click.secho(f"Failed to save {paper.id}: {str(e)}", fg="red")

    click.secho(
        f"\nSaved {len(selected_papers)} papers to project '{target_project_name}'",
        fg="green",
        bold=True,
    )


def get_recent_papers() -> List[Paper]:
    """Retrieve recently searched/fetched papers."""
    # TODO: Replace with actual implementation
    return [
        Paper(
            id="123",
            title="Sample Paper 1",
            authors=["Alice", "Bob"],
            source="arxiv",
            doi="10.1234/sample1",
            abstract="Sample abstract 1",
        ),
        Paper(
            id="456",
            title="Sample Paper 2",
            authors=["Charlie", "David"],
            source="ieee",
            doi="10.5678/sample2",
            abstract="Sample abstract 2",
        ),
    ]
