import logging
from typing import List, Dict, Any, Optional
from src.sources.http_client import fetch_url
from src.config import Config

logger = logging.getLogger(__name__)

class HuggingFaceAdapter:
    BASE_URL = "https://huggingface.co/api"

    def __init__(self):
        self.headers = {
            "User-Agent": "AI-Orbit-Ingestion-Bot"
        }
        if Config.HF_TOKEN:
            self.headers["Authorization"] = f"Bearer {Config.HF_TOKEN}"

    def discover(self) -> List[Dict[str, Any]]:
        logger.info("Discovering from Hugging Face...")
        results = []
        limit = min(100, Config.MAX_RECORDS_PER_SOURCE)
        url = f"{self.BASE_URL}/models?sort=downloads&direction=-1&limit={limit}"
        
        for page in range(1, Config.MAX_PAGES_PER_SOURCE + 1):
            try:
                response = fetch_url(url, headers=self.headers)
                models = response.json()
                if not models:
                    break
                for model in models:
                    results.append({
                        "_source": "huggingface",
                        "model": model
                    })
                    if len(results) >= Config.MAX_RECORDS_PER_SOURCE:
                        logger.info(f"Reached MAX_RECORDS_PER_SOURCE ({Config.MAX_RECORDS_PER_SOURCE}) for HF")
                        return results
                        
                next_link = response.links.get("next", {}).get("url")
                if next_link:
                    url = next_link
                else:
                    break
            except Exception as e:
                logger.error(f"Hugging Face discovery failed on page {page}: {e}")
                break
                
        return results

    def extract(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            model_id = item["model"]["id"]
            url = f"{self.BASE_URL}/models/{model_id}"
            response = fetch_url(url, headers=self.headers)
            item["full_model"] = response.json()
            return item
        except Exception as e:
            logger.warning(f"Failed to extract full HF model {item.get('model', {}).get('id')}: {e}")
            return item
