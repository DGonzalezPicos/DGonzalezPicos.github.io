#!/usr/bin/env python3
"""Fetch publication stats from NASA ADS and update resume.tex."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"
RESUME_TEX = ROOT / "assets" / "resume.tex"

ADS_QUERY = 'author:"González Picos, D.; Picos, Darío González"'
ADS_SEARCH_URL = "https://api.adsabs.harvard.edu/v1/search/query"
SELECTED_BIBCODES = {
    "2025NatAs...9.1692G",
    "2025A&A...703A..65G",
    "2025A&A...693A.298G",
    "2024AJ....168..246Z",
    "2024A&A...689A.212G",
}


def load_env(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}. Copy .env.template to .env and set ADS_API_TOKEN.")
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def ads_search(token: str, rows: int = 100) -> list[dict]:
    params = urllib.parse.urlencode(
        {
            "q": ADS_QUERY,
            "sort": "date desc",
            "rows": rows,
            "fl": "title,author,bibcode,pub,year,doi,citation_count,property,identifier",
        }
    )
    request = urllib.request.Request(
        f"{ADS_SEARCH_URL}?{params}",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    return payload["response"]["docs"]


def is_refereed(doc: dict) -> bool:
    props = doc.get("property", [])
    return "REFEREED" in props and "NOT REFEREED" not in props


def arxiv_id(doc: dict) -> str | None:
    for ident in doc.get("identifier", []):
        if ident.startswith("arXiv:"):
            return ident.replace("arXiv:", "")
    for doi in doc.get("doi", []):
        if "arxiv" in doi.lower():
            return doi.split("arXiv.")[-1]
    bibcode = doc.get("bibcode", "")
    if bibcode.startswith("20") and "arXiv" in bibcode:
        match = re.search(r"arXiv(\d{4}\.\d{4,5})", bibcode)
        if match:
            return match.group(1)
    return None


def fetch_stats(token: str) -> dict:
    docs = ads_search(token)
    refereed = [doc for doc in docs if is_refereed(doc)]
    return {
        "date": date.today().isoformat(),
        "total_entries": len(docs),
        "refereed_papers": len(refereed),
        "total_citations": sum(doc.get("citation_count", 0) for doc in docs),
        "refereed_citations": sum(doc.get("citation_count", 0) for doc in refereed),
        "citations_by_bibcode": {doc["bibcode"]: doc.get("citation_count", 0) for doc in docs},
    }


def update_summary_line(tex: str, stats: dict) -> str:
    lines = tex.splitlines()
    updated = False
    cleaned: list[str] = []
    for line in lines:
        if line.startswith("As of ") or line.startswith("ootnote{Publication data collected from NASA Astrophysics Data System}"):
            if updated:
                continue
            line = (
                f"As of {stats['date']}, part of {stats['refereed_papers']} refereed papers with "
                f"{stats['total_citations']} total citations; "
                r"a complete listing can be found in my \href{https://ui.adsabs.harvard.edu/search/p_=0&q=author%3A%22Gonz%C3%A1lez%20Picos%2C%20D.%3B%20Picos%2C%20Dar%C3%ADo%20Gonz%C3%A1lez%22&sort=date%20desc%2C%20bibcode%20desc}{ADS} or "
                r"\href{https://orcid.org/0000-0001-9282-9462}{ORCID}."
            )
            updated = True
        cleaned.append(line)
    return "\n".join(cleaned) + ("\n" if tex.endswith("\n") else "")


def update_citation_tags(tex: str, citations: dict[str, int]) -> str:
    bibcode_to_arxiv = {
        "2025NatAs...9.1692G": "2508.18424",
        "2025A&A...703A..65G": "2509.11694",
        "2025A&A...693A.298G": "2501.01789",
        "2024AJ....168..246Z": "2409.16660",
        "2024A&A...689A.212G": "2407.07678",
    }
    for bibcode, arxiv in bibcode_to_arxiv.items():
        count = citations.get(bibcode)
        if count is None:
            continue
        tex = re.sub(
            rf"\(arXiv:{re.escape(arxiv)}\) \[\d+ citations\]",
            f"(arXiv:{arxiv}) [{count} citations]",
            tex,
        )
    return tex


def update_last_updated(tex: str, stats: dict) -> str:
    formatted = date.fromisoformat(stats["date"]).strftime("%B %d, %Y")
    return re.sub(r"Last updated: [^\n]+", f"Last updated: {formatted}", tex)


def compile_resume() -> None:
    assets_dir = RESUME_TEX.parent
    for _ in range(2):
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", RESUME_TEX.name],
            cwd=assets_dir,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    for suffix in (".aux", ".log", ".out"):
        path = assets_dir / f"resume{suffix}"
        if path.exists():
            path.unlink()


def main() -> int:
    load_env(ENV_FILE)
    token = os.environ.get("ADS_API_TOKEN")
    if not token:
        print("ADS_API_TOKEN is not set.", file=sys.stderr)
        return 1

    stats = fetch_stats(token)
    tex = RESUME_TEX.read_text()
    tex = update_summary_line(tex, stats)
    tex = update_citation_tags(tex, stats["citations_by_bibcode"])
    tex = update_last_updated(tex, stats)
    RESUME_TEX.write_text(tex)
    compile_resume()

    print(
        f"Updated resume: {stats['refereed_papers']} refereed papers, "
        f"{stats['total_citations']} total citations (ADS, {stats['date']})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
