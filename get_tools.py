import requests
from src.processing.classification import classify_entity

headers = {'Accept': 'application/vnd.github.v3+json'}
url = 'https://api.github.com/search/repositories?q="ai tool"'
res = requests.get(url, headers=headers).json()

items = res.get('items', [])
for repo in items[:10]:
    name = repo.get('name', '').lower()
    desc = (repo.get('description') or '').lower()
    topics = repo.get('topics', [])
    text = f'{name} {desc} {" ".join(topics)}'
    
    raw = {
        '_source': 'github',
        'repo': repo
    }
    
    classification = classify_entity(raw)
    print(f"Name: {name} | Class: {classification} | Desc: {desc[:100]}")
