from .base_api import ResearchAPI, Paper, Citation
from xploreapi import Xplore
from typing import List, Optional, Union
from datetime import date
import os
from dotenv import load_dotenv


class IEEEAPI(ResearchAPI):
    def __init__(self) -> None:
        load_dotenv()
        self.api_key = os.getenv("IEEE_API_KEY")
        self.query = Xplore(self.api_key)

    def search(
        self,
        query: str,
        limit: int,
        before: Optional[date],
        after: Optional[date],
        author: str,
        sort: bool,
    ) -> List[Paper]:
        # Building the search query based on the provided parameters
        search_query = self.query.queryText(query)

        if before:
            search_query.insertionEndDate(
                before.strftime("%Y%m%d")
            )  # Date in YYYYMMDD format
        if after:
            search_query.insertionStartDate(
                after.strftime("%Y%m%d")
            )  # Date in YYYYMMDD format
        if author:
            search_query.authorText(author)
        if sort:
            search_query.resultsSorting(
                "publicationYear", "desc"
            )  # Sort by publication year (descending)

        search_query.startingResult(0)
        search_query.maximumResults(limit)

        # Make the API call with the built query
        data = search_query.callAPI()

        # Parsing the response and returning the results as a list of Paper objects
        papers = []
        for item in data["records"]:
            paper = Paper(
                id=item["article_number"],
                title=item["title"],
                authors=item["authors"],
                abstract=item["abstract"],
                pdf_url=item.get("pdf_url", None),
                publication_date=item.get("publication_date", None),
                source=item.get("source", None),
                doi=item.get("doi", None),
                citation_count=item.get("citation_count", 0),
            )
            papers.append(paper)

        return papers

    def download_paper(self, paper_id: str) -> Optional[Paper]:
        # Create the query for downloading the paper using its ID
        search_query = self.query.articleNumber(paper_id)

        # Make the API call with the built query
        data = search_query.callAPI()

        if not data or "records" not in data:
            return None  # If no records found, return None

        item = data["records"][0]

        # Create and return a Paper object
        paper = Paper(
            id=item["article_number"],
            title=item["title"],
            authors=item["authors"],
            abstract=item["abstract"],
            pdf_url=item.get("pdf_url", None),
            publication_date=item.get("publication_date", None),
            source=item.get("source", None),
            doi=item.get("doi", None),
            citation_count=item.get("citation_count", 0),
        )

        return paper

    def get_citation(self, paper_id: str, format: int) -> Union[Citation, None]:
        # Create the query for retrieving citations based on paper_id and format
        search_query = self.query.citations(paper_id, format)

        # Make the API call with the built query
        data = search_query.callAPI()

        if not data or "citations" not in data:
            return None  # If no citations found, return None

        citation_data = data["citations"][
            0
        ]  # Assuming the first citation is the required one

        # Create and return a Citation object
        citation = Citation(
            id=citation_data["citation_id"],
            title=citation_data["title"],
            citation_format=citation_data["citation_format"],
            citation_str=citation_data["citation_str"],
            authors=citation_data["authors"],
            year=citation_data.get("year", None),
            source=citation_data.get("source", None),
            url=citation_data.get("url", None),
        )

        return citation
