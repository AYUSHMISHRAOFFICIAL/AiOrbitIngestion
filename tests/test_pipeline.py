import pytest
from src.processing.normalization import normalize_url, normalize_name
from src.sources.http_client import validate_url, SSRFViolationError
from src.resolution import resolve_entities

def test_normalize_url():
    assert normalize_url("http://example.com:80/test?utm_source=123") == "http://example.com/test"
    assert normalize_url("HTTPS://EXAMPLE.COM/test/") == "https://example.com/test/"
    assert normalize_url("http://example.com/?ref=abc&q=1") == "http://example.com/?q=1"

def test_normalize_name():
    assert normalize_name("OpenAI Inc.") == "openai"
    assert normalize_name("Open AI, LLC") == "open ai"
    assert normalize_name("  Meta  Platforms  ") == "meta platforms"
    
    # Unicode composed/decomposed
    assert normalize_name("Cafe\u0301") == "cafe" # decomposed e + accent
    assert normalize_name("Caf\u00e9") == "cafe"  # composed e with accent
    
    # Unicode whitespace (U+2000 EN QUAD, U+3000 IDEOGRAPHIC SPACE)
    assert normalize_name("Alpha\u2000Beta\u3000Gamma") == "alpha beta gamma"
    
    # Punctuation normalization
    assert normalize_name("A.B-C!D") == "a b c d"

def test_ssrf_validation():
    # Should pass
    validate_url("https://github.com")
    
    # Should fail due to scheme
    with pytest.raises(SSRFViolationError):
        validate_url("ftp://example.com")
        
    # Should fail due to localhost
    with pytest.raises(SSRFViolationError):
        validate_url("http://localhost")
        
    with pytest.raises(SSRFViolationError):
        validate_url("http://127.0.0.1")
        
    with pytest.raises(SSRFViolationError):
        validate_url("http://169.254.169.254")

def test_entity_resolution():
    raw_entities = [
        {
            "entity_type": "Company",
            "name": "OpenAI Inc.",
            "canonical_entity_url": "https://openai.com",
            "categories": ["ai"]
        },
        {
            "entity_type": "Company",
            "name": "OpenAI",
            "canonical_entity_url": "https://openai.com",
            "categories": ["llm"]
        },
        {
            "entity_type": "Company",
            "name": "Meta AI",
            "canonical_entity_url": "https://ai.meta.com",
        }
    ]
    resolved = resolve_entities(raw_entities)
    assert len(resolved) == 2
    
    # OpenAI should be merged
    openai = next(e for e in resolved if e["name"] == "OpenAI Inc.")
    assert "ai" in openai["categories"]
    assert "llm" in openai["categories"]

from src.processing.classification import classify_entity

def test_classification_taxonomy():
    # 1. Model (from huggingface source)
    assert classify_entity({"_source": "huggingface"}) == "Model"
    # 2. News (from rss source)
    assert classify_entity({"_source": "rss"}) == "News"
    # 3. Creative (from youtube source)
    assert classify_entity({"_source": "youtube"}) == "Creative"
    
    # 4. MCP (from github source)
    assert classify_entity({"_source": "github", "repo": {"topics": ["mcp"]}}) == "MCP"
    # 5. Framework
    assert classify_entity({"_source": "github", "repo": {"description": "a web framework"}}) == "Framework"
    # 6. API
    assert classify_entity({"_source": "github", "repo": {"topics": ["api"]}}) == "API"
    # 7. Robot
    assert classify_entity({"_source": "github", "repo": {"description": "humanoid robot project"}}) == "Robot"
    # 8. Device
    assert classify_entity({"_source": "github", "repo": {"description": "custom hardware"}}) == "Device"
    # 9. Company
    assert classify_entity({"_source": "github", "repo": {"description": "official company repo"}}) == "Company"
    # 10. Research
    assert classify_entity({"_source": "github", "repo": {"description": "implementation of the paper"}}) == "Research"
    # 11. Collection
    assert classify_entity({"_source": "github", "repo": {"name": "awesome-llm"}}) == "Collection"
    # 12. Personal
    assert classify_entity({"_source": "github", "repo": {"name": "my-dotfiles"}}) == "Personal"
    # 13. Task
    assert classify_entity({"_source": "github", "repo": {"description": "evaluation benchmark"}}) == "Task"
    
    # 14. Tool (Fallback / Default for GitHub)
    assert classify_entity({"_source": "github", "repo": {"description": "general utility script"}}) == "Tool"
    
    # 15. Explicit Tool indicators
    # Explicit AI tool -> Tool
    assert classify_entity({"_source": "github", "repo": {"description": "an amazing ai tool"}}) == "Tool"
    # AI toolkit -> Tool
    assert classify_entity({"_source": "github", "repo": {"name": "my-ai-toolkit", "description": "works with models"}}) == "Tool"
    # CLI AI tool -> Tool
    assert classify_entity({"_source": "github", "repo": {"topics": ["cli", "ai"]}}) == "Tool"
    # incidental tool but clearly model -> Model
    assert classify_entity({"_source": "github", "repo": {"description": "this tool trains a model"}}) == "Model"
    # incidental tool but clearly api -> API
    assert classify_entity({"_source": "github", "repo": {"description": "this tool hits an api"}}) == "API"
    
    # Negative/Ambiguity Cases
    # Precedence test: "api" is checked before "robot" (if no explicit tool).
    assert classify_entity({"_source": "github", "repo": {"description": "robot api"}}) == "API"
    # Fallback to Tool when no keywords match
    assert classify_entity({"_source": "github", "repo": {"name": "unknown", "description": "some random string without keywords"}}) == "Tool"
from src.relationships import extract_relationships

def test_extract_relationships():
    entities = [
        {"id": "hf1", "entity_type": "Model", "name": "meta-llama/Llama-3", "source": {"name": "Hugging Face"}, "metadata": {"author": "meta-llama"}},
        {"id": "comp1", "entity_type": "Company", "name": "meta-llama"},
        {"id": "gh1", "entity_type": "Tool", "source": {"name": "GitHub"}, "metadata": {"owner_url": "https://github.com/org"}, "description": "solves task1"},
        {"id": "comp2", "entity_type": "Company", "source_url": "https://github.com/org"},
        {"id": "task1", "entity_type": "Task", "name": "task1"},
        {"id": "mcp1", "entity_type": "MCP", "description": "integrates with gh1-tool"},
        {"id": "tool2", "entity_type": "Tool", "name": "gh1-tool"},
        {"id": "dev1", "entity_type": "Device", "description": "runs meta-llama/Llama-3 local"}
    ]
    
    rels = extract_relationships(entities)
    types = [r["relationship_type"] for r in rels]
    assert "develops_model" in types
    assert "develops_tool" in types
    assert "solves_task" in types
    assert "integrates_with" in types
    assert "runs_model" in types
