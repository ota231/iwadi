from typing import List, Literal, Optional
from tabulate import tabulate
import click
from src.api.base_api import Paper

DisplayFormat = Literal["table", "json", "minimal"]


def display_papers(papers: List[Paper], format: DisplayFormat = "table") -> None:
    """
    Display papers in the specified format

    Args:
        papers: List of Paper objects to display
        format: Output format (table|json|minimal)
    """
    if not papers:
        click.secho("No papers to display", fg="yellow")
        return

    if format == "json":
        _display_json(papers)
    elif format == "minimal":
        _display_minimal(papers)
    else:
        _display_table(papers)


def validate_format(format_str: str) -> DisplayFormat:
    """Convert and validate display format"""
    if format_str.lower() in ("table", "json", "minimal"):
        return format_str.lower()  # type: ignore
    raise ValueError(f"Invalid format: {format_str}")


def _display_table(papers: List[Paper]) -> None:
    """Display papers in a formatted table"""
    headers = ["#", "Title", "Authors", "Year", "Source", "Citations"]
    rows = []

    for idx, paper in enumerate(papers, 1):
        authors = ", ".join(paper.authors[:2])
        if len(paper.authors) > 2:
            authors += " et al."

        year = paper.publication_date.year if paper.publication_date else "N/A"

        rows.append(
            [
                idx,
                click.style(
                    paper.title[:60] + ("..." if len(paper.title) > 60 else ""),
                    bold=True,
                ),
                authors,
                year,
                paper.source or "Unknown",
                paper.citation_count or 0,
            ]
        )

    click.echo(tabulate(rows, headers=headers, tablefmt="grid"))


def _display_minimal(papers: List[Paper]) -> None:
    """Display minimal compact output"""
    for idx, paper in enumerate(papers, 1):
        authors = ", ".join(a.split()[0] for a in paper.authors[:2])
        year = paper.publication_date.year if paper.publication_date else "N/A"
        click.echo(
            f"{idx}. {click.style(paper.title[:80], bold=True)} ({authors}, {year})"
        )


def _display_json(papers: List[Paper]) -> None:
    """Display papers as JSON output"""
    import json

    output = [
        {
            "id": paper.id,
            "title": paper.title,
            "authors": paper.authors,
            "year": paper.publication_date.year if paper.publication_date else None,
            "source": paper.source,
            "citations": paper.citation_count,
            "url": paper.pdf_url or f"https://doi.org/{paper.doi}"
            if paper.doi
            else None,
        }
        for paper in papers
    ]
    click.echo(json.dumps(output, indent=2))


def display_error(message: str, details: Optional[str] = None) -> None:
    """Display error message with consistent formatting"""
    click.secho("\nError: ", fg="red", nl=False, bold=True)
    click.echo(message)
    if details:
        click.secho("Details: ", fg="yellow", nl=False)
        click.echo(details)
    click.echo("")
