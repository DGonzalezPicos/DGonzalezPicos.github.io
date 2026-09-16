# Darío González Picos — personal website

Live site is the built Jekyll output. Source lives in `academic-website-template/`.
Old Hyperspace site is preserved in `backup_hyperspace_2026-07-18/`.

## Preview / deploy

See `academic-website-template/README_SITE.md`.

```bash
cd academic-website-template
./deploy-github.sh    # GitHub-shaped HTML (/assets/...) — commit/push only this
git add -u && git commit && git push
./deploy.sh           # Leiden (/~picos/...) + Apache perms — local only, do not commit
```

After `./deploy.sh`, `git status` will look dirty (URL prefixes differ). That is normal.
Do **not** commit that tree — the pre-commit hook blocks `/~picos/` paths so GitHub Pages CSS does not break.

If Publications/About return Apache 403 (“unable to read htaccess”), run:

```bash
./fix-web-perms.sh
```
