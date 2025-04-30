from typing import Optional, List
import typer
from src.api.base_api import Paper
from src.cli.utils.interactive import prompt_paper_selection
from src.cli.utils.error_handler import api_error_handler
from src.cli.utils.completion import complete_projects
from src.api.arxiv_api import ArxivAPI
from src.api.ieee_api import IEEEAPI
from src.cli.context import IwadiContext
from pathlib import Path

app = typer.Typer()

API_MAP = {
    "arxiv": ArxivAPI(),
    "ieee": IEEEAPI(),
}


@app.command()
@api_error_handler
def papers(
    paper_ids: Optional[List[str]] = typer.Argument(
        None,
        help="Paper IDs to save",
        autocompletion=lambda: [p.id for p in get_recent_papers()],
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        "-p",
        help="Project to save to (uses active project if not specified)",
        autocompletion=complete_projects,
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Select papers interactively"
    ),
    ctx: Optional[typer.Context] = None,
) -> None:
    """Save papers to a research project."""
    assert ctx is not None
    iwadi_ctx: IwadiContext = ctx.obj

    # Validate we have either an active project or a specified project
    if not project and not iwadi_ctx.active_project:
        typer.secho(
            "No project specified and no active project set. "
            "Use --project or set an active project.",
            fg="red",
        )
        raise typer.Exit(1)

    target_project_name = (
        project if not iwadi_ctx.active_project else iwadi_ctx.active_project.name
    )

    papers_dir = (
        iwadi_ctx.get_papers_path()
        if not project
        else Path(f"projects/{target_project_name}/papers")
    )

    if not paper_ids and not interactive:
        typer.secho("Must specify either paper IDs or --interactive", fg="red")
        raise typer.Exit(1)

    available_papers = get_recent_papers()

    if interactive:
        selected_papers = prompt_paper_selection(available_papers)
    else:
        selected_papers = [p for p in available_papers if p.id in (paper_ids or [])]

    if not selected_papers:
        typer.secho("No papers selected to save.", fg="yellow")
        return

    for paper in selected_papers:
        if not paper.source:
            typer.secho(f"Skipping {paper.id}: No source available", fg="yellow")
            continue
        source_api = API_MAP.get(paper.source.lower())
        if not source_api:
            typer.secho(
                f"Skipping {paper.id}: Unsupported source {paper.source}", fg="yellow"
            )
            continue

        try:
            source_api.download_paper(paper.id, dirpath=str(papers_dir))
            typer.secho(f"✓ Saved {paper.title[:50]}...", fg="green")

        except Exception as e:
            typer.secho(f"Failed to save {paper.id}: {str(e)}", fg="red")

    typer.secho(
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


def save_papers(papers: List[Paper], project_name: str, ctx: IwadiContext) -> None:
    """Download paper PDFs using context for path resolution"""
    try:
        papers_dir = ctx.get_papers_path()

        for paper in papers:
            source_api = API_MAP.get(paper.source.lower()) if paper.source else None
            if not source_api:
                typer.secho(f"Unsupported source: {paper.source}", fg="red")
                continue

            try:
                source_api.download_paper(paper.id, dirpath=str(papers_dir))
                typer.secho(
                    f"Saved: {paper.title} to project {project_name} in {str(papers_dir)}",
                    fg="cyan",
                )

            except Exception as e:
                typer.secho(f"Failed to download {paper.id}: {str(e)}", fg="red")

    except ValueError as e:
        typer.secho(f"Error: {str(e)}", fg="red")
        raise typer.Exit(1)
    # TODO: metadata saving, in DB
