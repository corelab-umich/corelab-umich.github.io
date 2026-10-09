#!/usr/bin/env python3
"""Discover new CORE publications; write candidates for a reviewed Git update."""
import argparse
import datetime as dt
import html
import json
import os
from pathlib import Path
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]


def title_key(value):
    value = unicodedata.normalize('NFKD', html.unescape(value)).casefold()
    return ''.join(c for c in value if c.isalnum())


def doi_key(value):
    value = urllib.parse.unquote(value or '').strip().lower()
    return re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '', value)


def orcid_key(value):
    return (value or '').rstrip('/').rsplit('/', 1)[-1]


class Paragraphs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.current = None
        self.paragraphs = []

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.current = []

    def handle_data(self, data):
        if self.current is not None:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == 'p' and self.current is not None:
            self.paragraphs.append(''.join(self.current))
            self.current = None


def legacy_titles(source):
    parser = Paragraphs()
    parser.feed(source)
    return {title_key(match.group(1)) for p in parser.paragraphs
            for match in [re.search(r'[“"](.+?)[”"]', p)] if match}


def atomic_json(path, value):
    text = json.dumps(value, ensure_ascii=False, indent=2) + '\n'
    if path.exists() and path.read_text() == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(text)
    temporary.replace(path)
    return True


class OpenAlex:
    def __init__(self):
        self.headers = {'Accept': 'application/json', 'User-Agent': 'CORELab-Publications/1.0'}
        key = os.environ.get('OPENALEX_API_KEY')
        if key:
            self.headers['Authorization'] = 'Bearer ' + key

    def get(self, params):
        url = 'https://api.openalex.org/works?' + urllib.parse.urlencode(params)
        for attempt in range(4):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers=self.headers), timeout=30) as response:
                    return json.load(response)
            except urllib.error.HTTPError as error:
                if error.code not in (429, 500, 502, 503, 504) or attempt == 3:
                    raise RuntimeError(f'OpenAlex request failed (HTTP {error.code}); publication data was not written.') from None
            except (urllib.error.URLError, TimeoutError):
                if attempt == 3:
                    raise RuntimeError('OpenAlex connection failed; publication data was not written.') from None
            time.sleep(2 ** attempt)

    def works(self, author, start_date):
        if author.get('orcid'):
            selector = 'authorships.author.orcid:https://orcid.org/' + orcid_key(author['orcid'])
        elif author.get('openalex_id'):
            identifier = author['openalex_id'].rsplit('/', 1)[-1]
            selector = 'authorships.author.id:' + identifier
        else:
            raise ValueError(f"Enabled author {author['name']} has no verified identifier")
        filters = [selector, 'from_publication_date:' + start_date]
        if author.get('from_date'):
            filters.append('from_publication_date:' + max(start_date, author['from_date']))
            filters.pop(1)
        if author.get('to_date'):
            filters.append('to_publication_date:' + author['to_date'])
        params = {'filter': ','.join(filters), 'sort': 'publication_date:desc', 'per_page': 100, 'cursor': '*'}
        results, seen = [], set()
        while True:
            data = self.get(params)
            if not isinstance(data.get('results'), list):
                raise ValueError('OpenAlex response has no results list')
            results.extend(data['results'])
            cursor = data.get('meta', {}).get('next_cursor')
            if not data['results'] or not cursor:
                break
            if cursor in seen:
                raise ValueError('OpenAlex returned a repeated cursor')
            seen.add(cursor)
            params['cursor'] = cursor
        return results


def safe_url(value):
    return value if value and urllib.parse.urlsplit(value).scheme in ('https', 'http') else None


def eligible(work, config, today):
    if work.get('type') not in config['types'] or work.get('is_retracted'):
        return False
    date = work.get('publication_date')
    if not date or date < config['from_date'] or date > today:
        return False
    excluded = config.get('exclude', {})
    if work['id'] in excluded.get('openalex_ids', []) or doi_key(work.get('doi')) in {doi_key(x) for x in excluded.get('dois', [])}:
        return False
    if title_key(work.get('display_name', '')) in {title_key(x) for x in excluded.get('titles', [])}:
        return False
    anchor = config.get('required_coauthor_orcid')
    if anchor and not any(orcid_key(a.get('author', {}).get('orcid')) == orcid_key(anchor) for a in work.get('authorships', [])):
        return False
    return bool(work.get('display_name'))


