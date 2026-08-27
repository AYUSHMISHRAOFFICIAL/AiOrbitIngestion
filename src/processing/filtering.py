import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

def cap_entities_and_filter_relationships(
    resolved_entities: List[Dict[str, Any]], 
    relationships: List[Dict[str, Any]], 
    target_count: int = 280
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Deterministically caps the number of entities to target_count (if greater)
    and filters relationships to only include those between retained entities.
    
    Selection priority:
    1. Entity participation in relationships (higher degree = higher priority)
    2. Fallback: string sorting by UUID to guarantee deterministic tie-breaking
    """
    if len(resolved_entities) <= target_count:
        # No capping needed, but still ensure relationships only point to valid entities
        valid_ids = {e["id"] for e in resolved_entities}
        filtered_rels = [
            r for r in relationships 
            if r["source_id"] in valid_ids and r["target_id"] in valid_ids
        ]
        return resolved_entities, filtered_rels

    logger.info(f"Capping entities from {len(resolved_entities)} to {target_count} deterministically.")
    
    # Calculate degree for each entity (number of relationships it is involved in)
    entity_degrees = {e["id"]: 0 for e in resolved_entities}
    for rel in relationships:
        if rel["source_id"] in entity_degrees:
            entity_degrees[rel["source_id"]] += 1
        if rel["target_id"] in entity_degrees:
            entity_degrees[rel["target_id"]] += 1
            
    # Sort entities deterministically
    # Sort key:
    # 1. Negative degree (so higher degree comes first)
    # 2. String value of the entity ID (ascending) as a stable tie-breaker
    sorted_entities = sorted(
        resolved_entities, 
        key=lambda e: (-entity_degrees.get(e["id"], 0), str(e["id"]))
    )
    
    # Cap the list
    retained_entities = sorted_entities[:target_count]
    retained_ids = {e["id"] for e in retained_entities}
    
    # Filter relationships to only include those where BOTH source and target are retained
    retained_relationships = [
        rel for rel in relationships
        if rel["source_id"] in retained_ids and rel["target_id"] in retained_ids
    ]
    
    logger.info(f"Retained {len(retained_relationships)} relationships after capping.")
    
    return retained_entities, retained_relationships
