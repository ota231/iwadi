from .base_api import ResearchAPI, Paper, Citation
from .xploreapi import Xplore
from typing import List, Optional, Dict, Any
from datetime import date
import os
from dotenv import load_dotenv
from requests.exceptions import RequestException
import requests


from .base_api_error import (
    APIRequestError,
    APIResponseError,
    APIAuthError,
    APIErrorDetail,
)


class IEEEAPI(ResearchAPI):
    def __init__(self) -> None:
        load_dotenv()
        self.api_key = os.getenv("IEEE_API_KEY")
        if not self.api_key:
            raise APIAuthError(
                message="IEEE API key not found in environment variables",
                source="ieee",
                details=APIErrorDetail(code="ieee:missing_api_key", retryable=False),
            )
        self.query = Xplore(self.api_key)

    def _handle_ieee_error(self, error_data: Dict[str, Any]) -> None:
        """Map IEEE API error responses to appropriate exception types"""
        if "error" in error_data:
            error_msg = error_data["error"]

            if "Authorization token not provided" in error_msg:
                raise APIAuthError(
                    message=error_msg,
                    source="ieee",
                    details=APIErrorDetail(code="ieee:auth_required", retryable=False),
                )
            elif any(
                msg in error_msg
                for msg in ["Service Not Found", "Internal Server Error"]
            ):
                raise APIRequestError(
                    message=error_msg,
                    status_code=500,
                    source="ieee",
                    details=APIErrorDetail(code="ieee:server_error", retryable=True),
                )
            else:
                raise APIResponseError(
                    message=error_msg,
                    source="ieee",
                    details=APIErrorDetail(
                        code="ieee:invalid_request",
                        retryable=False,
                        metadata={"raw_error": error_data},
                    ),
                )

    def search(
        self,
        query: str,
        limit: int = 10,
        before: Optional[date] = None,
        after: Optional[date] = None,
        author: str = "",
        sort: bool = True,
    ) -> List[Paper]:
        """Search IEEE Xplore for papers matching criteria.

        Args:
            query: Search terms
            limit: Maximum results (default 10)
            before: Return papers before this date
            after: Return papers after this date
            author: Filter by author name
            sort: Sort by relevance (True) or date (False)

        Returns:
            List of Paper objects

        Raises:
            APIResponseError: For invalid queries or empty results
            APIRequestError: For network/retryable errors
            APIAuthError: For authorization issues
        """
        # Validate query parameters
        if not query.strip():
            raise APIResponseError(
                message="Empty search query",
                source="ieee",
                details=APIErrorDetail(code="ieee:empty_query", retryable=False),
            )

        if "*" in query:
            if query.count("*") > 2:
                raise APIResponseError(
                    message="Maximum 2 wildcards allowed",
                    source="ieee",
                    details=APIErrorDetail(
                        code="ieee:too_many_wildcards",
                        retryable=False,
                        metadata={"query": query},
                    ),
                )
            if any(len(term) < 3 for term in query.split("*")[:-1]):
                raise APIResponseError(
                    message="Wildcard terms need ≥3 characters",
                    source="ieee",
                    details=APIErrorDetail(
                        code="ieee:invalid_wildcard", retryable=False
                    ),
                )

        try:
            # Build search query
            search_query = self.query.queryText(query)

            # Date filters
            if before:
                search_query.insertionEndDate(before.strftime("%Y%m%d"))
            if after:
                search_query.insertionStartDate(after.strftime("%Y%m%d"))

            # Author filter
            if author:
                search_query.authorText(author)

            # Sorting
            search_query.resultsSorting(
                "publicationYear" if not sort else "relevance", "desc"
            )

            # Result limits
            search_query.startingResult(0)
            search_query.maximumResults(min(limit, 100))  # IEEE max is 100

            # Execute search
            response = search_query.callAPI()

            # Handle API errors
            if "error" in response:
                self._handle_ieee_error(response)

            # Check for empty results
            if not response.get("records"):
                raise APIResponseError(
                    message="No results found",
                    source="ieee",
                    details=APIErrorDetail(
                        code="ieee:no_results",
                        retryable=True,
                        metadata={
                            "query": query,
                            "params": {
                                "limit": limit,
                                "before": before,
                                "after": after,
                                "author": author,
                            },
                        },
                    ),
                )

            # Process results
            papers = []
            for record in response["records"]:
                try:
                    # Parse publication date (handling multiple formats)
                    pub_date = None
                    if record.get("publication_date"):
                        try:
                            pub_date = date.fromisoformat(record["publication_date"])
                        except ValueError:
                            # Fallback for other date formats
                            pass

                    papers.append(
                        Paper(
                            id=record["article_number"],
                            title=record["title"],
                            authors=[auth["name"] for auth in record["authors"]],
                            abstract=record.get("abstract", ""),
                            pdf_url=record.get("pdf_url"),
                            publication_date=pub_date,
                            source=record.get("publisher", "IEEE"),
                            doi=record.get("doi"),
                            citation_count=int(record.get("citation_count", 0)),
                        )
                    )
                except (KeyError, ValueError) as e:
                    raise APIResponseError(
                        message=f"Invalid paper record: {str(e)}",
                        source="ieee",
                        details=APIErrorDetail(
                            code="ieee:invalid_record",
                            retryable=False,
                            metadata={"record": record, "exception": str(e)},
                        ),
                    )

            return papers

        except RequestException as e:
            raise APIRequestError(
                message=f"Search failed: {str(e)}",
                source="ieee",
                details=APIErrorDetail(
                    code="ieee:network_error",
                    retryable=True,
                    metadata={"exception": str(e)},
                ),
            ) from e
        except Exception as e:
            raise APIRequestError(
                message=f"Unexpected search error: {str(e)}",
                source="ieee",
                details=APIErrorDetail(
                    code="ieee:search_failed",
                    retryable=False,
                    metadata={"exception": str(e)},
                ),
            ) from e

    def download_paper(
        self, paper_id: str, dirpath: str = ".", filename: Optional[str] = None
    ) -> None:
        """Download a paper PDF from IEEE using arnumber.

        Args:
            paper_id: IEEE article number (arnumber)
            dirpath: Directory to save PDF (default: current directory)
            filename: Custom filename (optional)

        Returns:
            Path to downloaded PDF

        Raises:
            APIResponseError: If paper not found or no PDF available
            APIRequestError: For network or filesystem issues
            APIAuthError: For authorization problems
        """
        try:
            # Validate/setup directory
            os.makedirs(dirpath, exist_ok=True)
            if not os.access(dirpath, os.W_OK):
                raise PermissionError(f"Cannot write to {dirpath}")

            # Build PDF URL (IEEE direct download pattern)
            pdf_url = (
                "http://ieeexplore.ieee.org/stampPDF/getPDF.jsp?"
                f"tp=&isnumber=&arnumber={paper_id}"
            )

            if not filename:
                filename = f"ieee_{paper_id}.pdf"
            filepath = os.path.join(dirpath, filename)

            # Download with session cookies (simulates browser)
            with requests.Session() as session:
                # Set headers to mimic browser
                session.headers.update(
                    {
                        "User-Agent": "Mozilla/5.0",
                        "Accept": "application/pdf",
                        "Referer": f"http://ieeexplore.ieee.org/document/{paper_id}",
                    }
                )

                response = session.get(
                    pdf_url, stream=True, allow_redirects=True, timeout=30
                )

                # Check for HTTP errors
                if response.status_code == 403:
                    raise APIAuthError(
                        message="PDF download forbidden - check API credentials",
                        source="ieee",
                        details=APIErrorDetail(
                            code="ieee:pdf_forbidden", retryable=False
                        ),
                    )
                elif response.status_code == 404:
                    raise APIResponseError(
                        message=f"PDF not found for paper {paper_id}",
                        source="ieee",
                        details=APIErrorDetail(
                            code="ieee:paper_not_found", retryable=False
                        ),
                    )
                elif not response.ok:
                    raise APIRequestError(
                        message=f"Download failed with HTTP {response.status_code}",
                        source="ieee",
                        details=APIErrorDetail(
                            code="ieee:download_error",
                            retryable=True,
                            metadata={
                                "status_code": response.status_code,
                                "url": pdf_url,
                            },
                        ),
                    )

                # Save PDF
                with open(filepath, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)

                # Verify PDF was actually downloaded
                if os.path.getsize(filepath) == 0:
                    os.remove(filepath)
                    raise APIResponseError(
                        message="Received empty PDF file",
                        source="ieee",
                        details=APIErrorDetail(code="ieee:empty_pdf", retryable=True),
                    )

        except requests.exceptions.SSLError as e:
            raise APIRequestError(
                message=f"SSL error during download: {str(e)}",
                source="ieee",
                details=APIErrorDetail(code="ieee:ssl_error", retryable=True),
            ) from e
        except requests.exceptions.Timeout as e:
            raise APIRequestError(
                message="Download timed out",
                source="ieee",
                details=APIErrorDetail(code="ieee:timeout", retryable=True),
            ) from e
        except Exception as e:
            # do not re-wrap custom errors
            if isinstance(e, (APIResponseError, APIAuthError, APIRequestError)):
                raise
            raise APIRequestError(
                message=f"Download failed: {str(e)}",
                source="ieee",
                details=APIErrorDetail(code="ieee:download_failed", retryable=False),
            ) from e

    def get_citation(self, paper_id: str, format: int = 0) -> Citation:
        """Get formatted citation for a paper.

        Args:
            paper_id: IEEE article number
            format: 0=MLA, 1=APA, 2=Chicago

        Returns:
            Citation object

        Raises:
            APIResponseError: For invalid requests or data
            APIRequestError: For network/retryable errors
            APIAuthError: For authorization issues
        """
        try:
            # Validate input format
            if format not in {0, 1, 2}:
                raise APIResponseError(
                    message="Invalid citation format (must be 0-2)",
                    source="ieee",
                    details=APIErrorDetail(
                        code="ieee:invalid_format",
                        retryable=False,
                        metadata={"valid_formats": [0, 1, 2]},
                    ),
                )

            # Make API call
            search_query = self.query.citations(paper_id, format)
            data = search_query.callAPI()

            # Check for API errors
            if "error" in data:
                self._handle_ieee_error(data)

            # Validate response structure
            if not data.get("citations"):
                raise APIResponseError(
                    message=f"No citations found for paper {paper_id}",
                    source="ieee",
                    details=APIErrorDetail(
                        code="ieee:no_citations",
                        retryable=False,
                        metadata={"paper_id": paper_id},
                    ),
                )

            citation_data = data["citations"][0]

            return Citation(
                id=citation_data["citation_id"],
                title=citation_data["title"],
                citation_format=["MLA", "APA", "Chicago"][format],
                citation_str=citation_data["citation_str"],
                authors=citation_data["authors"],
                year=citation_data.get("year"),
                source="IEEE",
                url=citation_data.get(
                    "url", f"https://doi.org/{citation_data.get('doi', '')}"
                ),
            )

        except KeyError as e:
            raise APIResponseError(
                message=f"Missing required citation field: {str(e)}",
                source="ieee",
                details=APIErrorDetail(
                    code="ieee:invalid_response",
                    retryable=False,
                    metadata={"citation_data": citation_data},
                ),
            ) from e
        except RequestException as e:
            raise APIRequestError(
                message=f"Network error fetching citation: {str(e)}",
                source="ieee",
                details=APIErrorDetail(code="ieee:network_error", retryable=True),
            ) from e
        except Exception as e:
            raise APIRequestError(
                message=f"Unexpected error: {str(e)}",
                source="ieee",
                details=APIErrorDetail(code="ieee:unknown_error", retryable=False),
            ) from e
