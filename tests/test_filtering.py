import pytest
from src.processing.filtering import cap_entities_and_filter_relationships

def test_filtering_under_cap():
    entities = [{"id": f"e{i}"} for i in range(100)]
    rels = [{"id": "r1", "source_id": "e1", "target_id": "e2"}]
    
    capped_entities, capped_rels = cap_entities_and_filter_relationships(entities, rels, target_count=280)
    
    assert len(capped_entities) == 100
    assert len(capped_rels) == 1

def test_filtering_over_cap():
    # 300 entities
    entities = [{"id": f"e{i}"} for i in range(300)]
    # relationships linking some of them
    rels = [{"id": f"r{i}", "source_id": f"e{i}", "target_id": f"e{i+1}"} for i in range(50)]
    
    capped_entities, capped_rels = cap_entities_and_filter_relationships(entities, rels, target_count=280)
    
    # Check count
    assert len(capped_entities) == 280
    
    # Check deterministic selection (entities with relationships should be prioritized)
    # The first 51 entities (e0 to e50) are involved in relationships, so they should be included
    capped_ids = {e["id"] for e in capped_entities}
    for i in range(51):
        assert f"e{i}" in capped_ids
        
    # Check relationships are filtered correctly
    for r in capped_rels:
        assert r["source_id"] in capped_ids
        assert r["target_id"] in capped_ids
        
    # Ensure no duplicates
    assert len(capped_ids) == len(capped_entities)
    
    # Test repeatability
    capped_entities_2, capped_rels_2 = cap_entities_and_filter_relationships(entities, rels, target_count=280)
    assert [e["id"] for e in capped_entities] == [e["id"] for e in capped_entities_2]

def test_filtering_relationship_integrity():
    # E0, E1, E2
    entities = [{"id": "e0"}, {"id": "e1"}, {"id": "e2"}]
    # e1 -> e2
    rels = [{"id": "r1", "source_id": "e1", "target_id": "e2"}]
    
    # Cap to 2, e1 and e2 should be chosen because they have degree 1, e0 has 0.
    capped_entities, capped_rels = cap_entities_and_filter_relationships(entities, rels, target_count=2)
    
    capped_ids = {e["id"] for e in capped_entities}
    assert "e1" in capped_ids
    assert "e2" in capped_ids
    assert "e0" not in capped_ids
    
    assert len(capped_rels) == 1
    assert capped_rels[0]["source_id"] == "e1"
    assert capped_rels[0]["target_id"] == "e2"

def test_filtering_orphaned_relationship():
    # What if a relationship points to a non-existent entity even before capping?
    entities = [{"id": "e1"}]
    rels = [{"id": "r1", "source_id": "e1", "target_id": "e2"}]
    
    capped_entities, capped_rels = cap_entities_and_filter_relationships(entities, rels, target_count=10)
    
    # The relationship should be stripped because e2 doesn't exist in entities
    assert len(capped_rels) == 0
