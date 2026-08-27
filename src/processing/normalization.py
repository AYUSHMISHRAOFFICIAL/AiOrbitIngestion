import re
from urllib.parse import urlparse, urlunparse
from typing import Optional

def normalize_url(url: str) -> Optional[str]:
    if not url:
        return None
    url = url.strip()
    try:
        parsed = urlparse(url)
        # Force lowercase scheme and hostname
        scheme = parsed.scheme.lower()
        hostname = (parsed.hostname or "").lower()
        
        # Remove default ports
        port = parsed.port
        if port == 80 and scheme == "http":
            port = None
        elif port == 443 and scheme == "https":
            port = None
        
        netloc = hostname
        if port:
            netloc += f":{port}"
            
        # Ensure trailing slash consistency for root domains
        path = parsed.path
        if not path:
            path = "/"
            
        # Basic removal of common tracking params
        query = parsed.query
        if query:
            params = query.split("&")
            filtered_params = [p for p in params if not p.startswith(("utm_", "ref="))]
            query = "&".join(filtered_params)
            
        # Reconstruct
        normalized = urlunparse((scheme, netloc, path, parsed.params, query, parsed.fragment))
        return normalized
    except Exception:
        return url

import unicodedata

def normalize_name(name: str) -> str:
    if not name:
        return ""
    # unicode normalization: NFKD decomposes characters, ascii encode ignores combining marks
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    # lowercase
    name = name.lower()
    # remove punctuation
    name = re.sub(r'[^\w\s]', ' ', name)
    # remove common suffixes
    name = re.sub(r'\b(inc|llc|corp|ltd|co)\b', '', name)
    # collapse whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    return name
