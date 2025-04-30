from typing import Optional, List
from pathlib import Path
import typer
from src.api.base_api import Paper
from src.cli.utils.interactive import prompt_paper_selection
from src.cli.utils.error_handler import api_error_handler
from src.cli.utils.completion import complete_projects

app = typer.Typer()


@app.command()
@api_error_handler
def papers(
    paper_ids: Optional[List[str]] = typer.Argument(
        None,
        help="Paper IDs to save",
        autocompletion=lambda: [],  # Could implement paper ID completion
    ),
    project: str = typer.Option(
        ...,
        "--project",
        "-p",
        help="Project to save to",
        autocompletion=complete_projects,
    ),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Select papers interactively"
    ),
    output_dir: Path = typer.Option(
        Path("projects"), "--output", "-o", help="Projects directory"
    ),
) -> None:
    """Save papers to a research project."""
    if not paper_ids and not interactive:
        typer.secho("Must specify either paper IDs or --interactive", fg="red")
        raise typer.Exit(1)

    # Get papers from your storage system
    all_papers = get_recent_papers()  # Implement this function

    if interactive:
        selected_papers = prompt_paper_selection(all_papers)
    else:
        paper_id_list = paper_ids or []
        selected_papers = [p for p in all_papers if p.id in paper_id_list]

    if not selected_papers:
        typer.secho("No papers selected to save.", fg="yellow")
        return

    # Save implementation
    project_path = output_dir / project
    project_path.mkdir(exist_ok=True)

    save_papers(selected_papers, project_path)  # Implement this function

    typer.secho(
        f"Saved {len(selected_papers)} papers to project '{project}'", fg="green"
    )


def get_recent_papers() -> List[Paper]:
    """Retrieve recently searched/fetched papers."""
    # TODO: Implement based on your storage system
    # This is a placeholder implementation
    paper_1 = Paper(
        id="123",
        title="Sample Paper 1",
        authors=["Alice", "Bob"],
        source="arxiv",
        doi="10.1234/sample1",
        abstract="An abstract of sample paper 1.",
    )
    paper_2 = Paper(
        id="456",
        title="Sample Paper 2",
        authors=["Charlie", "David"],
        source="ieee",
        doi="10.5678/sample2",
        abstract="An abstract of sample paper 2.",
    )
    return [paper_1, paper_2]


def save_papers(papers: List[Paper], project_path: Path) -> None:
    """Save individual paper to project directory."""
    # TODO: Implement saving logic (PDFs, metadata, etc.)
    pass
