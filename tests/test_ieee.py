import pytest
from unittest.mock import MagicMock
from src.api.ieee_api import IEEEAPI

# Sample mock data for the tests
mock_paper_data = {
    "records": [
        {
            "article_number": "12345",
            "title": "Sample Paper",
            "authors": ["John Doe", "Jane Smith"],
            "abstract": "This is a sample abstract.",
            "pdf_url": "https://example.com/sample.pdf",
            "publication_date": "2021-01-01",
            "source": "IEEE",
            "doi": "10.1109/sample.2021",
            "citation_count": 10,
        }
    ]
}

mock_citation_data = {
    "citations": [
        {
            "citation_id": "54321",
            "title": "Cited Paper",
            "citation_format": "IEEE",
            "citation_str": "Doe, J., & Smith, J. (2021). Cited Paper. IEEE.",
            "authors": ["John Doe", "Jane Smith"],
            "year": 2021,
            "source": "IEEE",
            "url": "https://example.com/cited-paper",
        }
    ]
}


# Mocking Xplore API calls
@pytest.fixture
def mock_xplore_api() -> MagicMock:
    # Create a mock instance of Xplore
    mock_api = MagicMock()

    # Mock the callAPI method to return mock data
    mock_api.queryText.return_value.callAPI.return_value = mock_paper_data
    mock_api.articleNumber.return_value.callAPI.return_value = mock_paper_data
    mock_api.citations.return_value.callAPI.return_value = mock_citation_data

    return mock_api


@pytest.fixture
def ieee_api(mock_xplore_api: MagicMock) -> IEEEAPI:
    # Inject the mock Xplore API into the IEEEAPI instance
    api = IEEEAPI()
    api.query = mock_xplore_api  # Replace the actual API with the mock
    return api


# Test the search method
def test_search(ieee_api: IEEEAPI) -> None:
    papers = ieee_api.search(
        query="AI research",
        limit=5,
        before=None,
        after=None,
        author="John Doe",
        sort=True,
    )

    assert len(papers) == 1  # We have one paper in our mock data
    assert papers[0].id == "12345"
    assert papers[0].title == "Sample Paper"
    assert papers[0].authors == ["John Doe", "Jane Smith"]
    assert papers[0].pdf_url == "https://example.com/sample.pdf"


# Test the download_paper method
def test_download_paper(ieee_api: IEEEAPI) -> None:
    paper = ieee_api.download_paper("12345")

    assert paper is not None
    assert paper.id == "12345"
    assert paper.title == "Sample Paper"
    assert paper.authors == ["John Doe", "Jane Smith"]
    assert paper.pdf_url == "https://example.com/sample.pdf"


# Test the get_citation method
def test_get_citation(ieee_api: IEEEAPI) -> None:
    citation = ieee_api.get_citation("12345", format=0)

    assert citation is not None
    assert citation.id == "54321"
    assert citation.title == "Cited Paper"
    assert citation.citation_str == "Doe, J., & Smith, J. (2021). Cited Paper. IEEE."
    assert citation.authors == ["John Doe", "Jane Smith"]
    assert citation.year == 2021
    assert citation.source == "IEEE"
    assert citation.url == "https://example.com/cited-paper"
