# Darío González Picos — personal website

Live site is the built Jekyll output. Source lives in `academic-website-template/`.
Old Hyperspace site is preserved in `backup_hyperspace_2026-07-18/`.

## Preview / deploy

See `academic-website-template/README_SITE.md`.

```bash
cd academic-website-template
./deploy.sh            # Leiden (baseurl=/~picos) — always run this last
# ./deploy-github.sh   # then commit/push, then ./deploy.sh again
```

If Publications/About return Apache 403 (“unable to read htaccess”), run:

```bash
academic-website-template/fix-web-perms.sh
```

That is caused by `umask 077` making pages unreadable to Apache — not a missing `.htaccess`.
