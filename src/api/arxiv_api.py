# mypy: ignore-errors
from datetime import date
from typing import List, Optional
import arxiv

from .base_api import ResearchAPI, Paper, Citation


class ArxivAPI(ResearchAPI):
    def __init__(self) -> None:
        self.client = arxiv.Client()

    def search(
        self,
        query: str,
        limit: int = 10,
        before: Optional[date] = None,
        after: Optional[date] = None,
        author: str = "",
        sort: bool = True,
    ) -> List[Paper]:
        # Construct arXiv query string with optional filters
        query_parts = [query]

        if author:
            query_parts.append(f"au:{author}")
        if before:
            query_parts.append(f"submittedDate:[* TO {before.isoformat()}]")
        if after:
            query_parts.append(f"submittedDate:[{after.isoformat()} TO *]")

        full_query = " AND ".join(query_parts)

        search = arxiv.Search(
            query=full_query,
            max_results=limit,
            sort_by=arxiv.SortCriterion.Relevance
            if sort
            else arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending,
        )

        results = []
        for result in self.client.results(search):
            paper = Paper(
                id=result.entry_id,
                title=result.title,
                authors=[a.name for a in result.authors],
                abstract=result.summary,
                published=result.published.date(),
                pdf_url=result.pdf_url,
                source="arXiv",
            )
            results.append(paper)

        return results

    def get_citation(self, paper_id: str, format: int = 0) -> Citation:
        """
        Retrieve a formatted Citation object for a given paper ID.

        Args:
            paper_id: The arXiv ID of the paper.
            format: Citation format preference (0 = MLA, 1 = APA, 2 = Chicago).

        Returns:
            A list with one Citation object.
        """
        search = arxiv.Search(id_list=[paper_id])
        paper = next(self.client.results(search))

        authors = [author.name for author in paper.authors]
        year = paper.published.year
        title = paper.title
        url = paper.entry_id

        # Format the citation string based on format choice
        if format == 0:  # MLA
            citation_format = "MLA"
            author_str = ", ".join(authors)
            citation_str = f'{author_str}. "{title}." arXiv, {year}, {url}.'
        elif format == 1:  # APA
            citation_format = "APA"
            author_str = ", ".join(authors)
            citation_str = f"{author_str} ({year}). {title}. arXiv. {url}"
        elif format == 2:  # Chicago
            citation_format = "Chicago"
            author_str = ", ".join(authors)
            citation_str = f'{author_str}. "{title}." arXiv ({year}). {url}.'
        else:
            citation_format = "Unknown"
            citation_str = f"{', '.join(authors)}. {title} ({year}). {url}"

        citation = Citation(
            id=paper.entry_id,
            title=paper.title,
            citation_format=citation_format,
            citation_str=citation_str,
            authors=authors,
            year=year,
            source="arXiv",
            url=url,
        )

        return citation

    def download_paper(self, paper_id: str, dirpath: str = ".") -> None:
        """
        Download the PDF of a paper given its arXiv ID.

        Args:
            paper_id: The arXiv ID of the paper.
            dirpath: Directory path to download the paper into (default current directory).
            filename: Custom filename (optional).
        """
        search = arxiv.Search(id_list=[paper_id])
        paper = next(self.client.results(search))
        paper.download_pdf(dirpath=dirpath, filename=paper.title)
