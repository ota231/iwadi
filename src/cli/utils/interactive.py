from typing import List, Optional
import typer
from src.api.base_api import Paper


def prompt_paper_selection(papers: List[Paper]) -> Optional[List[Paper]]:
    """Interactive paper selection prompt."""
    if not papers:
        typer.secho("No papers found to select.", fg="red")
        return None

    # Display papers with numbering
    for idx, paper in enumerate(papers, start=1):
        typer.echo(
            f"{idx}. {typer.style(paper.title, bold=True)}\n"
            f"   Authors: {', '.join(paper.authors[:3])}"
            f"{'...' if len(paper.authors) > 3 else ''}\n"
            f"   Year: {paper.publication_date.year if paper.publication_date else 'N/A'}"
        )

    # Prompt with validation
    while True:
        selected = typer.prompt(
            "Select papers to save (comma-separated numbers or 'all')", default="all"
        )

        if selected.lower() == "all":
            return papers

        try:
            indices = [int(i.strip()) for i in selected.split(",")]
            if all(1 <= i <= len(papers) for i in indices):
                return [papers[i - 1] for i in indices]
        except ValueError:
            pass

        typer.secho("Invalid selection. Please try again.", fg="red")
