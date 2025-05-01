import click
from datetime import date
from typing import Optional, List, Union, cast

from src.api.arxiv_api import ArxivAPI
from src.api.ieee_api import IEEEAPI
from src.api.base_api import ResearchAPI, Paper, SortBy, SortOrder
from src.cli.utils.display import display_papers, display_error, validate_format
from src.cli.utils.interactive import prompt_paper_selection
from src.cli.utils.error_handler import api_error_handler
from src.cli.commands.save import save_papers
from src.cli.context import IwadiContext

API_MAP = {
    "arxiv": ArxivAPI(),
    "ieee": IEEEAPI(),
}


def get_api(source: str) -> Optional[Union[ResearchAPI, None]]:
    """Factory method for API instances with proper typing"""
    return API_MAP.get(source.lower()) if source else None


@click.command(help="Search research papers across multiple sources")
@click.argument("search", required=True)
@click.option("--author", "-a", help="Filter by author name")
@click.option("--after", type=int, help="Year after (inclusive)")
@click.option("--before", type=int, help="Year before (inclusive)")
@click.option(
    "--source",
    "-s",
    "sources",
    multiple=True,
    default=["arxiv", "ieee"],
    help="Sources to search",
)
@click.option(
    "--sort",
    "sort_by",
    default="relevance",
    help="Sort method (relevance, author, last_updated_date, submitted_date)",
    show_default=True,
)
@click.option(
    "--order",
    "sort_order",
    default="descending",
    help="Sort order (ascending, descending)",
    show_default=True,
)
@click.option(
    "--limit",
    "-l",
    default=10,
    type=click.IntRange(1, 100),
    help="Maximum results per source",
    show_default=True,
)
@click.option("--save", "-S", is_flag=True, help="Prompt to save results after display")
@click.option(
    "--format",
    "-f",
    "output_format",
    default="table",
    help="Output format (table, json, etc.)",
    show_default=True,
)
@click.pass_context
@api_error_handler
def search(
    ctx: click.Context,
    search: str,
    author: Optional[str],
    after: Optional[int],
    before: Optional[int],
    sources: List[str],
    sort_by: str,
    sort_order: str,
    limit: int,
    save: bool,
    output_format: str,
) -> None:
    """
    Search research papers across multiple sources.

    Examples:

        iwadi search "quantum computing" --author "Preskill" --after 2018
        iwadi search "neural networks" --source arxiv --source ieee --limit 5
    """

    iwadi_ctx: IwadiContext = ctx.obj

    if not search.strip():
        display_error("Search query cannot be empty")
        raise click.Abort()

    if sort_by.lower() not in [
        "relevance",
        "author",
        "last_updated_date",
        "submitted_date",
    ]:
        display_error(
            "Invalid sort method. Choose from: relevance, author, last_updated_date, submitted_date"
        )
        raise click.Abort()

    if sort_order.lower() not in ["ascending", "descending"]:
        display_error("Invalid sort order. Choose from: ascending, descending")
        raise click.Abort()

    sort_by_lit = cast(SortBy, sort_by.lower())
    sort_order_lit = cast(SortOrder, sort_order.lower())

    after_date = date(after, 1, 1) if after else None
    before_date = date(before, 12, 31) if before else None

    all_results: List[Paper] = []

    for source in sources:
        api = get_api(source)
        if not api:
            display_error(
                f"Unknown source: {source}. Valid sources: {', '.join(API_MAP.keys())}"
            )
            continue

        try:
            results = api.search(
                query=search,
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

    if not all_results:
        display_error("No results found across all sources")
        raise click.Abort()

    try:
        fmt = validate_format(output_format)
        display_papers(all_results, format=fmt)
    except ValueError as e:
        display_error(str(e))
        raise click.Abort()

    if save or click.confirm("\nWould you like to save any papers?"):
        selected = prompt_paper_selection(all_results)
        if selected:
            project = click.prompt("Enter project name to save to")
            save_papers(selected, project_name=project, ctx=iwadi_ctx)
            click.secho(
                f"Saved {len(selected)} papers to project '{project}'", fg="green"
            )
