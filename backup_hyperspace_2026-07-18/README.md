# Darío González Picos — Personal Website

Static personal site hosted from this directory.

## Local preview

```bash
python3 -m http.server 8008
```

Then open `http://localhost:8008`.

## CV updates from ADS

```bash
cp .env.template .env   # add ADS_API_TOKEN
python3 update_resume_from_ads.py
```

## Main pages

- `index.html` — homepage
- `isotope_ratios.html` — isotope ratio measurements table
- `isotope_ratios_viewer.html` — raw CSV viewer
- `assets/resume.pdf` — CV (generated from `assets/resume.tex`)
