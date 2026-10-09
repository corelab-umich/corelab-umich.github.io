# CORE Lab website

Local GitHub Pages-ready Jekyll source. No remote is configured and nothing has been published.

## Standalone development

Requires Ruby 3.3, Bundler, a C/C++ toolchain, and Ruby development headers. Install dependencies and build:

```bash
bundle config set --local path vendor/bundle
bundle install
bundle exec jekyll build
python3 scripts/check_links.py _site
```

For the linked local preview, use `../scripts/preview.sh` from the workspace. For this repository alone, use `bundle exec jekyll serve --config _config.yml,_config.local.yml`.

## Structure

Pages are Markdown; the homepage is HTML/Liquid. Shared project summaries live in `_data/projects.yml`, the layout in `_layouts/default.html`, and styles in `assets/style.css`. Check `CONTENT_REVIEW.md` before replacing university content.

## Future GitHub Pages

Intended repository: `corelab-umich/corelab-umich.github.io`. The existing workflow builds pull requests without deployment, and publishes main-branch pushes once GitHub Pages is enabled with GitHub Actions. Confirm repository naming and audience before creating the remote. Review content and remove the local-draft footer when the website is approved.

The generated `_site/` directory is ignored. Commit source files and `Gemfile.lock`. Code/theme licensing and permission to republish lab content should be selected by the lab before public release; no license for CORE material has been assumed.
