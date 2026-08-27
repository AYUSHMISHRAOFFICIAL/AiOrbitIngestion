import pytest
from src.resolution import resolve_entities

def test_ambiguous_name_exact_match():
    # OpenAI vs Open AI vs OPENAI without URLs
    entities = [
        {"name": "OpenAI"},
        {"name": "Open AI"},
        {"name": "OPENAI"}
    ]
    resolved = resolve_entities(entities)
    assert len(resolved) == 3
    # First one has no ambiguous with, but the rest do
    assert "_ambiguous_with" in resolved[1]
    assert "_ambiguous_with" in resolved[2]

def test_ambiguous_fuzzy_match():
    # Llama vs Llama 2 vs Llama 3 vs LlamaIndex
    entities = [
        {"name": "Llama"},
        {"name": "Llama 2"},
        {"name": "Llama 3"},
        {"name": "LlamaIndex"}
    ]
    resolved = resolve_entities(entities)
    assert len(resolved) == 4
    # "Llama" and "Llama 2" are 77% similar -> no flag for 0.85? Let's see:
    # difflib for "llama" and "llama 2" (5 vs 7 chars) = 2 * 5 / 12 = 0.833, so it might not flag.
    # What about "llama" and "llama 3"? Same.
    # What about "llama index"? 0.66.
    # To test fuzzy, we need something > 0.85, like "HuggingFace" vs "Hugging Face"
    entities2 = [
        {"name": "HuggingFace"},
        {"name": "Hugging Face"}
    ]
    resolved2 = resolve_entities(entities2)
    assert len(resolved2) == 2
    assert "_ambiguous_with" in resolved2[1]

def test_exact_canonical_url_merge():
    entities = [
        {"name": "OpenAI", "canonical_entity_url": "https://openai.com"},
        {"name": "Open AI Inc", "canonical_entity_url": "https://openai.com"}
    ]
    resolved = resolve_entities(entities)
    assert len(resolved) == 1
    assert resolved[0]["name"] == "OpenAI"

def test_homepage_domain_match_merge():
    entities = [
        {"name": "OpenAI", "homepage_url": "https://openai.com/"},
        {"name": "OpenAI", "homepage_url": "https://openai.com/research"}
    ]
    resolved = resolve_entities(entities)
    assert len(resolved) == 1
