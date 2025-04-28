from dataclasses import dataclass
from typing import List, Optional
from datetime import date
from abc import ABC, abstractmethod


@dataclass
class Paper:
    id: str
    title: str
    authors: List[str]
    abstract: str
    pdf_url: Optional[str]
    publication_date: Optional[date]
    source: Optional[str]
    doi: Optional[str]
    citation_count: Optional[int] = 0


@dataclass
class Citation:
    id: str
    title: str
    authors: List[str]
    year: Optional[int] = None
    venue: Optional[str] = None
    url: Optional[str] = None


class ResearchAPI(ABC):
    @abstractmethod
    def search(
        self,
        query: str,
        limit: int,
        before: date,
        after: date,
        author: str,
        sort: bool,
    ) -> List[Paper]:
        """Search for papers given a query string."""
        pass

    @abstractmethod
    def download_paper(self, paper_id: str) -> Optional[Paper]:
        """
        Download a paper given its ID.
        
        Args:
            paper_id: ID of the paper to download.

        Returns:
            A Paper object with the downloaded content.
        """
        pass

    @abstractmethod
    def get_citations(self, paper_id: str, format: int) -> List[str]:
        """
        Retrieve a list of citations for a given paper.
        
        Args:
            paper_id: ID of the paper to retrieve citations for.
            format: Citation format preference (e.g., 0 = minimal, 1 = full).

        Returns:
            A list of Citation objects.
        """
        pass
