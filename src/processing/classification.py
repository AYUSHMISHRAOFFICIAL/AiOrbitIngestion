import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def classify_entity(raw_item: Dict[str, Any]) -> str:
    """
    Deterministic rule-based classification.
    """
    source = raw_item.get("_source")
    
    if source == "huggingface":
        return "Model"
    elif source == "rss":
        return "News"
    elif source == "youtube":
        return "Creative"
        
    if source == "github":
        repo = raw_item.get("repo", {})
        name = repo.get("name", "").lower()
        desc = (repo.get("description") or "").lower()
        topics = repo.get("topics", [])
        text = f"{name} {desc} {' '.join(topics)}"
        
        if "mcp" in topics or "model context protocol" in text:
            return "MCP"
            
        # Explicit strong signals for Tool BEFORE generic keywords
        if "tool" in name or "toolkit" in name or "tool" in topics or "toolkit" in topics or "cli" in topics:
            return "Tool"
            
        tool_phrases = ["ai tool", "ai toolkit", "developer tool", "cli tool", "command-line tool", "ai utility", "ai assistant tool"]
        if any(phrase in text for phrase in tool_phrases):
            return "Tool"

        if "framework" in topics or "framework" in text:
            return "Framework"
        if "api" in topics or "api" in text:
            return "API"
        if "robot" in text or "robotics" in topics:
            return "Robot"
        if "device" in text or "hardware" in text:
            return "Device"
        if "company" in text:
            return "Company"
        if "research" in text or "paper" in text:
            return "Research"
        if "collection" in text or "awesome" in name:
            return "Collection"
        if "personal" in text or "dotfiles" in name:
            return "Personal"
        if "task" in text or "benchmark" in text:
            return "Task"
        if "model" in text or "llm" in topics:
            return "Model"
            
        return "Tool"
        
    return "Tool"

def extract_categories(raw_item: Dict[str, Any]) -> list:
    cats = []
    source = raw_item.get("_source")
    if source == "github":
        topics = raw_item.get("repo", {}).get("topics", [])
        cats.extend(topics)
    elif source == "huggingface":
        # HF models tags can be huge, let's just pick a few semantic ones
        pipeline_tag = raw_item.get("full_model", {}).get("pipeline_tag")
        if pipeline_tag:
            cats.append(pipeline_tag)
    
    # Filter out empty or extremely long categories
    return sorted([c.lower() for c in set(cats) if c and len(c) < 50])
