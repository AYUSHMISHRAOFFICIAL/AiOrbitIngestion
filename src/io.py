import json
import logging
import os
from typing import List, Dict, Any
from src.config import Config
from src.schema import Entity, Relationship

logger = logging.getLogger(__name__)

def validate_and_write(entities: List[Dict[str, Any]], relationships: List[Dict[str, Any]]):
    """
    Validates entities and relationships against Pydantic schemas and writes them to the final directory.
    """
    logger.info("Validating entities...")
    valid_entities = []
    entity_ids = set()
    
    for raw_ent in entities:
        try:
            ent_obj = Entity(**raw_ent)
            valid_entities.append(ent_obj.model_dump())
            entity_ids.add(ent_obj.id)
        except Exception as e:
            logger.error(f"Failed to validate entity {raw_ent.get('id')}: {e}")
            
    logger.info("Validating relationships...")
    valid_relationships = []
    
    for raw_rel in relationships:
        # Check referential integrity
        source_id = raw_rel.get("source_id")
        target_id = raw_rel.get("target_id")
        
        if source_id not in entity_ids or target_id not in entity_ids:
            logger.warning(f"Referential integrity failed for relationship {raw_rel.get('id')}. Skipping.")
            continue
            
        try:
            rel_obj = Relationship(**raw_rel)
            valid_relationships.append(rel_obj.model_dump())
        except Exception as e:
            logger.error(f"Failed to validate relationship {raw_rel.get('id')}: {e}")
            
    # Create output directories if they don't exist
    os.makedirs(Config.FINAL_DIR, exist_ok=True)
    os.makedirs(Config.RAW_DIR, exist_ok=True)
    os.makedirs(Config.PROCESSED_DIR, exist_ok=True)
    
    entities_path = os.path.join(Config.FINAL_DIR, "entities.json")
    relationships_path = os.path.join(Config.FINAL_DIR, "relationships.json")
    
    logger.info(f"Writing {len(valid_entities)} entities to {entities_path}")
    with open(entities_path, "w", encoding="utf-8") as f:
        json.dump(valid_entities, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Writing {len(valid_relationships)} relationships to {relationships_path}")
    with open(relationships_path, "w", encoding="utf-8") as f:
        json.dump(valid_relationships, f, indent=2, ensure_ascii=False)
