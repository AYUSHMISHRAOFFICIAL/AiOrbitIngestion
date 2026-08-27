import json
from collections import Counter
from src.sources.github import GitHubAdapter
from src.sources.huggingface import HuggingFaceAdapter
from src.sources.youtube import YouTubeAdapter
from src.sources.rss import RSSAdapter
from src.processing.cleaning import clean_text
from src.processing.normalization import normalize_url, normalize_name
from src.processing.classification import classify_entity, extract_categories
from src.resolution import resolve_entities
from src.relationships import extract_relationships
from src.processing.filtering import cap_entities_and_filter_relationships

def run_diagnostic():
    # 1. Discovery & Extraction
    raw_items = []
    adapters = [GitHubAdapter(), HuggingFaceAdapter(), YouTubeAdapter(), RSSAdapter()]
    for adapter in adapters:
        discovered = adapter.discover()
        for item in discovered:
            extracted = adapter.extract(item)
            if extracted:
                raw_items.append(extracted)

    # 2. Cleaning, Normalization
    processed_entities = []
    for raw in raw_items:
        source_type = raw.get("_source")
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
            
            if owner.get("login"):
                comp = {
                    "entity_type": "Company",
                    "name": owner.get("login"),
                    "canonical_entity_url": normalize_url(owner.get("html_url", "")),
                    "source_url": owner.get("url", ""),
                    "categories": [],
                    "metadata": {}
                }
                processed_entities.append(comp)
        elif source_type == "huggingface":
            model = raw.get("model", {})
            entity["name"] = clean_text(model.get("id"), max_length=100)
            entity["description"] = "Hugging Face Model"
            entity["canonical_entity_url"] = normalize_url(f"https://huggingface.co/{model.get('id')}")
            
            author = model.get("author") or (model.get("id", "").split("/")[0] if "/" in model.get("id", "") else None)
            if author:
                comp = {
                    "entity_type": "Company",
                    "name": author,
                    "canonical_entity_url": normalize_url(f"https://huggingface.co/{author}"),
                    "source_url": f"https://huggingface.co/{author}",
                    "categories": [],
                    "metadata": {}
                }
                processed_entities.append(comp)
        elif source_type == "youtube":
            video = raw.get("video", {})
            snippet = video.get("snippet", {})
            entity["name"] = clean_text(snippet.get("title"), max_length=150)
            entity["description"] = clean_text(snippet.get("description"))
            video_id = video.get("id", {}).get("videoId")
            entity["canonical_entity_url"] = normalize_url(f"https://youtube.com/watch?v={video_id}")
        elif source_type == "rss":
            news = raw.get("news", {})
            entity["name"] = clean_text(news.get("title"), max_length=200)
            entity["description"] = clean_text(news.get("description"))
            link = news.get("link")
            entity["canonical_entity_url"] = normalize_url(link)
            
        processed_entities.append(entity)

    # 3. Entity Resolution
    resolved_entities = resolve_entities(processed_entities)
    
    # 4. Relationships
    relationships = extract_relationships(resolved_entities)

    before_counts = Counter(e.get("entity_type") for e in resolved_entities)
    
    tools_before = [e for e in resolved_entities if e.get("entity_type") == "Tool"]
    robots_before = [e for e in resolved_entities if e.get("entity_type") == "Robot"]

    # 5. Capping
    capped_entities, _ = cap_entities_and_filter_relationships(resolved_entities, relationships, target_count=280)
    
    after_counts = Counter(e.get("entity_type") for e in capped_entities)

    print(f"Total resolved entities before capping: {len(resolved_entities)}\n")
    
    req_cats = ["Company", "Tool", "Task", "Model", "Device", "Robot", "MCP", "Framework", "API", "Research", "Collection", "Personal", "Creative", "News"]
    
    print("Category Counts (Before -> After):")
    for cat in req_cats:
        print(f"{cat}: {before_counts.get(cat, 0)} -> {after_counts.get(cat, 0)}")
    
    print("\nTools Before Capping:")
    for t in tools_before:
        print(f" - {t.get('name')} (ID: {t.get('id')})")
        
    print("\nRobots Before Capping:")
    for r in robots_before:
        print(f" - {r.get('name')} (ID: {r.get('id')})")
        
if __name__ == '__main__':
    run_diagnostic()
