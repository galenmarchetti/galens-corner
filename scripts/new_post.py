#!/usr/bin/env python3
"""Create a Markdown essay: python scripts/new_post.py 'Post title'."""
from datetime import date
from pathlib import Path
import argparse
import re
import yaml

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('title')
args = parser.parse_args()
slug = re.sub(r'[^a-z0-9]+', '-', args.title.lower()).strip('-')
if not slug:
    parser.error('Title must contain at least one ASCII letter or number')
path = Path(__file__).resolve().parents[1] / 'posts' / f'{date.today()}-{slug}.md'
metadata = {'title': args.title, 'date': date.today().isoformat(), 'slug': slug,
            'author': 'Galen Marchetti', 'description': 'Add a short description.',
            'tags': [], 'draft': True}
with path.open('x', encoding='utf-8') as f:
    f.write('---\n'+yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True)+'---\n\nWrite your essay here.\n')
print(path)
