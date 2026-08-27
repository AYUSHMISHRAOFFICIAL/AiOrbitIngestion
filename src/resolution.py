import uuid
import logging
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from src.schema import Entity
from src.processing.normalization import normalize_name, normalize_url

logger = logging.getLogger(__name__)

# Predefined namespace for AI Orbit UUIDv5 generation
AI_ORBIT_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "https://aiorbit.internal")

def generate_stable_id(entity: Dict[str, Any]) -> str:
    """
    UUIDv5 Strategy: entity_type + canonical identity + trusted source identifier
    Fallback Hierarchy:
    1. Canonical URL
    2. Trusted source ID
    3. Canonical domain + normalized name
    4. Normalized name + entity type
    """
    entity_type = entity.get("entity_type", "Unknown").lower()
    canonical_url = entity.get("canonical_entity_url")
    source_url = entity.get("source_url")
    name = entity.get("name", "")
    norm_name = normalize_name(name)
    
    identity_string = ""
    
    if canonical_url:
        identity_string = f"{entity_type}:{canonical_url}"
    elif source_url:
         identity_string = f"{entity_type}:{source_url}"
    else:
        # fallback
        homepage_url = entity.get("homepage_url")
        if homepage_url:
             try:
                 domain = urlparse(homepage_url).netloc
                 identity_string = f"{entity_type}:{domain}:{norm_name}"
             except:
                 pass
                 
        if not identity_string:
            identity_string = f"{entity_type}:{norm_name}"
            
    return str(uuid.uuid5(AI_ORBIT_NAMESPACE, identity_string))

import difflib

def resolve_entities(raw_entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    1. Level 1: Exact canonical URL -> AUTO MERGE
    2. Level 2: Exact trusted source identifier -> AUTO MERGE
    3. Level 3: Canonical URL/domain + compatible identity -> AUTO MERGE
    4. Level 4: Normalized name + strong contextual evidence -> POSSIBLE AUTO MERGE
    5. Level 5: Fuzzy name similarity -> AMBIGUOUS / KEEP SEPARATE
    """
    logger.info("Resolving entities...")
    resolved = []
    
    for raw in raw_entities:
        canonical_url = raw.get("canonical_entity_url")
        source_url = raw.get("source_url")
        norm_name = normalize_name(raw.get("name", ""))
        
        merged = False
        for existing in resolved:
            existing_canonical_url = existing.get("canonical_entity_url")
            existing_source_url = existing.get("source_url")
            existing_norm_name = normalize_name(existing.get("name", ""))
            
            # Level 1: Exact canonical URL
            if canonical_url and existing_canonical_url and canonical_url == existing_canonical_url:
                merge_entities(existing, raw)
                merged = True
                break
                
            # Level 2: Exact trusted source identifier
            if source_url and existing_source_url and source_url == existing_source_url:
                merge_entities(existing, raw)
                merged = True
                break
                
            # Level 3: Canonical domain + compatible identity
            if homepage_domains_match(raw, existing) and norm_name == existing_norm_name and norm_name:
                merge_entities(existing, raw)
                merged = True
                break
                
            # Level 4/5: Ambiguous Exact or Fuzzy name match without strong evidence
            if norm_name and existing_norm_name:
                if norm_name == existing_norm_name:
                    logger.warning(f"Ambiguous exact name match without domain evidence: {norm_name}")
                    raw["_ambiguous_with"] = existing.get("name", existing_norm_name)
                    # KEEP SEPARATE
                    continue
                    
                similarity = difflib.SequenceMatcher(None, norm_name, existing_norm_name).ratio()
                if similarity > 0.85:
                    logger.warning(f"Ambiguous fuzzy match: '{norm_name}' ~ '{existing_norm_name}'")
                    raw["_ambiguous_with"] = existing.get("name", existing_norm_name)
                    # KEEP SEPARATE
                    continue
            
        if not merged:
            resolved.append(raw)
            
    # Assign IDs after merging
    for entity in resolved:
        entity["id"] = generate_stable_id(entity)
        
    return resolved

def merge_entities(target: Dict[str, Any], source: Dict[str, Any]):
    """Merges source data into target data."""
    if "categories" in source:
        target_cats = set(target.get("categories", []))
        target_cats.update(source.get("categories", []))
        target["categories"] = sorted(list(target_cats))
        
    if not target.get("description") and source.get("description"):
        target["description"] = source.get("description")
        
    if not target.get("canonical_entity_url") and source.get("canonical_entity_url"):
        target["canonical_entity_url"] = source.get("canonical_entity_url")

def homepage_domains_match(e1: Dict[str, Any], e2: Dict[str, Any]) -> bool:
    h1 = e1.get("homepage_url")
    h2 = e2.get("homepage_url")
    if not h1 or not h2:
        return False
    try:
        return urlparse(h1).netloc == urlparse(h2).netloc
    except:
        return False
