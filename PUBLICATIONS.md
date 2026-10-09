# Publication discovery

The existing CORE Lab bibliography is preserved in `publications.html`. New citations are stored in `_data/publications.json` and shown before that archive, with the latest three also shown on Research output. Discovery uses OpenAlex author identities; it does not scrape name matches or update patents and invited talks.

## Schedule and activation

`.github/workflows/publications.yml` runs monthly on the third at 10:23 UTC and supports manual runs. Once this repository is pushed, enable Actions and allow Actions to create pull requests in repository settings. A successful run with additions opens a review pull request; it never merges or deploys them. An existing publication-update PR pauses additional discovery until it is reviewed. The generated report accompanies the PR.

Standard GitHub-hosted runners are free for public repositories. Private repositories use the account's included minutes and billing rules. Monthly runs are the default regardless of cost. See https://docs.github.com/en/billing/concepts/product-billing/github-actions.

Optionally set the repository Actions secret `OPENALEX_API_KEY` for a larger free API allowance. The script passes it as a Bearer header and does not store it in source or output. See https://help.openalex.org/api/authentication/.

## Authors and lab scope

`_data/authors.json` contains 22 verified identities: the faculty member, eight listed current students, and thirteen PhD alumni. Nineteen have verified ORCID identifiers; Aleksandra Dudek, Ashley Ortenburg, and Diego Ramirez-Gomez use verified OpenAlex author IDs. Verification links and dates are included in each record. The roster reflects the recovered website; confirm current membership before expanding discovery.

Only faculty/current students are enabled initially. Alumni are retained but disabled. Set `enabled` per author and optional `from_date`/`to_date` membership dates (YYYY-MM-DD). Dates are unset rather than guessed.

`_data/publication_sync.json` starts discovery at January 1, 2025, avoiding wholesale re-import of the historical archive. Its initial coauthor requirement limits candidates to papers with Christopher Vermillion's ORCID. This conservative rule may omit valid lab work without the PI; the lab can remove or change it after reviewing its scope. ORCID queries are preferred over a single OpenAlex author ID because an author's records can be split across identities.

## Local use

```bash
python3 -m unittest discover -s tests -v
python3 scripts/sync_publications.py --report publication-review.md
bundle exec jekyll build
python3 scripts/check_links.py _site
```

The script fetches all enabled identities before writing. A failed request leaves the existing data untouched. Empty/no-change runs do not rewrite it. Existing reviewed entries, including manual corrections and fields, are retained even if an API record disappears.

## Review additions

Check author identity, lab relevance, publisher title, DOI, venue, and online/issue year. OpenAlex metadata can contain formatting errors or assign an online year different from the journal issue. Six initial candidates were discovered locally; verify them before publishing.

Deduplication uses DOI, normalized title, and OpenAlex work ID, including titles in the legacy bibliography. A published version is preferred to a same-title preprint within a run. Different-title versions may require manual resolution. Retracted, future-dated, and out-of-scope records are excluded.

Correct titles/venues directly in `_data/publications.json`. To reject an entry permanently, add its DOI, OpenAlex ID, or title to the appropriate `exclude` list in `_data/publication_sync.json` and remove the rejected entry from the data file. Merely deleting it can cause rediscovery. Preserve manual corrections in a review commit.

The nine unit tests cover pagination, duplicate handling, scope, exclusions, publication/preprint preference, retained corrections, atomic/no-change writes, and failed-fetch preservation.
