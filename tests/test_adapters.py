import pytest
import responses
from unittest.mock import patch
from src.sources.github import GitHubAdapter
from src.sources.huggingface import HuggingFaceAdapter
from src.sources.youtube import YouTubeAdapter
from src.sources.rss import RSSAdapter
from src.config import Config

@pytest.fixture(autouse=True)
def mock_config():
    Config.GITHUB_TOKEN = "fake_github"
    Config.HF_TOKEN = "fake_hf"
    Config.YOUTUBE_API_KEY = "fake_yt"
    Config.MAX_RECORDS_PER_SOURCE = 5
    Config.MAX_PAGES_PER_SOURCE = 2
    yield

@responses.activate
def test_github_adapter_success_pagination():
    responses.add(
        responses.GET,
        "https://api.github.com/search/repositories",
        json={"items": [{"id": 1}, {"id": 2}]},
        status=200,
        match=[responses.matchers.query_param_matcher({"q": "topic:artificial-intelligence topic:machine-learning topic:llm", "sort": "stars", "order": "desc", "per_page": 5, "page": 1})]
    )
    responses.add(
        responses.GET,
        "https://api.github.com/search/repositories",
        json={"items": []},
        status=200,
        match=[responses.matchers.query_param_matcher({"q": "topic:artificial-intelligence topic:machine-learning topic:llm", "sort": "stars", "order": "desc", "per_page": 5, "page": 2})]
    )
    
    adapter = GitHubAdapter()
    results = adapter.discover()
    
    assert len(results) == 2
    assert results[0]["_source"] == "github"

@responses.activate
def test_huggingface_adapter_success_pagination():
    responses.add(
        responses.GET,
        "https://huggingface.co/api/models",
        json=[{"id": "model1"}, {"id": "model2"}],
        status=200,
        headers={"Link": '<https://huggingface.co/api/models?page=2>; rel="next"'}
    )
    responses.add(
        responses.GET,
        "https://huggingface.co/api/models?page=2",
        json=[{"id": "model3"}],
        status=200
    )
    
    adapter = HuggingFaceAdapter()
    results = adapter.discover()
    
    assert len(results) == 3
    assert results[-1]["_source"] == "huggingface"

@responses.activate
def test_youtube_adapter_success_pagination():
    responses.add(
        responses.GET,
        "https://www.googleapis.com/youtube/v3/search",
        json={"items": [{"id": {"kind": "youtube#video", "videoId": "v1"}}], "nextPageToken": "token2"},
        status=200,
        match=[responses.matchers.query_param_matcher({"part": "snippet", "type": "video", "q": "artificial intelligence OR machine learning tools OR LLMs", "maxResults": 5, "key": "fake_yt"})]
    )
    responses.add(
        responses.GET,
        "https://www.googleapis.com/youtube/v3/search",
        json={"items": [{"id": {"kind": "youtube#video", "videoId": "v2"}}]},
        status=200,
        match=[responses.matchers.query_param_matcher({"part": "snippet", "type": "video", "q": "artificial intelligence OR machine learning tools OR LLMs", "maxResults": 5, "key": "fake_yt", "pageToken": "token2"})]
    )
    
    adapter = YouTubeAdapter()
    results = adapter.discover()
    
    assert len(results) == 2

@responses.activate
def test_rss_adapter_success():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <item>
                <title>Test 1</title>
                <link>http://example.com/1</link>
                <description>Desc 1</description>
            </item>
            <item>
                <title>Test 2</title>
                <link>http://example.com/2</link>
                <description>Desc 2</description>
            </item>
        </channel>
    </rss>
    """
    responses.add(
        responses.GET,
        "https://towardsdatascience.com/feed",
        body=xml_content,
        status=200
    )
    
    adapter = RSSAdapter()
    results = adapter.discover()
    
    assert len(results) == 2
    assert results[0]["_source"] == "rss"
    assert results[0]["news"]["title"] == "Test 1"

@responses.activate
def test_adapter_auth_failure():
    responses.add(
        responses.GET,
        "https://api.github.com/search/repositories",
        json={"message": "Bad credentials"},
        status=401
    )
    adapter = GitHubAdapter()
    results = adapter.discover()
    assert len(results) == 0

@responses.activate
@patch('time.sleep', return_value=None)
def test_adapter_rate_limit(mock_sleep):
    responses.add(
        responses.GET,
        "https://api.github.com/search/repositories",
        json={"message": "API rate limit exceeded"},
        status=403
    )
    adapter = GitHubAdapter()
    results = adapter.discover()
    assert len(results) == 0
