import json

try:
    with open('data/final/entities.json', encoding='utf-8') as f:
        ents = json.load(f)
except FileNotFoundError:
    ents = []

try:
    with open('data/final/relationships.json', encoding='utf-8') as f:
        rels = json.load(f)
except FileNotFoundError:
    rels = []

print(f"Entities: {len(ents)}")
print(f"Relationships: {len(rels)}")

cats = set()
sources = set()
entity_types = set()
unique_ids = set()
duplicate_ids = 0

for e in ents:
    cats.update(e.get("categories", []))
    sources.add(e.get("source", {}).get("name"))
    entity_types.add(e.get("entity_type"))
    if e.get("id") in unique_ids:
        duplicate_ids += 1
    unique_ids.add(e.get("id"))

print(f"Unique IDs: {len(unique_ids)}")
print(f"Duplicate IDs: {duplicate_ids}")
print(f"Categories: {cats}")
print(f"Sources: {sources}")
print(f"Entity Types: {entity_types}")
