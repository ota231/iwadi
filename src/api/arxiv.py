import arxiv
from arxiv import Search, Client, SortCriterion

from datetime import date
from typing import List
import arxiv

from .base import ResearchAPI, Paper, Citation

class ArxivAPI(ResearchAPI):
    def __init__(self):
        self.client = Client()


    def search(
        self,
        query: str,
        limit: int = 10,
        before: date = None,
        after: date = None,
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
            sort_by=arxiv.SortCriterion.Relevance if sort else arxiv.SortCriterion.SubmittedDate,
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
                source="arXiv"
            )
            results.append(paper)

        return results

    def get_citations(self, paper_id: str, format: int = 0) -> List[str]:
        """
        Retrieve a formatted citation for a given paper ID.

        Args:
            paper_id: The arXiv ID of the paper.
            format: Citation style (0 = MLA, 1 = APA, 2 = Chicago)

        Returns:
            A list with one formatted citation string.
        """
        search = Search(id_list=[paper_id])
        paper = next(self.client.results(search))

        authors = ", ".join([author.name for author in paper.authors])
        title = paper.title
        year = paper.published.year
        url = paper.entry_id

        if format == 0:  # MLA
            citation = f'{authors}. "{title}." *arXiv*, {year}, {url}.'
        elif format == 1:  # APA
            citation = f'{authors} ({year}). {title}. *arXiv*. {url}'
        elif format == 2:  # Chicago
            citation = f'{authors}. "{title}." *arXiv*, {year}. {url}.'
        else:
            citation = f"{paper_id} (Unknown citation format requested)"

        return [citation]

        
    def download_paper(self, paper_id: str, dirpath: str = ".", filename: str = None) -> None:
        """
        Download the PDF of a paper given its arXiv ID.
        
        Args:
            paper_id: The arXiv ID of the paper.
            dirpath: Directory path to download the paper into (default current directory).
            filename: Custom filename (optional).
        """
        search = Search(id_list=[paper_id])
        paper = next(self.client.results(search))
        paper.download_pdf(dirpath=dirpath, filename=filename)