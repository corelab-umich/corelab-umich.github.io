"""Check generated local HTML links, assets, and fragment targets without network access."""
import sys
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(); self.links=[]; self.ids=set(); self.feed(path.read_text())
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.add(a['id'])
        for attr in ['href','src']:
            if attr in a: self.links.append(a[attr])
root=Path(sys.argv[1]).resolve()
base=sys.argv[2].rstrip('/') if len(sys.argv)>2 else ''
pages={p:Page(p) for p in root.rglob('*.html')}; errors=[]
for path,page in pages.items():
    for link in page.links:
        u=urlsplit(link)
        if u.scheme or u.netloc: continue
        url=unquote(u.path)
        if url.startswith('/'):
            if base:
                if url==base: url='/'
                elif url.startswith(base+'/'): url=url[len(base):]
                else: continue # link to sibling lab website
            elif url.startswith('/lab-manual') and not (root/'lab-manual').exists(): continue # sibling documentation site
            target=root/url.lstrip('/')
        else: target=path.parent/url if url else path
        target=target.resolve()
        if target.is_dir(): target=target/'index.html'
        if not target.exists(): errors.append(f'{path.relative_to(root)}: missing {link}')
        elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:
            errors.append(f'{path.relative_to(root)}: missing fragment {link}')
if errors: print('\n'.join(sorted(set(errors)))); sys.exit(1)
print(f'Checked {len(pages)} HTML pages: local links and fragments pass.')