def entry(work):
    location = work.get('primary_location') or {}
    venue = location.get('source') or {}
    biblio = work.get('biblio') or {}
    doi = doi_key(work.get('doi'))
    authors = [a['author']['display_name'] for a in work.get('authorships', []) if a.get('author', {}).get('display_name')]
    return {'id': work['id'], 'doi': doi or None, 'title': work['display_name'],
            'authors': authors, 'year': work['publication_year'], 'date': work['publication_date'],
            'type': work['type'], 'venue': venue.get('display_name') or '',
            'volume': biblio.get('volume'), 'issue': biblio.get('issue'),
            'pages': '–'.join(dict.fromkeys(str(x) for x in [biblio.get('first_page'), biblio.get('last_page')] if x)),
            'url': ('https://doi.org/' + doi) if doi else safe_url(location.get('landing_page_url')) or work['id']}


def discover(works, existing, legacy, config, today):
    # Retain reviewed entries, including manual corrections and items absent from a later API response.
    result = list(existing)
    ids = {e['id'] for e in existing}
    dois = {doi_key(e.get('doi')) for e in existing if e.get('doi')}
    titles = legacy | {title_key(e['title']) for e in existing}
    added = []
    # Prefer published records over preprints of the same title.
    works = sorted(works, key=lambda w: (w.get('type') == 'preprint', not bool(w.get('doi')), w['id']))
    for work in works:
        if not eligible(work, config, today):
            continue
        doi, title = doi_key(work.get('doi')), title_key(work['display_name'])
        if work['id'] in ids or (doi and doi in dois) or title in titles:
            continue
        record = entry(work)
        result.append(record)
        added.append(record)
        ids.add(record['id']); titles.add(title)
        if doi:
            dois.add(doi)
    result.sort(key=lambda e: (e['date'], e['title']), reverse=True)
    return result, added


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '_data/publications.json')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--offline', type=Path, help='Use a JSON array of OpenAlex works instead of network requests')
    args = parser.parse_args(argv)
    roster = json.loads((ROOT / '_data/authors.json').read_text())
    config = json.loads((ROOT / '_data/publication_sync.json').read_text())
    legacy = legacy_titles((ROOT / 'publications.html').read_text())
    existing = json.loads(args.output.read_text()) if args.output.exists() else []
    if args.offline:
        works = json.loads(args.offline.read_text())
    else:
        client, works = OpenAlex(), []
        for author in roster:
            if author['enabled']:
                works.extend(client.works(author, config['from_date']))
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    result, added = discover(works, existing, legacy, config, today)
    changed = atomic_json(args.output, result)
    lines = ['# Publication update review', '',
             f'{len(added)} new records discovered. Existing bibliography entries and reviewed additions are preserved.', '',
             'Check author identity, lab relevance, citation metadata, duplicates with altered titles, and preprint/published versions before merging.', '',
             'To reject a record permanently, remove it from `_data/publications.json` and add its DOI or OpenAlex ID to `_data/publication_sync.json` → `exclude`.', '']
    for record in sorted(added, key=lambda e: e['date'], reverse=True):
        lines.extend([f"- **{record['title']}** ({record['year']})", f"  Authors: {', '.join(record['authors'])}", f"  Venue: {record['venue'] or 'Not supplied'}; {record['url']}"])
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text('\n'.join(lines) + '\n')
    print(f"Fetched {len(works)} records; added {len(added)}; retained {len(existing)} reviewed additions; data {'changed' if changed else 'unchanged'}.")


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, ValueError, KeyError, OSError) as error:
        print(f'Publication sync failed: {error}', file=sys.stderr)
        sys.exit(1)
