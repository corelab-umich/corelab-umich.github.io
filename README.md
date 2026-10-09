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

Pages are Markdown, including all four research areas, faculty biography, and prospective-student guidance; the homepage is HTML/Liquid. Research navigation and dated news are editable in `_data/research.yml` and `_data/news.yml`. Shared project summaries live in `_data/projects.yml`, the layout in `_layouts/default.html`, and styles in `assets/style.css`. Check `CONTENT_REVIEW.md` when updating university-sourced content.

## GitHub Pages

Intended repository: `corelab-umich/corelab-umich.github.io`. The workflow builds pull requests without deployment, and publishes main-branch pushes once GitHub Pages is enabled with GitHub Actions. Review content and remove the local-draft footer when the website is approved.

The generated `_site/` directory is ignored. Commit source files and `Gemfile.lock`. Code/theme licensing and permission to republish lab content should be selected by the lab before public release; no license for CORE material has been assumed.
