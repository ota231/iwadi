from dataclasses import dataclass
from typing import List, Optional, Union
from datetime import date
from abc import ABC, abstractmethod


@dataclass
class Paper:
    id: str
    title: str
    authors: List[str]
    abstract: str
    pdf_url: Optional[str] = None
    publication_date: Optional[date] = None
    source: Optional[str] = None
    doi: Optional[str] = None
    citation_count: Optional[int] = 0


@dataclass
class Citation:
    id: str
    title: str
    citation_format: str
    citation_str: str
    authors: List[str]
    year: Optional[int] = None
    source: Optional[str] = None
    url: Optional[str] = None


class ResearchAPI(ABC):
    @abstractmethod
    def search(
        self,
        query: str,
        limit: int,
        before: Optional[date],
        after: Optional[date],
        author: str,
        sort: bool,
    ) -> List[Paper]:
        """Search for papers given a query string."""
        pass

    @abstractmethod
    def download_paper(
        self, paper_id: str, dirpath: str = ".", filename: Optional[str] = None
    ) -> None:
        """
        Download a paper given its ID.

        Args:
            paper_id: ID of the paper to download.
            dirpath: Directory path to save the downloaded paper.

        Returns:
            A Paper object with the downloaded content.
        """
        pass

    @abstractmethod
    def get_citation(self, paper_id: str, format: int) -> Union[Citation, None]:
        """
        Retrieve a list of citations for a given paper.

        Args:
            paper_id: ID of the paper to retrieve citations for.
            format: Citation format preference (e.g., 0 = minimal, 1 = full).

        Returns:
            A list of Citation objects.
        """
        pass
