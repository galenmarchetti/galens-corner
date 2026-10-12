#!/usr/bin/env python3
"""Build a static blog and machine-readable copies from posts/*.md."""
from datetime import date, datetime, timezone
from email.utils import format_datetime
from html import escape
from pathlib import Path
import argparse
import json
import re
import shutil
import xml.etree.ElementTree as ET

from markdown_it import MarkdownIt
import yaml

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN = MarkdownIt('commonmark', {'html': True})

def read_posts(root=ROOT):
    posts = []
    seen = set()
    for path in sorted((root / 'posts').glob('*.md')):
        raw = path.read_text(encoding='utf-8')
        if not raw.startswith('---\n'):
            raise ValueError(f'{path.name}: YAML frontmatter required')
        _, front, body = raw.split('---\n', 2)
        meta = yaml.safe_load(front)
        if meta.get('draft', False):
            continue
        for field in ('title', 'date', 'slug', 'description'):
            if not meta.get(field):
                raise ValueError(f'{path.name}: missing {field}')
        slug = meta['slug']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or slug in seen:
            raise ValueError(f'{path.name}: invalid or duplicate slug')
        seen.add(slug)
        published = date.fromisoformat(str(meta['date']))
        posts.append(dict(meta, date=published.isoformat(), body=body.strip(), raw=raw,
                          filename=path.name, html=MARKDOWN.render(body.strip())))
    return sorted(posts, key=lambda p: (p['date'], p['slug']), reverse=True)

def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def build(root=ROOT, url_override=None):
    config = json.loads((root / 'site.json').read_text())
    base = (url_override or config['url']).rstrip('/')
    out = root / 'docs'
    if out.exists():
        shutil.rmtree(out)  # docs/ is generated; handwritten files live elsewhere.
    out.mkdir()
    posts = read_posts(root)
    def page(title, description, content, path='', extra=''):
        url = base + '/' + path
        page_title = title if title == config['title'] else title + ' — ' + config['title']
        return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(page_title)}</title>
<meta name="description" content="{escape(description, quote=True)}">
<link rel="canonical" href="{url}"><link rel="stylesheet" href="{base}/style.css">
<link rel="alternate" type="application/rss+xml" title="RSS" href="{base}/feed.xml">
<meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{url}">{extra}
</head><body><a class="skip" href="#content">Skip to content</a>
<header class="site-header"><a class="wordmark" href="{base}/">{escape(config['title'])}<span> / </span></a><nav aria-label="Main"><a href="{base}/">Essays</a><a href="{config['substack']}">Substack ↗</a><a href="{config['repository']}">GitHub ↗</a></nav></header>
<main id="content">{content}</main>
<footer><span>© {date.today().year} {escape(config['author'])}</span><div><a href="{base}/feed.xml">RSS</a><a href="{base}/llms.txt">For AI readers</a><a href="{config['repository']}">Source</a></div></footer>
</body></html>'''
    items = []
    index = []
    llms = [f"# {config['title']}\n\n> {config['description']}\n\nEssays by {config['author']}. Full text is available without JavaScript or authentication.\n\n## Indexes\n\n- [JSON post index]({base}/index.json)\n- [All essays in Markdown]({base}/llms-full.txt)\n- [RSS feed]({base}/feed.xml)\n\n## Essays\n"]
    full = [f"# {config['title']}\n"]
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')
    for key, value in [('title', config['title']), ('link', base+'/'), ('description', config['description'])]:
        ET.SubElement(channel, key).text = value
    sitemap = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
    ET.SubElement(ET.SubElement(sitemap, 'url'), 'loc').text = base+'/'
    for p in posts:
        path = f"essays/{p['slug']}/"
        url = base+'/'+path
        mdurl = f"{base}/posts/{p['filename']}"
        published = datetime.fromisoformat(p['date']).replace(tzinfo=timezone.utc)
        date_label = published.strftime('%B %d, %Y').replace(' 0', ' ')
        word_count = len(re.findall(r'\b\w+\b', p['body']))
        minutes = max(1, round(word_count/220))
        original = f'<a href="{escape(p["original_url"], quote=True)}">Read on Substack ↗</a>' if p.get('original_url') else ''
        content = f'''<article><header class="article-header"><a class="back" href="{base}/">← All essays</a><p class="eyebrow"><time datetime="{p['date']}">{date_label}</time> · {minutes} min read</p><h1>{escape(p['title'])}</h1><p class="subtitle">{escape(p['description'])}</p><p class="byline">{escape(p.get('author', config['author']))}</p></header><div class="prose">{p['html']}</div><aside class="article-links"><a href="{mdurl}">Read as Markdown</a>{original}</aside></article>'''
        write(out/path/'index.html', page(p['title'], p['description'], content, path, '<meta property="og:type" content="article">'))
        write(out/'posts'/p['filename'], p['raw'])
        items.append(f'''<li><div class="entry-meta"><time datetime="{p['date']}">{date_label}</time><span>{minutes} min read</span></div><div><h2><a href="{url}">{escape(p['title'])}<span aria-hidden="true"> ↗</span></a></h2><p>{escape(p['description'])}</p></div></li>''')
        index.append({k:p[k] for k in ('title','slug','date','description')} | {'url':url,'markdown_url':mdurl,'source_url':config['repository']+'/blob/main/posts/'+p['filename']})
        llms.append(f"- [{p['title']}]({mdurl}): {p['description']} ({p['date']})")
        full.append(f"\n---\n\n# {p['title']}\n\n{p['description']}\n\n{p['date']} · {config['author']}\n\nSource: {url}\n\n{p['body']}\n")
        item = ET.SubElement(channel, 'item')
        for key,value in [('title',p['title']),('link',url),('guid',url),('pubDate',format_datetime(published)),('description',p['html'])]:
            ET.SubElement(item,key).text=value
        entry = ET.SubElement(sitemap, 'url')
        ET.SubElement(entry, 'loc').text=url
        ET.SubElement(entry, 'lastmod').text=p['date']
    home = f'''<section class="intro"><p class="eyebrow">A notebook in public</p><h1>Questions worth<br><em>sitting with.</em></h1><p>{escape(config['description'])}</p><div class="intro-signature">By {escape(config['author'])}</div></section><section class="essays" aria-labelledby="essays-title"><div class="section-heading"><h2 id="essays-title">Essays</h2><span>{len(posts):02d}</span></div><ol class="essay-list">{''.join(items)}</ol></section>'''
    write(out/'index.html',page(config['title'],config['description'],home))
    write(out/'404.html',page('Page not found','This page does not exist.',f'<h1>Page not found.</h1><p><a href="{base}/">Return to the essays →</a></p>','404.html'))
    write(out/'index.json',json.dumps({'title':config['title'],'posts':index},ensure_ascii=False,indent=2)+'\n')
    write(out/'llms.txt','\n'.join(llms)+'\n')
    write(out/'llms-full.txt','\n'.join(full).rstrip()+'\n')
    write(out/'feed.xml',ET.tostring(rss,encoding='unicode',xml_declaration=True))
    write(out/'sitemap.xml',ET.tostring(sitemap,encoding='unicode',xml_declaration=True))
    write(out/'robots.txt',f'User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n')
    write(out/'.nojekyll','')
    shutil.copyfile(root/'theme/style.css',out/'style.css')
    print(f'Built {len(posts)} post(s) into {out}')
    return posts

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', help='Override site URL for a local preview build')
    build(url_override=parser.parse_args().url)
