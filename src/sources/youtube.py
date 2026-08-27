import logging
from typing import List, Dict, Any, Optional
from src.sources.http_client import fetch_url
from src.config import Config

logger = logging.getLogger(__name__)

class YouTubeAdapter:
    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self):
        self.api_key = Config.YOUTUBE_API_KEY

    def discover(self) -> List[Dict[str, Any]]:
        if not self.api_key:
            logger.warning("YouTube API key not found. Skipping YouTube discovery.")
            return []
            
        logger.info("Discovering from YouTube...")
        results = []
        import urllib.parse
        query = "artificial intelligence OR machine learning tools OR LLMs"
        encoded_query = urllib.parse.quote(query)
        
        per_page = min(50, Config.MAX_RECORDS_PER_SOURCE)
        page_token = ""
        
        for page in range(1, Config.MAX_PAGES_PER_SOURCE + 1):
            url = f"{self.BASE_URL}/search?part=snippet&type=video&q={encoded_query}&maxResults={per_page}&key={self.api_key}"
            if page_token:
                url += f"&pageToken={page_token}"
                
            try:
                response = fetch_url(url)
                data = response.json()
                items = data.get("items", [])
                
                if not items:
                    break
                    
                for item in items:
                    if item["id"].get("kind") == "youtube#video":
                        results.append({
                            "_source": "youtube",
                            "video": item
                        })
                        if len(results) >= Config.MAX_RECORDS_PER_SOURCE:
                            logger.info(f"Reached MAX_RECORDS_PER_SOURCE ({Config.MAX_RECORDS_PER_SOURCE}) for YouTube")
                            return results
                            
                page_token = data.get("nextPageToken")
                if not page_token:
                    break
            except Exception as e:
                logger.error(f"YouTube discovery failed on page {page}: {e}")
                break
                
        return results

    def extract(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            return item
            
        try:
            video_id = item["video"]["id"]["videoId"]
            url = f"{self.BASE_URL}/videos?part=snippet,statistics&id={video_id}&key={self.api_key}"
            response = fetch_url(url)
            data = response.json()
            if data.get("items"):
                item["full_video"] = data["items"][0]
            return item
        except Exception as e:
            logger.warning(f"Failed to extract full YouTube video {item.get('video', {}).get('id', {}).get('videoId')}: {e}")
            return item
