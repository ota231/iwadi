import pytest
from unittest.mock import patch
from datetime import date
from src.api.ieee_api import IEEEAPI
from typing import Dict
from unittest.mock import MagicMock
from src.api.base_api_error import (
    APIRequestError,
    APIResponseError,
    APIAuthError,
)
from pathlib import Path


class TestIEEEAPI:
    @pytest.fixture
    def ieee_api(self) -> IEEEAPI:
        with patch.dict("os.environ", {"IEEE_API_KEY": "test_key"}):
            return IEEEAPI()

    # ---- Success Cases ----
    def test_search_success(self, ieee_api: IEEEAPI) -> None:
        """Test successful search with mock results"""
        mock_response = {
            "records": [
                {
                    "article_number": "12345678",
                    "title": "Test Paper",
                    "authors": [{"name": "Author 1"}, {"name": "Author 2"}],
                    "abstract": "Test abstract",
                    "publication_date": "2023-01-01",
                    "pdf_url": "http://example.com/test.pdf",
                    "publisher": "IEEE",
                    "doi": "10.1109/TEST.2023.12345678",
                    "citation_count": "5",
                }
            ]
        }

        with patch.object(ieee_api.query, "callAPI", return_value=mock_response):
            papers = ieee_api.search("machine learning", limit=1)

            assert len(papers) == 1
            paper = papers[0]
            assert paper.title == "Test Paper"
            assert paper.authors == ["Author 1", "Author 2"]
            assert paper.publication_date == date(2023, 1, 1)

    def test_download_paper_success(self, ieee_api: IEEEAPI, tmp_path: str) -> None:
        """Test successful paper download"""
        mock_response = {
            "records": [
                {"article_number": "12345678", "pdf_url": "http://example.com/test.pdf"}
            ]
        }

        with patch.object(ieee_api.query, "callAPI", return_value=mock_response), patch(
            "requests.Session.get"
        ) as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.iter_content.return_value = [b"pdf content"]

            ieee_api.download_paper("12345678", dirpath=str(tmp_path))
            pdf_path = Path(tmp_path) / "ieee_12345678.pdf"
            assert pdf_path.exists()

    # ---- Failure Cases ----
    def test_search_empty_query(self, ieee_api: IEEEAPI) -> None:
        """Test empty query validation"""
        with pytest.raises(APIResponseError) as exc_info:
            ieee_api.search("")

        assert exc_info.value.details.code == "ieee:empty_query"

    def test_search_wildcard_error(self, ieee_api: IEEEAPI) -> None:
        """Test invalid wildcard usage"""
        with pytest.raises(APIResponseError) as exc_info:
            ieee_api.search("ab*")

        assert exc_info.value.details.code == "ieee:invalid_wildcard"

    def test_search_api_error(self, ieee_api: IEEEAPI) -> None:
        """Test API error response"""
        mock_error = {"error": "Service Not Found", "status": 500}

        with patch.object(ieee_api.query, "callAPI", return_value=mock_error):
            with pytest.raises(APIRequestError) as exc_info:
                ieee_api.search("test")

            assert exc_info.value.details.code == "ieee:server_error"
            assert exc_info.value.details.retryable is True

    def test_download_paper_not_found(self, ieee_api: IEEEAPI) -> None:
        """Test download for non-existent paper"""
        mock_response: Dict = {"records": []}

        with patch.object(ieee_api.query, "callAPI", return_value=mock_response):
            with pytest.raises(APIResponseError) as exc_info:
                ieee_api.download_paper("99999999")

            assert exc_info.value.details.code == "ieee:paper_not_found"

    def test_download_no_pdf(self, ieee_api: IEEEAPI) -> None:
        """Test paper with no PDF available"""
        mock_response = {
            "records": [{"article_number": "12345678", "title": "Paper Without PDF"}]
        }

        with patch.object(ieee_api.query, "callAPI", return_value=mock_response):
            with pytest.raises(APIResponseError) as exc_info:
                ieee_api.download_paper("12345678")

            assert exc_info.value.details.code == "ieee:no_pdf_available"
            assert "Paper Without PDF" in str(exc_info.value)

    def test_auth_error(self) -> None:
        """Test missing API key"""
        with patch.dict("os.environ", {}):  # No API key
            with pytest.raises(APIAuthError) as exc_info:
                IEEEAPI()

            assert exc_info.value.details.code == "ieee:missing_api_key"

    # ---- Edge Cases ----
    def test_search_max_limit(self, ieee_api: IEEEAPI) -> None:
        """Test automatic limit adjustment"""
        mock_response: Dict = {"records": []}
        mock_query = MagicMock()
        mock_query.callAPI.return_value = mock_response

        ieee_api.query = mock_query
        ieee_api.search("test", limit=200)  # Should be capped to 100

        mock_query.maximumResults.assert_called_once_with(100)

    def test_invalid_date_format(self, ieee_api: IEEEAPI) -> None:
        """Test handling of non-ISO date formats"""
        mock_response = {
            "records": [
                {
                    "article_number": "123",
                    "title": "Old Paper",
                    "authors": [],
                    "abstract": "",
                    "publication_date": "January 2001",  # Non-ISO format
                    "publisher": "IEEE",
                }
            ]
        }

        with patch.object(ieee_api.query, "callAPI", return_value=mock_response):
            papers = ieee_api.search("test")
            assert papers[0].publication_date is None  # Should gracefully handle

    def test_query_construction(self, ieee_api: IEEEAPI) -> None:
        """Test query parameter building"""
        mock_query = MagicMock()
        mock_query.callAPI.return_value = {"records": []}

        # Apply the mock
        ieee_api.query = mock_query
        ieee_api.search(
            query="AI",
            limit=5,
            before=date(2023, 12, 31),
            after=date(2020, 1, 1),
            author="Smith",
            sort=False,
        )

        mock_query.queryText.assert_called_once_with("AI")
        mock_query.insertionEndDate.assert_called_once_with("20231231")
        mock_query.insertionStartDate.assert_called_once_with("20200101")
        mock_query.authorText.assert_called_once_with("Smith")
        mock_query.resultsSorting.assert_called_once_with("publicationYear", "desc")
