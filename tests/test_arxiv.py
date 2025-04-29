import pytest
import arxiv
from unittest.mock import MagicMock, patch
from datetime import date
from src.api.arxiv_api import ArxivAPI
from src.api.base_api_error import APIResponseError, APIRequestError, APIServiceError


class TestArxivAPI:
    @pytest.fixture
    def arxiv_api(self) -> ArxivAPI:
        return ArxivAPI()

    def test_search_success(self, arxiv_api: ArxivAPI) -> None:
        """Test successful search with mock results"""
        mock_paper = MagicMock()
        mock_paper.entry_id = "1234.5678"
        mock_paper.title = "Test Paper"
        mock_paper.authors = [
            type("Author", (), {"name": "Author One"}),
            type("Author", (), {"name": "Author Two"}),
        ]
        mock_paper.summary = "Test abstract"
        mock_paper.published.date.return_value = date(2023, 1, 1)
        mock_paper.pdf_url = "http://test.url/pdf"

        with patch.object(arxiv_api.client, "results", return_value=iter([mock_paper])):
            papers = arxiv_api.search("test query")

            assert len(papers) == 1
            paper = papers[0]
            assert paper.title == "Test Paper"
            assert paper.authors == ["Author One", "Author Two"]

    def test_search_empty_results(self, arxiv_api: ArxivAPI) -> None:
        """Test empty results handling"""
        with patch.object(arxiv_api.client, "results", return_value=iter([])):
            with pytest.raises(APIResponseError) as exc_info:
                arxiv_api.search("test query")
            assert "No results found" in str(exc_info.value)

    def test_get_citation_success(self, arxiv_api: ArxivAPI) -> None:
        """Test citation generation"""
        mock_paper = MagicMock()
        mock_paper.entry_id = "1234.5678"
        mock_paper.title = "Test Paper"
        mock_paper.authors = [type("Author", (), {"name": "Test Author"})]
        mock_paper.published.year = 2023

        with patch.object(arxiv_api.client, "results", return_value=iter([mock_paper])):
            citation = arxiv_api.get_citation("1234.5678")
            assert citation.title == "Test Paper"
            assert "Test Author" in citation.citation_str

    def test_get_citation_missing_paper(self, arxiv_api: ArxivAPI) -> None:
        """Test paper not found error"""
        with patch.object(arxiv_api.client, "results", return_value=iter([])):
            with pytest.raises(APIResponseError) as exc_info:
                arxiv_api.get_citation("invalid_id")
            assert "No paper found" in str(exc_info.value)

    def test_download_paper_success(self, arxiv_api: ArxivAPI, tmp_path: str) -> None:
        """Test paper download"""
        mock_paper = MagicMock()
        mock_paper.title = "Test Paper"
        mock_paper.download_pdf = MagicMock()

        with patch.object(arxiv_api.client, "results", return_value=iter([mock_paper])):
            arxiv_api.download_paper("1234.5678", dirpath=str(tmp_path))
            mock_paper.download_pdf.assert_called_once_with(
                dirpath=str(tmp_path), filename="Test Paper"
            )

    def test_http_error_handling(self, arxiv_api: ArxivAPI) -> None:
        """Test HTTP error propagation"""
        mock_error = arxiv.HTTPError(
            url="http://arxiv.org/fail",
            retry=0,
            status=404,
        )

        with patch.object(arxiv_api.client, "results", side_effect=mock_error):
            with pytest.raises(APIRequestError) as exc_info:
                arxiv_api.search("test query")
            assert "HTTP 404" in str(exc_info.value)

    def test_search_http_error(self, arxiv_api: ArxivAPI) -> None:
        """Test HTTP error during search"""
        mock_error = arxiv.HTTPError(
            url="http://arxiv.org/fail",
            retry=0,
            status=500,
        )

        with patch.object(arxiv_api.client, "results", side_effect=mock_error):
            with pytest.raises(APIRequestError) as exc_info:
                arxiv_api.search("test query")
            assert "HTTP 500" in str(exc_info.value)
            assert exc_info.value.details.retryable is True

    def test_search_empty_page_error(self, arxiv_api: ArxivAPI) -> None:
        """Test unexpected empty page error"""
        mock_error = arxiv.UnexpectedEmptyPageError(
            url="http://arxiv.org/empty",
            retry=1,
            raw_feed="<feed></feed>",
        )

        with patch.object(arxiv_api.client, "results", side_effect=mock_error):
            with pytest.raises(APIServiceError) as exc_info:
                arxiv_api.search("test query")
            assert "empty page" in str(exc_info.value).lower()
            assert exc_info.value.details.retryable is True

    def test_search_missing_field_error(self, arxiv_api: ArxivAPI) -> None:
        """Test missing required field in response"""
        mock_error = arxiv.Result.MissingFieldError(
            missing_field="authors",
        )

        with patch.object(arxiv_api.client, "results", side_effect=mock_error):
            with pytest.raises(APIResponseError) as exc_info:
                arxiv_api.search("test query")
            assert "authors" in str(exc_info.value)
            assert exc_info.value.details.retryable is False

    def test_download_paper_paper_not_found(
        self, arxiv_api: ArxivAPI, tmp_path: str
    ) -> None:
        """Test paper not found error during download"""
        with patch.object(arxiv_api.client, "results", return_value=iter([])):
            with pytest.raises(APIResponseError) as exc_info:
                arxiv_api.download_paper("1234", dirpath=str(tmp_path))
            assert "No paper found with ID: 1234" in str(exc_info.value)

    def test_download_paper_fail_permission(
        self, arxiv_api: ArxivAPI, tmp_path: str
    ) -> None:
        """Test download permission error"""
        mock_paper = MagicMock()
        mock_paper.title = "Test Paper"
        mock_paper.download_pdf.side_effect = PermissionError("Read-only filesystem")

        with patch.object(arxiv_api.client, "results", return_value=iter([mock_paper])):
            with pytest.raises(APIRequestError) as exc_info:
                arxiv_api.download_paper("1234.5678", dirpath=str(tmp_path))
            assert (
                exc_info.value.details.metadata is not None
            )  # Ensure metadata exists (APIErrorDetail is Dict or None type)
            exception_msg = exc_info.value.details.metadata["exception"]
            assert "read-only" in exception_msg.lower()
            assert exc_info.value.details.retryable is True

    def test_search_retry_exhausted(self, arxiv_api: ArxivAPI) -> None:
        """Test that search properly handles retry exhaustion when API requests keep failing."""
        mock_error = arxiv.HTTPError(
            url="http://arxiv.org/retry_fail",
            retry=arxiv_api.max_retries,  # matches retry limit
            status=503,
        )

        with patch.object(arxiv_api.client, "results", side_effect=mock_error):
            with pytest.raises(APIRequestError) as exc_info:
                arxiv_api.search("test query")

            assert exc_info.value.status_code == 503
            assert (
                exc_info.value.details.metadata is not None
            )  # Ensure metadata exists (APIErrorDetail is Dict or None type)
            assert (
                exc_info.value.details.metadata["retry_attempt"]
                == arxiv_api.max_retries
            )
            assert exc_info.value.details.retryable is False
