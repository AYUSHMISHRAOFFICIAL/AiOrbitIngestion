import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
from src.sources.http_client import fetch_url
from src.config import Config

logger = logging.getLogger(__name__)

class RSSAdapter:
    FEEDS = [
        "https://towardsdatascience.com/feed",
        "https://bair.berkeley.edu/blog/feed.xml"
    ]

    def discover(self) -> List[Dict[str, Any]]:
        logger.info("Discovering from RSS...")
        results = []
        
        for feed_url in self.FEEDS:
            if len(results) >= Config.MAX_RECORDS_PER_SOURCE:
                break
                
            try:
                response = fetch_url(feed_url, headers={"User-Agent": "AI-Orbit-Ingestion-Bot"})
                root = ET.fromstring(response.content)
                
                items = root.findall(".//item")
                if not items:
                    items = root.findall(". //*{http://www.w3.org/2005/Atom}entry")
                
                for el in items:
                    if len(results) >= Config.MAX_RECORDS_PER_SOURCE:
                        logger.info(f"Reached MAX_RECORDS_PER_SOURCE ({Config.MAX_RECORDS_PER_SOURCE}) for RSS")
                        break
                        
                    title_el = el.find("title")
                    link_el = el.find("link")
                    desc_el = el.find("description")
                    if desc_el is None:
                         desc_el = el.find(". //*{http://www.w3.org/2005/Atom}summary")
                         
                    link = None
                    if link_el is not None:
                        link = link_el.text
                        if not link:
                            link = link_el.attrib.get("href")

                    if title_el is not None and link:
                        results.append({
                            "_source": "rss",
                            "feed_url": feed_url,
                            "news": {
                                "title": title_el.text,
                                "link": link,
                                "description": desc_el.text if desc_el is not None else ""
                            }
                        })
                        
            except Exception as e:
                logger.error(f"RSS discovery failed for {feed_url}: {e}")
                
        return results

    def extract(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # RSS usually contains what we need in the feed, no further extraction needed
        return item
