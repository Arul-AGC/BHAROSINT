import os
import pytest
from src.exporter import export_json, export_csv, export_html

@pytest.fixture
def mock_results():
    return [
        {"title": "Test Title", "snippet": "Test snippet", "link": "http://test.com", "lang": "en"}
    ]

@pytest.fixture
def mock_analysis():
    return {
        "summary": "Test summary",
        "keywords": ["test"],
        "sentiment": {"label": "Positive", "score": 1, "positive_terms": ["good"]},
        "threat": {"level": "LOW", "score": 1, "threat_terms": ["leak"]},
        "entities": {"persons": ["Test Person"]},
        "stats": {"items_analyzed": 1}
    }

def test_export_json(tmp_path, mock_results, mock_analysis):
    out_dir = str(tmp_path)
    filepath = export_json(mock_results, mock_analysis, "test_query", out_dir)
    assert os.path.exists(filepath)
    assert filepath.endswith(".json")
    with open(filepath, "r") as f:
        content = f.read()
        assert "Test Title" in content
        assert "Test summary" in content

def test_export_csv(tmp_path, mock_results):
    out_dir = str(tmp_path)
    filepath = export_csv(mock_results, None, "test_query", out_dir)
    assert os.path.exists(filepath)
    assert filepath.endswith(".csv")
    with open(filepath, "r") as f:
        content = f.read()
        assert "Test Title" in content
        assert "title,snippet,link,lang" in content

def test_export_html(tmp_path, mock_results, mock_analysis):
    out_dir = str(tmp_path)
    filepath = export_html(mock_results, mock_analysis, "test_query", out_dir)
    assert os.path.exists(filepath)
    assert filepath.endswith(".html")
    with open(filepath, "r") as f:
        content = f.read()
        assert "<html" in content
        assert "Test Title" in content
        assert "Test summary" in content
        assert "Test Person" in content

def test_export_csv_empty(tmp_path):
    out_dir = str(tmp_path)
    filepath = export_csv([], None, "test_query", out_dir)
    assert os.path.exists(filepath)
    with open(filepath, "r") as f:
        content = f.read()
        assert "No results found" in content
