import logging
import uuid
from typing import List, Dict, Any

logger = logging.getLogger(__name__)
AI_ORBIT_REL_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_URL, "https://aiorbit.internal/relationships")

def extract_relationships(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Infers relationships from the resolved entities list based on evidence.
    """
    logger.info("Extracting relationships...")
    relationships = []
    
    for entity in entities:
        source_name = entity.get("source", {}).get("name", "")
        
        # Company/Model
        if entity.get("entity_type") == "Model" and source_name == "Hugging Face":
            author_id = entity.get("metadata", {}).get("author")
            if not author_id and "/" in entity.get("name", ""):
                author_id = entity.get("name").split("/")[0]
            if author_id:
                author_name = author_id.lower()
                target = next((e for e in entities if e.get("entity_type") == "Company" and e.get("name", "").lower() == author_name), None)
                if target:
                    relationships.append({
                        "id": str(uuid.uuid5(AI_ORBIT_REL_NAMESPACE, f"{target['id']}:develops_model:{entity['id']}")),
                        "source_id": target["id"],
                        "target_id": entity["id"],
                        "relationship_type": "develops_model",
                        "confidence": 0.9,
                        "evidence": "Model author matches company",
                        "evidence_source": entity.get("source_url")
                    })
                    
        # Company/Tool
        if entity.get("entity_type") == "Tool" and source_name == "GitHub":
            owner_url = entity.get("metadata", {}).get("owner_url")
            if owner_url:
                target = next((e for e in entities if e.get("source_url") == owner_url and e.get("entity_type") == "Company"), None)
                if target:
                    relationships.append({
                        "id": str(uuid.uuid5(AI_ORBIT_REL_NAMESPACE, f"{target['id']}:develops_tool:{entity['id']}")),
                        "source_id": target["id"],
                        "target_id": entity["id"],
                        "relationship_type": "develops_tool",
                        "confidence": 0.9,
                        "evidence": "GitHub organization owns tool",
                        "evidence_source": entity.get("source_url")
                    })

        # Tool/Task
        if entity.get("entity_type") == "Tool":
            desc = entity.get("description", "").lower()
            for target in entities:
                if target.get("entity_type") == "Task":
                    t_name = target.get("name", "").lower()
                    if t_name and len(t_name) > 3 and t_name in desc:
                        relationships.append({
                            "id": str(uuid.uuid5(AI_ORBIT_REL_NAMESPACE, f"{entity['id']}:solves_task:{target['id']}")),
                            "source_id": entity["id"],
                            "target_id": target["id"],
                            "relationship_type": "solves_task",
                            "confidence": 0.6,
                            "evidence": "Tool description mentions task",
                            "evidence_source": entity.get("source_url")
                        })
                        
        # MCP/Tool
        if entity.get("entity_type") == "MCP":
            desc = entity.get("description", "").lower()
            for target in entities:
                if target.get("entity_type") == "Tool":
                    t_name = target.get("name", "").lower()
                    if t_name and len(t_name) > 3 and t_name in desc:
                        relationships.append({
                            "id": str(uuid.uuid5(AI_ORBIT_REL_NAMESPACE, f"{entity['id']}:integrates_with:{target['id']}")),
                            "source_id": entity["id"],
                            "target_id": target["id"],
                            "relationship_type": "integrates_with",
                            "confidence": 0.6,
                            "evidence": "MCP mentions tool",
                            "evidence_source": entity.get("source_url")
                        })

        # Device/Model
        if entity.get("entity_type") == "Device":
            desc = entity.get("description", "").lower()
            for target in entities:
                if target.get("entity_type") == "Model":
                    target_name = target.get("name", "").lower()
                    if target_name and len(target_name) > 3 and target_name in desc:
                        relationships.append({
                            "id": str(uuid.uuid5(AI_ORBIT_REL_NAMESPACE, f"{entity['id']}:runs_model:{target['id']}")),
                            "source_id": entity["id"],
                            "target_id": target["id"],
                            "relationship_type": "runs_model",
                            "confidence": 0.6,
                            "evidence": "Device mentions model",
                            "evidence_source": entity.get("source_url")
                        })
                    
    # Deduplicate relationships by ID
    unique_rels = {r["id"]: r for r in relationships}
    return list(unique_rels.values())
