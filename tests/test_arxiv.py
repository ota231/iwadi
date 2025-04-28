import pytest
from unittest.mock import patch, MagicMock
from src.api.arxiv_api import ArxivAPI


@pytest.fixture
def arxiv_api() -> ArxivAPI:
    return ArxivAPI()


def test_search(arxiv_api: ArxivAPI) -> None:
    # Mock the client's results
    with patch.object(arxiv_api.client, "results") as mock_results:
        mock_result = MagicMock()
        mock_result.entry_id = "1234.5678"
        mock_result.title = "Test Paper"
        mock_result.authors = [
            MagicMock(name="Author One"),
            MagicMock(name="Author Two"),
        ]
        mock_result.summary = "Test Abstract"
        mock_result.published.date.return_value = "2024-04-01"
        mock_result.pdf_url = "http://arxiv.org/pdf/1234.5678.pdf"

        mock_results.return_value = [mock_result]

        papers = arxiv_api.search("machine learning", limit=1)

        assert len(papers) == 1
        paper = papers[0]
        assert paper.title == "Test Paper"
        assert paper.source == "arXiv"
        assert "Author One" in paper.authors[0] or "Author Two" in paper.authors[1]


def test_get_citation(arxiv_api: ArxivAPI) -> None:
    with patch.object(arxiv_api.client, "results") as mock_results:
        mock_result = MagicMock()
        mock_result.entry_id = "1234.5678"
        mock_result.title = "Test Citation Paper"
        mock_result.authors = [MagicMock(name="Author One")]
        mock_result.published.year = 2024

        mock_results.return_value = [mock_result]

        citation = arxiv_api.get_citation("1234.5678")

        assert citation.title == "Test Citation Paper"
        assert citation.citation_format == "MLA"
        assert "Author One" in citation.citation_str


def test_download_paper(arxiv_api: ArxivAPI, tmp_path: str) -> None:
    with patch.object(arxiv_api.client, "results") as mock_results:
        mock_result = MagicMock()
        mock_result.download_pdf = MagicMock()
        mock_result.title = "Test Download Paper"
        mock_results.return_value = [mock_result]

        arxiv_api.download_paper("1234.5678", dirpath=str(tmp_path))

        mock_result.download_pdf.assert_called_once_with(
            dirpath=str(tmp_path), filename="Test Download Paper"
        )
