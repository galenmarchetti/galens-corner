# Galen’s Corner

Essays by Galen Marchetti. Plain Markdown is the source of truth; a small Python build produces a static reading site and machine-readable feeds.

**[Read the blog](https://galenmarchetti.github.io/galens-corner/)** · [Substack](https://galenmarchetti.substack.com/) · [Essays as Markdown](posts/)

## For AI readers

No login, client-side rendering, or API key is needed.

- [Post index (JSON)](https://galenmarchetti.github.io/galens-corner/index.json): titles, dates, descriptions, HTML URLs, and Markdown URLs.
- [llms.txt](https://galenmarchetti.github.io/galens-corner/llms.txt): lightweight discovery index.
- [llms-full.txt](https://galenmarchetti.github.io/galens-corner/llms-full.txt): every published essay in one response.
- [RSS](https://galenmarchetti.github.io/galens-corner/feed.xml): full rendered articles.
- Raw GitHub: `https://raw.githubusercontent.com/galenmarchetti/galens-corner/main/posts/<filename>.md`.

Start with `index.json`, then fetch each `markdown_url`. The website serves byte-for-byte copies of the source Markdown, including frontmatter. `llms.txt` is a convenience index, not a guarantee that every crawler will discover or use it.

## Write and publish

Requires Python 3.10+.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/new_post.py "My next essay"
```

Edit the new file in `posts/`. The frontmatter contains `title`, `date`, `slug`, `author`, `description`, `tags`, and `draft`. Keep the body in Markdown; the page template supplies the title and byline. Set `draft: false` when ready.

```sh
python scripts/build.py
python -m unittest discover -s tests
git add posts docs
git commit -m "Publish essay"
git push
```

GitHub Pages publishes `main:/docs` on push. **Run the build before committing** so the site and Markdown sources stay in sync. No custom Actions workflow, hosting account, or secrets are required. `docs/` is entirely generated and replaced on each build. A draft is omitted from the site and feeds, but any file committed to this public repository is still public on GitHub.

Preview locally with production subpaths:

```sh
python scripts/build.py --url http://localhost:8000/galens-corner
mkdir -p /tmp/galens-corner-preview
ln -sfn "$PWD/docs" /tmp/galens-corner-preview/galens-corner
python -m http.server 8000 --directory /tmp/galens-corner-preview
```

Open `http://localhost:8000/galens-corner/`. Run `python scripts/build.py` again before committing to restore production URLs.

## Structure

```text
posts/              Canonical Markdown essays, with YAML frontmatter
scripts/build.py    Generates the website, RSS, JSON, sitemap, and LLM indexes
scripts/new_post.py Creates a new draft
scripts/export_ghost.py  Produces a Ghost JSON import file
site.json           Publication metadata, URLs, and repository settings
theme/style.css     Reading-site design
requirements.txt    Pinned build dependencies
tests/              Content preservation and publishing checks
docs/               Generated GitHub Pages output (committed)
```

## Ghost portability

For the **Ghost blogging platform**, run:

```sh
python scripts/export_ghost.py
```

Import `exports/ghost.json` with Ghost Admin's content import facility. This follows [Ghost's documented custom JSON migration format](https://docs.ghost.org/migration/custom), using HTML generated from the same Markdown. It preserves titles, slugs, publication dates, descriptions, links, and emphasis. It is a one-time migration helper, not bidirectional synchronization. No live Ghost import has been tested; review the result and author assignment in Ghost. Ghost may normalize HTML during import. Keep Markdown here as the editing source of truth.

Ghostty is a terminal emulator; these CLI commands can also be run there, with no integration required.

## Hosting elsewhere or using a custom domain

Any static host can serve `docs/`. Change `site.json`'s `url` and rebuild. For a custom GitHub Pages domain, also configure the domain and DNS in GitHub's Pages settings. See [GitHub Pages publishing documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## Content

- [Sentience](posts/2026-10-03-sentience.md), October 3, 2026. Originally published on [Substack](https://galenmarchetti.substack.com/p/sentience).

Copyright © Galen Marchetti. Public availability does not grant a redistribution license.
