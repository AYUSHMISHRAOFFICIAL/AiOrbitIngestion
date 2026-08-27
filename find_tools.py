import json
from src.sources.github import GitHubAdapter
from src.processing.classification import classify_entity
from src.processing.cleaning import clean_text

adapter = GitHubAdapter()
items = adapter.discover()
print(f'Discovered {len(items)} items from github.')

tools_found = []
for i in items:
    name = i.get('name', '').lower()
    desc = (i.get('description') or '').lower()
    topics = i.get('topics', [])
    text = f'{name} {desc} {" ".join(topics)}'
    
    if 'tool' in text:
        extracted = adapter.extract(i)
        if extracted:
            classification = classify_entity(extracted)
            tools_found.append({
                'name': name,
                'desc': clean_text(desc)[:100],
                'classification': classification,
                'id': extracted.get('repo', {}).get('full_name')
            })

for t in tools_found[:10]:
    print(f"Name: {t['name']} - Class: {t['classification']} - Desc: {t['desc']}")
