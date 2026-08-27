import os
import json
import pytest
from src.io import validate_and_write
from src.config import Config
from src.schema import Entity, Relationship

def test_io_validation_and_write(tmp_path):
    # override config to write to tmp_path
    Config.FINAL_DIR = str(tmp_path)
    Config.RAW_DIR = str(tmp_path)
    Config.PROCESSED_DIR = str(tmp_path)
    
    entities = [
        {
            "id": "e1",
            "entity_type": "Tool",
            "name": "Test Tool",
            "canonical_entity_url": "https://test.com",
            "categories": [],
            "metadata": {},
            "source_url": "https://test.com/source",
            "source": {"name": "Test", "url": "https://test.com/source"}
        }
    ]
    
    relationships = [
        {
            "id": "r1",
            "source_id": "e1",
            "target_id": "e1",
            "relationship_type": "solves_task",
            "confidence": 0.9,
            "evidence": "test",
            "evidence_source": "https://test.com"
        }
    ]
    
    validate_and_write(entities, relationships)
    
    entities_path = os.path.join(tmp_path, "entities.json")
    relationships_path = os.path.join(tmp_path, "relationships.json")
    
    assert os.path.exists(entities_path)
    assert os.path.exists(relationships_path)
    
    with open(entities_path, "r") as f:
        saved_entities = json.load(f)
        assert len(saved_entities) == 1
        assert saved_entities[0]["id"] == "e1"
        
    with open(relationships_path, "r") as f:
        saved_relationships = json.load(f)
        assert len(saved_relationships) == 1
        assert saved_relationships[0]["id"] == "r1"
