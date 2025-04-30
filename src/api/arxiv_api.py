from datetime import date
from typing import List, Optional
import arxiv
from .base_api import ResearchAPI, Paper, Citation, SortOrder, SortBy
from .base_api_error import (
    APIRequestError,
    APIResponseError,
    APIServiceError,
    APIErrorDetail,
    APIAuthError,
    APIQuotaError,
)


class ArxivAPI(ResearchAPI):
    def __init__(self, max_retries: int = 3) -> None:
        self.client = arxiv.Client()
        self.max_retries = max_retries

    def _handle_arxiv_error(self, error: Exception) -> None:
        """Map arXiv-specific errors to our standard error types."""
        if isinstance(error, arxiv.HTTPError):
            raise APIRequestError(
                message=f"arXiv API request failed with HTTP {error.status}",
                status_code=error.status,
                source="arxiv",
                details=APIErrorDetail(
                    code="arxiv:http_error",
                    retryable=error.retry < self.max_retries,
                    metadata={
                        "url": error.url,
                        "retry_attempt": error.retry,
                    },
                ),
            ) from error
        elif isinstance(error, arxiv.UnexpectedEmptyPageError):
            raise APIServiceError(
                message="arXiv API returned empty page unexpectedly",
                source="arxiv",
                details=APIErrorDetail(
                    code="arxiv:empty_page",
                    retryable=True,
                    metadata={"url": error.url, "retry_attempt": error.retry},
                ),
            ) from error
        elif isinstance(error, arxiv.Result.MissingFieldError):
            raise APIResponseError(
                message=f"Missing required field in arXiv response: {error.missing_field}",
                source="arxiv",
                details=APIErrorDetail(
                    code="arxiv:missing_field",
                    retryable=False,
                    metadata={"missing_field": error.missing_field},
                ),
            ) from error
        # check for custom errors
        # TODO: Add proper logic for quota and auth errors
        elif isinstance(
            error,
            (
                APIRequestError,
                APIAuthError,
                APIQuotaError,
                APIResponseError,
                APIServiceError,
            ),
        ):
            raise  # Re-raise unchanged
        # Fallback for truly unexpected errors
        raise APIRequestError(
            message=str(error),
            source="arxiv",
            details=APIErrorDetail(code="arxiv:unknown_error", retryable=False),
        ) from error

    def search(
        self,
        query: str,
        limit: int = 10,
        before: Optional[date] = None,
        after: Optional[date] = None,
        author: Optional[str] = None,
        sort_order: Optional[SortOrder] = "descending",
        sort_by: Optional[SortBy] = "relevance",
    ) -> List[Paper]:
        try:
            query_parts = [query]
            if author:
                query_parts.append(f"au:{author}")
            if before:
                query_parts.append(f"submittedDate:[* TO {before.isoformat()}]")
            if after:
                query_parts.append(f"submittedDate:[{after.isoformat()} TO *]")

            sort_criterion_map = {
                "relevance": arxiv.SortCriterion.Relevance,
                "last_updated_date": arxiv.SortCriterion.LastUpdatedDate,
                "submitted_date": arxiv.SortCriterion.SubmittedDate,
            }

            sort_order_map = {
                "ascending": arxiv.SortOrder.Ascending,
                "descending": arxiv.SortOrder.Descending,
            }

            # criterion and value can be None
            sort_criterion = sort_criterion_map.get(
                sort_by or "relevance", arxiv.SortCriterion.Relevance
            )
            sort_order_value = sort_order_map.get(
                sort_order or "descending", arxiv.SortOrder.Descending
            )

            search = arxiv.Search(
                query=" AND ".join(query_parts),
                max_results=limit,
                sort_by=sort_criterion,
                sort_order=sort_order_value,
            )

            # obtain results before processing to make error catching easier
            raw_results = list(self.client.results(search))

            results = []
            for result in raw_results:
                try:
                    results.append(
                        Paper(
                            id=result.entry_id,
                            title=result.title,
                            authors=[a.name for a in result.authors],
                            abstract=result.summary,
                            publication_date=result.published.date(),
                            pdf_url=result.pdf_url,
                            source="arXiv",
                        )
                    )
                except AttributeError as e:
                    raise APIResponseError(
                        message="Invalid arXiv result structure",
                        source="arxiv",
                        details=APIErrorDetail(
                            code="arxiv:invalid_result",
                            retryable=False,
                            metadata={"exception": str(e)},
                        ),
                    ) from e

            if not results:
                raise APIResponseError(
                    message="No results found for query",
                    source="arxiv",
                    details=APIErrorDetail(code="arxiv:no_results", retryable=True),
                )

            return results
        except Exception as e:
            self._handle_arxiv_error(e)
            raise

    def get_citation(self, paper_id: str, format: int = 0) -> Citation:
        try:
            search = arxiv.Search(id_list=[paper_id])
            try:
                paper = next(self.client.results(search))
            except StopIteration:
                raise APIResponseError(
                    message=f"No paper found with ID: {paper_id}",
                    source="arxiv",
                    details=APIErrorDetail(
                        code="arxiv:paper_not_found", retryable=False
                    ),
                )

            try:
                authors = [author.name for author in paper.authors]
                year = paper.published.year
                title = paper.title
                url = paper.entry_id
            except AttributeError as e:
                raise APIResponseError(
                    message="Missing required fields in arXiv paper",
                    source="arxiv",
                    details=APIErrorDetail(
                        code="arxiv:missing_fields",
                        retryable=False,
                        metadata={"missing_fields": str(e)},
                    ),
                )

            # Citation formatting remains the same
            if format == 0:  # MLA
                citation_format = "MLA"
                citation_str = f'{", ".join(authors)}. "{title}." arXiv, {year}, {url}.'
            elif format == 1:  # APA
                citation_format = "APA"
                citation_str = f"{', '.join(authors)} ({year}). {title}. arXiv. {url}"
            elif format == 2:  # Chicago
                citation_format = "Chicago"
                citation_str = (
                    f'{", ".join(authors)}. "{title}." arXiv ({year}). {url}.'
                )
            else:
                citation_format = "Unknown"
                citation_str = f"{', '.join(authors)}. {title} ({year}). {url}"

            return Citation(
                id=paper.entry_id,
                title=title,
                citation_format=citation_format,
                citation_str=citation_str,
                authors=authors,
                year=year,
                source="arXiv",
                url=url,
            )
        except Exception as e:
            self._handle_arxiv_error(e)
            raise

    def download_paper(
        self, paper_id: str, dirpath: str = ".", filename: Optional[str] = None
    ) -> None:
        try:
            search = arxiv.Search(id_list=[paper_id])
            try:
                paper = next(self.client.results(search))
            except StopIteration:
                raise APIResponseError(
                    message=f"No paper found with ID: {paper_id}",
                    source="arxiv",
                    details=APIErrorDetail(
                        code="arxiv:paper_not_found", retryable=False
                    ),
                )

            try:
                paper.download_pdf(dirpath=dirpath, filename=filename or paper.title)
            except Exception as e:
                raise APIRequestError(
                    message=f"Failed to download paper {paper_id}",
                    source="arxiv",
                    details=APIErrorDetail(
                        code="arxiv:download_failed",
                        retryable=True,
                        metadata={"exception": str(e)},
                    ),
                ) from e
        except Exception as e:
            self._handle_arxiv_error(e)
