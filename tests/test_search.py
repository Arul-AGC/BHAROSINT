import pytest
from src.search import duckduckgo_search

# This is a 'fixture'. It's like a setup variable that gets injected into our tests.
# This represents the FAKE raw data DuckDuckGo might return.
@pytest.fixture
def mock_ddg_response():
    return [
        {
            "title": "Python Programming",
            "body": "Python is a high-level programming language.",
            "href": "https://python.org"
        },
        {
            "title": "Learn Hindi",
            "body": "भारत में पाइथन प्रोग्रामिंग (Python programming in India)",
            "href": "https://example.com/hi"
        }
    ]

# The 'mocker' argument is provided by pytest-mock. 
# We use it to hijack the real DDGS.text function.
def test_duckduckgo_search_success(mocker, mock_ddg_response):
    # Hijack the inner DDGS context manager and its 'text' method
    mock_ddgs_instance = mocker.MagicMock()
    mock_ddgs_instance.text.return_value = mock_ddg_response
    
    # We mock the DDGS class itself so when our code calls DDGS(), it gets our mock
    mocker.patch("src.search.DDGS", return_value=mocker.MagicMock(__enter__=mocker.MagicMock(return_value=mock_ddgs_instance)))
    
    # Now we call our actual search function. 
    # Under the hood, it hits our mock instead of the real internet.
    results = duckduckgo_search("python", limit=2, lang="en")
    
    # Finally, we ASSERT (verify) that our code massaged the data correctly.
    # We expect our code to change "body" -> "snippet" and "href" -> "link"
    assert len(results) == 2
    assert results[0]["title"] == "Python Programming"
    assert results[0]["snippet"] == "Python is a high-level programming language."
    assert results[0]["link"] == "https://python.org"


def test_duckduckgo_search_language_filtering(mocker, mock_ddg_response):
    """Test that searching in Hindi successfully filters non-Hindi text if strict."""
    mock_ddgs_instance = mocker.MagicMock()
    mock_ddgs_instance.text.return_value = mock_ddg_response
    mocker.patch("src.search.DDGS", return_value=mocker.MagicMock(__enter__=mocker.MagicMock(return_value=mock_ddgs_instance)))
    
    # This time we ask for "hi" (Hindi) results.
    # Our internal `_filter_by_language` should strip out the English-only result.
    results = duckduckgo_search("python", limit=2, lang="hi")
    
    # The filter should leave us with only 1 result (the one with Hindi characters)
    assert len(results) == 1
    assert "भारत में पाइथन" in results[0]["snippet"]
