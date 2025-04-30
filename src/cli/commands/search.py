from datetime import date
from typing import Optional, List, Union, Dict, cast
import typer
from src.api.arxiv_api import ArxivAPI
from src.api.ieee_api import IEEEAPI
from src.api.base_api import Paper, SortBy, SortOrder
from src.cli.utils.display import display_papers, display_error, validate_format
from src.cli.utils.interactive import prompt_paper_selection
from src.cli.utils.error_handler import api_error_handler
from src.cli.commands.save import save_papers

app = typer.Typer(help="Search research papers across multiple sources")


def get_api(source: str) -> Optional[Union[ArxivAPI, IEEEAPI]]:
    """Factory method for API instances with proper typing"""
    apis: Dict[str, Union[ArxivAPI, IEEEAPI]] = {"arxiv": ArxivAPI(), "ieee": IEEEAPI()}
    return apis.get(source.lower())


@app.command()
@api_error_handler
def query(
    query: str = typer.Argument(..., help="Search terms"),
    author: Optional[str] = typer.Option(
        None, "--author", "-a", help="Filter by author name"
    ),
    after: Optional[int] = typer.Option(None, help="Year after (inclusive)"),
    before: Optional[int] = typer.Option(None, help="Year before (inclusive)"),
    sources: List[str] = typer.Option(
        ["arxiv", "ieee"],
        "--source",
        "-s",
        help="Sources to search",
        autocompletion=lambda: ["arxiv", "ieee"],
    ),
    sort_by: str = typer.Option(
        "relevance", "--sort", help="Sort method", case_sensitive=False
    ),
    sort_order: str = typer.Option(
        "descending", "--order", help="Sort order", case_sensitive=False
    ),
    limit: int = typer.Option(
        10, "--limit", "-l", help="Maximum results per source", min=1, max=100
    ),
    save: bool = typer.Option(
        False, "--save", "-S", help="Prompt to save results after display"
    ),
    output_format: str = typer.Option(
        "table", "--format", "-f", help="Output format", case_sensitive=False
    ),
) -> None:
    """
    Search research papers across multiple sources

    Examples:

    iwadi search "quantum computing" --author "Preskill" --after 2018
    iwadi search "neural networks" --source arxiv --source ieee --limit 5
    """
    # Validate inputs
    if not query.strip():
        display_error("Search query cannot be empty")
        raise typer.Exit(code=1)

    if sort_by.lower() not in ["relevance", "author", "last_updatted_date", "submitted_date"]:
        display_error("Invalid sort method. Choose from: relevance, author, last_updatted_date, submitted_date")
        raise typer.Exit(code=1)
    
    if sort_order.lower() not in ["ascending", "descending"]:
        display_error("Invalid sort order. Choose from: ascending, descending")
        raise typer.Exit(code=1)
    
    # cast to literals
    sort_by_lit = cast(SortBy, sort_by.lower())
    sort_order_lit = cast(SortOrder, sort_order.lower())

    # Convert years to dates
    after_date = date(after, 1, 1) if after else None
    before_date = date(before, 12, 31) if before else None

    # Execute searches
    all_results: List[Paper] = []
    for source in sources:
        api = get_api(source)
        if not api:
            display_error(f"Unknown source: {source}")
            continue

        try:
            results = api.search(
                query=query,
                author=author,
                after=after_date,
                before=before_date,
                sort_by=sort_by_lit,
                sort_order=sort_order_lit,
                limit=limit,
            )
            all_results.extend(results)
        except Exception as e:
            display_error(f"Error searching {source}: {str(e)}")
            continue

    # Display results
    if not all_results:
        display_error("No results found across all sources")
        raise typer.Exit(code=1)

    try:
        fmt = validate_format(output_format)
        display_papers(all_results, format=fmt)
    except ValueError as e:
        display_error(str(e))
        raise typer.Exit(1)

    # Handle saving
    if save or typer.confirm("\nWould you like to save any papers?"):
        selected = prompt_paper_selection(all_results)
        if selected:
            project = typer.prompt("Enter project name to save to")
            save_papers(
                selected, project_path=project
            )  # TODO: Get proper project path name
            typer.secho(
                f"Saved {len(selected)} papers to project '{project}'", fg="green"
            )


if __name__ == "__main__":
    app()
