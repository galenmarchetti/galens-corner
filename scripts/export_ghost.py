#!/usr/bin/env python3
"""Export published Markdown posts to Ghost's documented JSON import format."""
import json
from datetime import datetime, timezone
from build import ROOT, read_posts

posts = []
for n, post in enumerate(read_posts(), start=1):
    timestamp = post['date']+' 00:00:00'
    posts.append({'id': str(n), 'title': post['title'], 'slug': post['slug'],
                  'html': post['html'], 'type': 'post', 'status': 'published',
                  'visibility': 'public', 'created_at': timestamp,
                  'updated_at': timestamp, 'published_at': timestamp,
                  'custom_excerpt': post['description']})
export = {'meta': {'exported_on': int(datetime.now(timezone.utc).timestamp()*1000),
                   'version': '6.0.0'}, 'data': {'posts': posts}}
out = ROOT/'exports/ghost.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(export, ensure_ascii=False, indent=2)+'\n')
print(f'Exported {len(posts)} post(s) to {out}. Import through Ghost Admin and review before use.')
