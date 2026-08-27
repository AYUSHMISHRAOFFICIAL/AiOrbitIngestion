import logging
from typing import List, Dict, Any, Optional
from src.sources.http_client import fetch_url
from src.config import Config

logger = logging.getLogger(__name__)

class GitHubAdapter:
    BASE_URL = "https://api.github.com"
    
    def __init__(self):
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AI-Orbit-Ingestion-Bot"
        }
        if Config.GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {Config.GITHUB_TOKEN}"

    def discover(self) -> List[Dict[str, Any]]:
        logger.info("Discovering from GitHub...")
        results = []
        import urllib.parse
        query = "topic:artificial-intelligence topic:machine-learning topic:llm"
        encoded_query = urllib.parse.quote(query)
        
        per_page = min(100, Config.MAX_RECORDS_PER_SOURCE)
        
        for page in range(1, Config.MAX_PAGES_PER_SOURCE + 1):
            url = f"{self.BASE_URL}/search/repositories?q={encoded_query}&sort=stars&order=desc&per_page={per_page}&page={page}"
            try:
                response = fetch_url(url, headers=self.headers)
                data = response.json()
                items = data.get("items", [])
                if not items:
                    break
                for item in items:
                    results.append({
                        "_source": "github",
                        "repo": item
                    })
                    if len(results) >= Config.MAX_RECORDS_PER_SOURCE:
                        logger.info(f"Reached MAX_RECORDS_PER_SOURCE ({Config.MAX_RECORDS_PER_SOURCE}) for GitHub")
                        return results
            except Exception as e:
                logger.error(f"GitHub discovery failed on page {page}: {e}")
                break
                
        return results

    def extract(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            repo_data = item["repo"]
            owner_url = repo_data["owner"]["url"]
            owner_response = fetch_url(owner_url, headers=self.headers)
            item["owner"] = owner_response.json()
            return item
        except Exception as e:
            logger.warning(f"Failed to extract extra GitHub details: {e}")
            return item
