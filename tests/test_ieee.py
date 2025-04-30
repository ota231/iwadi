import pytest
from unittest.mock import patch
from datetime import date
from src.api.ieee_api import IEEEAPI
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

        # Mock both the query builder AND callAPI
        with patch.object(
            ieee_api.query, "queryText", return_value=ieee_api.query
        ) as mock_query_text, patch.object(
            ieee_api.query, "callAPI", return_value=mock_response
        ):
            papers = ieee_api.search("machine learning", limit=1)

            assert len(papers) == 1
            paper = papers[0]
            assert paper.title == "Test Paper"
            assert paper.authors == ["Author 1", "Author 2"]

            mock_query_text.assert_called_once_with("machine learning")

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
        print(exc_info.value.details)

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

            assert exc_info.value.details.code == "ieee:search_failed"
            assert exc_info.value.details.retryable is False

    def test_download_paper_not_found(self, ieee_api: IEEEAPI) -> None:
        """Test download for non-existent paper"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.ok = False

        with patch.object(
            ieee_api.query, "callAPI", return_value={"records": []}
        ), patch("requests.Session.get", return_value=mock_response):
            with pytest.raises(APIResponseError) as exc_info:
                ieee_api.download_paper("99999999")

            assert exc_info.value.details.code == "ieee:paper_not_found"

    def test_auth_error(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test missing API key"""
        monkeypatch.delenv("IEEE_API_KEY", raising=False)

        # mock load_dotenv() to do nothing
        with patch("src.api.ieee_api.load_dotenv") as mock_load:
            with pytest.raises(APIAuthError) as exc_info:
                IEEEAPI()

            assert exc_info.value.details.code == "ieee:missing_api_key"
            mock_load.assert_called_once()  # ensure it tried to load env

    # ---- Edge Cases ----
    def test_invalid_date_format(self, ieee_api: IEEEAPI) -> None:
        """Test that invalid date formats raise APIRequestError"""
        mock_response = {
            "records": [
                {
                    "article_number": "123",
                    "title": "Old Paper",
                    "authors": [{"name": "Author"}],
                    "abstract": "",
                    "publication_date": "January 2001",  # Non-ISO format
                    "publisher": "IEEE",
                }
            ]
        }

        with patch.object(ieee_api.query, "callAPI", return_value=mock_response):
            with pytest.raises(APIRequestError) as exc_info:
                ieee_api.search("test")

            # Verify the error details
            assert exc_info.value.details.code == "ieee:search_failed"
            print(exc_info.value)
            assert not exc_info.value.details.retryable

    def test_query_construction(self, ieee_api: IEEEAPI) -> None:
        """Test query parameter building"""
        mock_query = MagicMock()
        # Configure each method to return the mock itself for chaining
        mock_query.queryText.return_value = mock_query
        mock_query.insertionEndDate.return_value = mock_query
        mock_query.insertionStartDate.return_value = mock_query
        mock_query.authorText.return_value = mock_query
        mock_query.resultsSorting.return_value = mock_query
        mock_query.startingResult.return_value = mock_query
        mock_query.maximumResults.return_value = mock_query

        # Return a valid response with dummy data
        mock_query.callAPI.return_value = {
            "records": [
                {
                    "article_number": "123",
                    "title": "Test Paper",
                    "authors": [{"name": "Author"}],
                    "abstract": "Abstract",
                    "citation_count": 0,
                }
            ]
        }

        ieee_api.query = mock_query
        ieee_api.search(
            query="AI",
            limit=5,
            before=date(2023, 12, 31),
            after=date(2020, 1, 1),
            author="Smith",
            sort_order="ascending",
            sort_by="submitted_date",
        )

        mock_query.queryText.assert_called_once_with("AI")
        mock_query.insertionEndDate.assert_called_once_with("20231231")
        mock_query.insertionStartDate.assert_called_once_with("20200101")
        mock_query.authorText.assert_called_once_with("Smith")
        mock_query.resultsSorting.assert_called_once_with("publication_year", "asc")
        mock_query.maximumResults.assert_called_once_with(5)
