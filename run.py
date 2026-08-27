import logging
import time
from typing import List, Dict, Any

from src.config import Config
from src.sources.github import GitHubAdapter
from src.sources.huggingface import HuggingFaceAdapter
from src.sources.youtube import YouTubeAdapter
from src.sources.rss import RSSAdapter
from src.processing.cleaning import clean_text
from src.processing.normalization import normalize_url, normalize_name
from src.processing.classification import classify_entity, extract_categories
from src.resolution import resolve_entities
from src.relationships import extract_relationships
from src.io import validate_and_write

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info("Starting AI Orbit Ecosystem Data Ingestion Pipeline...")
    
    # 1. Discovery & Extraction
    raw_items = []
    adapters = [
        GitHubAdapter(),
        HuggingFaceAdapter(),
        YouTubeAdapter(),
        RSSAdapter()
    ]
    
    for adapter in adapters:
        discovered = adapter.discover()
        for item in discovered:
            extracted = adapter.extract(item)
            if extracted:
                raw_items.append(extracted)
                
    logger.info(f"Total raw items extracted: {len(raw_items)}")
    
    # 2. Cleaning, Normalization & Transformation to intermediate schema
    processed_entities = []
    for raw in raw_items:
        source_type = raw.get("_source")
        
        # Transform raw source-specific payload to generic entity intermediate format
        entity = {
            "entity_type": classify_entity(raw),
            "categories": extract_categories(raw),
            "metadata": {}
        }
        
        if source_type == "github":
            repo = raw.get("repo", {})
            owner = raw.get("owner", {})
            
            entity["name"] = clean_text(repo.get("name"), max_length=100)
            entity["description"] = clean_text(repo.get("description"))
            entity["canonical_entity_url"] = normalize_url(repo.get("html_url"))
            entity["repository_url"] = normalize_url(repo.get("html_url"))
            entity["homepage_url"] = normalize_url(repo.get("homepage"))
            entity["source_url"] = repo.get("url", "")
            entity["source"] = {"name": "GitHub", "url": repo.get("html_url", "")}
            
            entity["metadata"]["stars"] = repo.get("stargazers_count")
            entity["metadata"]["primary_language"] = repo.get("language")
            entity["metadata"]["owner_url"] = owner.get("url")
            entity["metadata"]["owner_name"] = owner.get("login")
            
            # Synthesize Company entity for the GitHub owner
            if owner.get("login"):
                comp = {
                    "entity_type": "Company",
                    "name": owner.get("login"),
                    "canonical_entity_url": normalize_url(owner.get("html_url", "")),
                    "source_url": owner.get("url", ""),
                    "source": {"name": "GitHub", "url": owner.get("html_url", "")},
                    "categories": [],
                    "metadata": {}
                }
                processed_entities.append(comp)
            
        elif source_type == "huggingface":
            model = raw.get("model", {})
            full_model = raw.get("full_model", {})
            
            entity["name"] = clean_text(model.get("id"), max_length=100)
            entity["description"] = "Hugging Face Model" # Often models lack descriptions
            entity["canonical_entity_url"] = normalize_url(f"https://huggingface.co/{model.get('id')}")
            entity["source_url"] = f"https://huggingface.co/api/models/{model.get('id')}"
            entity["source"] = {"name": "Hugging Face", "url": entity["canonical_entity_url"]}
            
            entity["metadata"]["downloads"] = model.get("downloads")
            
            # Synthesize Company entity for the HuggingFace author
            author = model.get("author") or (model.get("id", "").split("/")[0] if "/" in model.get("id", "") else None)
            if author:
                entity["metadata"]["author"] = author
                comp = {
                    "entity_type": "Company",
                    "name": author,
                    "canonical_entity_url": normalize_url(f"https://huggingface.co/{author}"),
                    "source_url": f"https://huggingface.co/{author}",
                    "source": {"name": "Hugging Face", "url": f"https://huggingface.co/{author}"},
                    "categories": [],
                    "metadata": {}
                }
                processed_entities.append(comp)
            
        elif source_type == "youtube":
            video = raw.get("video", {})
            full_video = raw.get("full_video", {})
            snippet = video.get("snippet", {})
            
            entity["name"] = clean_text(snippet.get("title"), max_length=150)
            entity["description"] = clean_text(snippet.get("description"))
            
            video_id = video.get("id", {}).get("videoId")
            entity["canonical_entity_url"] = normalize_url(f"https://youtube.com/watch?v={video_id}")
            entity["source_url"] = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}"
            entity["source"] = {"name": "YouTube", "url": entity["canonical_entity_url"]}
            
            entity["metadata"]["channel_title"] = snippet.get("channelTitle")
            
        elif source_type == "rss":
            news = raw.get("news", {})
            entity["name"] = clean_text(news.get("title"), max_length=200)
            entity["description"] = clean_text(news.get("description"))
            
            link = news.get("link")
            entity["canonical_entity_url"] = normalize_url(link)
            entity["source_url"] = raw.get("feed_url")
            entity["source"] = {"name": "RSS", "url": link or raw.get("feed_url")}
            
        processed_entities.append(entity)
        
    logger.info(f"Total intermediate entities prepared: {len(processed_entities)}")
    
    # 3. Entity Resolution + Deduplication
    resolved_entities = resolve_entities(processed_entities)
    logger.info(f"Total resolved entities: {len(resolved_entities)}")
    
    # 4. Relationship Mapping
    relationships = extract_relationships(resolved_entities)
    logger.info(f"Total relationships extracted before filtering: {len(relationships)}")
    
    # Cap entities deterministically to 280 and enforce referential integrity on relationships
    from src.processing.filtering import cap_entities_and_filter_relationships
    resolved_entities, relationships = cap_entities_and_filter_relationships(
        resolved_entities, relationships, target_count=280
    )
    
    logger.info(f"Final entities count: {len(resolved_entities)}")
    logger.info(f"Final relationships count: {len(relationships)}")
    
    # 5. Validation and Output
    validate_and_write(resolved_entities, relationships)
    logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    run_pipeline()
