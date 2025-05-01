import subprocess


def test_search_basic() -> None:
    result = subprocess.run(
        ["iwadi", "search", "deep learning", "--source", "arxiv"],
        input="n\n",
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    # Check that some known structure appears in the output
    assert "+----" in result.stdout  # Grid table line
    assert "Title" in result.stdout
    assert "Authors" in result.stdout



# TODO: CLI Runner
# TODO: Check error handling i.e. rate limits, no results
# TODO: check that parameters are passed correctly
# TODO: check that the search results are formatted correctly (format flag)
# TODO: check different parameter combinations