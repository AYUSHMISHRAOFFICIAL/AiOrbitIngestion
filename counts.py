import json
from collections import Counter

with open("data/final/entities.json", "r", encoding="utf-8") as f:
    entities = json.load(f)

print(f"Total entities: {len(entities)}")
counts = Counter(e["entity_type"] for e in entities)
for k, v in counts.items():
    print(f"{k}: {v}")
