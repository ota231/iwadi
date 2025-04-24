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
    pdf_url: str
    publication_date: date
    source: str
    doi: str
    citation_count: int
    
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
    def search(self, query: str, limit: int, before: date, after: date, author: str, source: str, sort: bool) -> List[Paper]:
        """Search for papers given a query string."""
        ...

    @abstractmethod
    def get_citations(self, paper_id: str, format: int) -> List[str]:
        """Retrieve a list of paper IDs that cite the given paper."""
        ...
