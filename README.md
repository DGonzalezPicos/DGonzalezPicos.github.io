# Darío González Picos — academic website

Static single-page site, dual-hosted:

- **GitHub Pages:** https://dgonzalezpicos.github.io/
- **Leiden:** https://home.strw.leidenuniv.nl/~picos/

Asset links are **relative** (`assets/`, `images/`, `papers/`) so both hosts work without path rewriting.

## Structure

- `index.html` — Summary, About, Research Highlights, Publications
- `assets/site.css` — styles (light default + dark theme toggle)
- `images/` — portrait, logo
- `papers/cv.pdf` — CV

Local backups (gitignored):

- `backup_jekyll_2026-11-17/` — previous Jekyll site
- `backup_hyperspace_2026-07-18/` — earlier Hyperspace theme

## Local preview

```bash
./local_html_site.sh          # http://localhost:8008/~picos/
```

## Publishing to GitHub Pages

```bash
./verify-github-paths.sh      # must pass (no /~picos/ paths)
git add -A
git status
git commit -m "…"
git push origin master
```

Do **not** commit `.env`, `backup_*`, or `academic-website-template/`.
