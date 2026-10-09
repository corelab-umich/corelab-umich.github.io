# CORE Lab website

GitHub Pages-ready Jekyll source for CORE Lab website.

## Standalone development

Requires Ruby 3.3, Bundler, a C/C++ toolchain, and Ruby development headers. Install dependencies and build:

```bash
bundle config set --local path vendor/bundle
bundle install
bundle exec jekyll build
python3 scripts/check_links.py _site
```

When both repositories are available in the shared workspace, run `docker compose up --build` from the workspace root, or use `../scripts/preview.sh` for a native preview. For this repository alone, use `bundle exec jekyll serve --config _config.yml,_config.local.yml`.

## Structure

Pages are HTML/Liquid, preserving the complete article content from 14 pages of the CORE Lab university website. Research figures, portraits, and videos are stored locally under `assets/images/` and `assets/videos/`. Navigation and the shared page wrapper are in `_layouts/default.html`; responsive styles are in `assets/style.css`.

The source-page and media mappings are recorded in `_data/content_sources.json`. Original wording and dates are preserved, including information that may be outdated. Check `CONTENT_REVIEW.md` before editing university-sourced content. The lab has authorized reuse of the existing website text and images.

## GitHub Pages

Intended repository: `corelab-umich/corelab-umich.github.io`. The workflow builds pull requests without deployment, and publishes main-branch pushes once GitHub Pages is enabled with GitHub Actions.

The generated `_site/` directory is ignored. Commit source files and `Gemfile.lock`. Select a code license and a reuse policy for lab-authored material before public release.

## Publications

Monthly discovery proposes additions for review. See `PUBLICATIONS.md` for author verification, scope, configuration, and activation.
