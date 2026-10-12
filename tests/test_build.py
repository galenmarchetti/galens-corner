import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build import ROOT, build, read_posts

class BlogBuildTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for folder in ('posts', 'theme'):
            shutil.copytree(ROOT/folder, self.root/folder)
        shutil.copyfile(ROOT/'site.json', self.root/'site.json')
    def tearDown(self):
        self.temp.cleanup()
    def test_markdown_preserved_and_indexes_agree(self):
        posts = build(self.root)
        index = json.loads((self.root/'docs/index.json').read_text())['posts']
        rss = ET.parse(self.root/'docs/feed.xml').findall('./channel/item')
        self.assertEqual(len(posts), len(index))
        self.assertEqual(len(posts), len(rss))
        for p, entry, item in zip(posts, index, rss):
            self.assertEqual((self.root/'docs/posts'/p['filename']).read_bytes(), (self.root/'posts'/p['filename']).read_bytes())
            self.assertEqual(entry['url'], item.findtext('link'))
            self.assertIn('/galens-corner/essays/', entry['url'])
            html = (self.root/'docs/essays'/p['slug']/'index.html').read_text()
            self.assertIn(entry['markdown_url'], html)
            self.assertIn(p['html'], html)
    def test_draft_absent_and_stale_output_removed(self):
        build(self.root)
        p = next((self.root/'posts').glob('*.md'))
        p.write_text(p.read_text().replace('draft: false', 'draft: true'))
        build(self.root)
        for path in (self.root/'docs').rglob('*'):
            if path.is_file():
                self.assertNotIn('Sentience',path.read_text())
        self.assertFalse((self.root/'docs/essays/sentience/index.html').exists())
    def test_slug_cannot_escape_output_directory(self):
        p=next((self.root/'posts').glob('*.md'))
        p.write_text(p.read_text().replace('slug: sentience','slug: ../../elsewhere'))
        with self.assertRaises(ValueError):
            read_posts(self.root)

if __name__ == '__main__':
    unittest.main()
