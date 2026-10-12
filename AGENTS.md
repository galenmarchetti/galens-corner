# Editing this blog

- `posts/*.md` is the canonical article source. Preserve the author's wording unless asked to edit it.
- Use date-prefixed filenames and unique kebab-case slugs. Required YAML fields: title, date, slug, description.
- `docs/` is generated. Edit `scripts/build.py`, `theme/style.css`, `site.json`, or the post sources; then run `python scripts/build.py`.
- Run `python -m unittest discover -s tests` for build changes.
- Commit generated `docs/` with source changes so Pages stays current.
- This repository is public. Keep private notes, records, credentials, and unrelated material out of it.
- Do not change publication dates or slugs casually; they are stable citation identifiers.
- Ghost exports are optional, generated into ignored `exports/`, and are not a live sync.
