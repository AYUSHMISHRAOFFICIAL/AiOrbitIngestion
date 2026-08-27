import pytest
import responses
import requests
import time
from unittest.mock import patch
from src.sources.http_client import fetch_url, NonRetryableFetchError, FetchError

@responses.activate
def test_404_no_retry():
    responses.add(responses.GET, 'http://example.com/api', status=404)
    with pytest.raises(NonRetryableFetchError) as exc:
        fetch_url('http://example.com/api')
    assert "Client error: 404" in str(exc.value)
    assert len(responses.calls) == 1

@responses.activate
def test_403_no_retry():
    responses.add(responses.GET, 'http://example.com/api', status=403)
    with pytest.raises(NonRetryableFetchError) as exc:
        fetch_url('http://example.com/api')
    assert "Client error: 403" in str(exc.value)
    assert len(responses.calls) == 1

@responses.activate
def test_422_no_retry():
    responses.add(responses.GET, 'http://example.com/api', status=422)
    with pytest.raises(NonRetryableFetchError) as exc:
        fetch_url('http://example.com/api')
    assert "Client error: 422" in str(exc.value)
    assert len(responses.calls) == 1

@responses.activate
@patch('time.sleep', return_value=None)
def test_429_retry_with_retry_after(mock_sleep):
    responses.add(responses.GET, 'http://example.com/api', status=429, headers={'Retry-After': '5'})
    responses.add(responses.GET, 'http://example.com/api', status=200, body="ok")
    
    res = fetch_url('http://example.com/api')
    assert res.text == "ok"
    assert len(responses.calls) == 2
    mock_sleep.assert_called_with(5)

@responses.activate
@patch('time.sleep', return_value=None)
def test_500_retry(mock_sleep):
    responses.add(responses.GET, 'http://example.com/api', status=500)
    responses.add(responses.GET, 'http://example.com/api', status=200, body="ok")
    
    res = fetch_url('http://example.com/api')
    assert res.text == "ok"
    assert len(responses.calls) == 2

@responses.activate
@patch('time.sleep', return_value=None)
def test_503_retry(mock_sleep):
    responses.add(responses.GET, 'http://example.com/api', status=503)
    responses.add(responses.GET, 'http://example.com/api', status=503)
    responses.add(responses.GET, 'http://example.com/api', status=200, body="ok")
    
    res = fetch_url('http://example.com/api')
    assert res.text == "ok"
    assert len(responses.calls) == 3

@responses.activate
@patch('time.sleep', return_value=None)
def test_timeout_retry(mock_sleep):
    responses.add(responses.GET, 'http://example.com/api', body=requests.exceptions.Timeout("Timeout"))
    responses.add(responses.GET, 'http://example.com/api', status=200, body="ok")
    
    res = fetch_url('http://example.com/api')
    assert res.text == "ok"
    assert len(responses.calls) == 2

@responses.activate
@patch('time.sleep', return_value=None)
def test_connection_failure_retry(mock_sleep):
    responses.add(responses.GET, 'http://example.com/api', body=requests.exceptions.ConnectionError("Connection Failed"))
    responses.add(responses.GET, 'http://example.com/api', status=200, body="ok")
    
    res = fetch_url('http://example.com/api')
    assert res.text == "ok"
    assert len(responses.calls) == 2
