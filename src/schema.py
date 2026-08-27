from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field

class SourceProvenance(BaseModel):
    name: str
    url: str

class Entity(BaseModel):
    id: str
    entity_type: str
    name: str
    description: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    
    canonical_entity_url: Optional[str] = None
    homepage_url: Optional[str] = None
    repository_url: Optional[str] = None
    source_url: str
    
    source: SourceProvenance
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Relationship(BaseModel):
    id: str
    source_id: str
    target_id: str
    relationship_type: str
    confidence: float
    evidence: str
    evidence_source: str
