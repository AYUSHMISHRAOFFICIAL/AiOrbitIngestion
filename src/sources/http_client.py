import socket
import ipaddress
import logging
from urllib.parse import urlparse, urljoin
import requests
from requests.exceptions import RequestException, Timeout, TooManyRedirects
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config import Config

logger = logging.getLogger(__name__)

class SSRFViolationError(Exception):
    """Raised when a URL violates SSRF protection rules."""
    pass

class FetchError(Exception):
    """Raised when an HTTP request fails."""
    pass

class NonRetryableFetchError(Exception):
    """Raised for 4xx errors that should not be retried."""
    pass

class TransientFetchError(Exception):
    """Raised for 5xx errors or transient issues that should be retried."""
    pass

class RateLimitError(TransientFetchError):
    """Raised for 429 Too Many Requests."""
    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after

def is_allowed_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
        return True
    except ValueError:
        return False

def resolve_and_validate_hostname(hostname: str) -> None:
    """Resolves the hostname and checks if the IP is allowed (not private/local)."""
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for info in addr_info:
            ip = info[4][0]
            if not is_allowed_ip(ip):
                raise SSRFViolationError(f"Hostname {hostname} resolved to a disallowed IP: {ip}")
    except socket.gaierror as e:
        raise SSRFViolationError(f"Could not resolve hostname {hostname}: {e}")

def validate_url(url: str) -> None:
    """Validates scheme and hostname for SSRF protection."""
    parsed = urlparse(url)
    if parsed.scheme not in Config.ALLOWED_SCHEMES:
        raise SSRFViolationError(f"Disallowed scheme: {parsed.scheme}")
    
    hostname = parsed.hostname
    if not hostname:
        raise SSRFViolationError(f"Invalid URL (no hostname): {url}")
    
    try:
        ipaddress.ip_address(hostname)
        if not is_allowed_ip(hostname):
             raise SSRFViolationError(f"URL contains a disallowed IP: {hostname}")
    except ValueError:
        pass

    resolve_and_validate_hostname(hostname)

def safe_request(url: str, method: str = 'GET', headers: dict = None, params: dict = None, **kwargs) -> requests.Response:
    """
    Performs a safe HTTP request with SSRF protection, including redirect validation.
    """
    validate_url(url)
    
    session = requests.Session()
    current_url = url
    
    for _ in range(Config.MAX_REDIRECTS + 1):
        try:
            response = session.request(
                method, 
                current_url, 
                headers=headers, 
                params=params, 
                timeout=Config.HTTP_TIMEOUT,
                allow_redirects=False,
                stream=True,
                **kwargs
            )
            
            if response.is_redirect:
                next_url = response.headers.get('Location')
                if not next_url:
                    break
                next_url = urljoin(current_url, next_url)
                validate_url(next_url)
                current_url = next_url
                continue
            
            # Not a redirect, check status code
            status = response.status_code
            if status >= 400:
                if status == 429:
                    retry_after = response.headers.get('Retry-After')
                    delay = int(retry_after) if retry_after and retry_after.isdigit() else None
                    response.close()
                    raise RateLimitError(f"Rate limited (429)", retry_after=delay)
                elif status in (408, 500, 502, 503, 504):
                    response.close()
                    raise TransientFetchError(f"Transient HTTP error: {status}")
                else:
                    response.close()
                    raise NonRetryableFetchError(f"Client error: {status}")
            
            # Check Content-Length if available
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > Config.MAX_RESPONSE_SIZE:
                response.close()
                raise FetchError(f"Response size exceeded {Config.MAX_RESPONSE_SIZE} bytes.")
            
            # Check size while downloading
            content = b""
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > Config.MAX_RESPONSE_SIZE:
                    response.close()
                    raise FetchError(f"Response size exceeded {Config.MAX_RESPONSE_SIZE} bytes.")
            
            response._content = content
            response.encoding = response.apparent_encoding
            return response
            
        except requests.exceptions.Timeout as e:
            raise TransientFetchError(f"Timeout: {e}")
        except requests.exceptions.ConnectionError as e:
            raise TransientFetchError(f"Connection error: {e}")
        except requests.exceptions.RequestException as e:
            raise NonRetryableFetchError(f"Request failed: {e}")
        except SSRFViolationError as e:
            raise e

    raise NonRetryableFetchError(f"Exceeded maximum redirects ({Config.MAX_REDIRECTS}) for URL: {url}")

import time

def fetch_url(url: str, method: str = 'GET', headers: dict = None, params: dict = None, **kwargs) -> requests.Response:
    """
    Fetches a URL using safe_request, with exponential backoff retries.
    """
    logger.debug(f"Fetching URL: {url}")
    
    max_attempts = Config.RETRY_ATTEMPTS
    base_delay = 2
    max_delay = 10
    
    for attempt in range(1, max_attempts + 1):
        try:
            return safe_request(url, method=method, headers=headers, params=params, **kwargs)
        except TransientFetchError as e:
            if attempt == max_attempts:
                raise FetchError(f"Max retries reached. Last error: {e}")
            
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            if isinstance(e, RateLimitError) and e.retry_after is not None:
                delay = min(e.retry_after, max_delay)
                
            logger.warning(f"Transient error fetching {url}: {e}. Retrying in {delay} seconds (Attempt {attempt}/{max_attempts})")
            time.sleep(delay)
