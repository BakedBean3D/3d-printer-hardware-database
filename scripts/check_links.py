#!/usr/bin/env python3
"""Check every URL cited in the database (sources, datasheet_url, notes).

Stdlib only. HEAD request per unique URL (GET fallback on 405), ~10 s
timeout, a couple of retries. Vendor sites commonly block bots: 403/429
count as "alive but unverifiable", never dead. Only confirmed-dead links
(404/410, DNS failure, or repeated connection failure) are reported.

Usage: python3 scripts/check_links.py [--output dead-links.md]
Writes the markdown report only when dead links were found; always exits 0
(the weekly workflow is informational and must never block anything).
"""
import glob
import os
import re
import sys
import time
import urllib.error
import urllib.request

import yaml

ROOT = os.path.join(os.path.dirname(__file__), "..")
CATEGORIES = ["motors", "hotends", "extruders", "probes", "toolheads",
              "controller_boards", "psu"]
# Parens stay in the class — real citation URLs contain them (Mean Well
# .../UHP-350(R)/...); _clean strips the unbalanced trailing ones instead.
URL_RE = re.compile(r"https?://[^\s'\"<>\[\]{}]+")
TIMEOUT = 10
RETRIES = 2
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; hardware-db-link-check)"}


def collect_urls():
    """url -> sorted list of 'file[entry_id]' citations."""
    found = {}

    def _clean(url):
        url = url.rstrip(".,;:")
        # a URL cited inside a parenthetical drags the closing paren along
        while url.endswith(")") and url.count("(") < url.count(")"):
            url = url[:-1].rstrip(".,;:")
        return url

    def add(url, where):
        found.setdefault(_clean(url), set()).add(where)

    for cat in CATEGORIES:
        for path in sorted(glob.glob(os.path.join(ROOT, cat, "*.yaml"))):
            rel = os.path.relpath(path, ROOT)
            with open(path) as f:
                data = yaml.safe_load(f) or []
            for entry in data:
                if not isinstance(entry, dict):
                    continue
                where = f"{rel}[{entry.get('id')}]"
                for field in ("datasheet_url", "notes"):
                    v = entry.get(field)
                    if isinstance(v, str):
                        for url in URL_RE.findall(v):
                            add(url, where)
                for v in entry.get("sources") or []:
                    if isinstance(v, str):
                        for url in URL_RE.findall(v):
                            add(url, where)
    return {u: sorted(w) for u, w in found.items()}


def check(url):
    """-> (status, detail); status in {'alive', 'unverifiable', 'dead'}."""
    method = "HEAD"
    last = None
    for attempt in range(RETRIES + 1):
        req = urllib.request.Request(url, method=method, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return "alive", str(resp.status)
        except urllib.error.HTTPError as e:
            # 403/429/401: bot-blocked. 414: server quirk on HEAD (seen on
            # wiki.fysetc.com, which serves the pages fine in a browser).
            if e.code in (403, 429, 401, 414):
                return "unverifiable", f"HTTP {e.code}"
            if e.code == 405 and method == "HEAD":
                method = "GET"
                continue
            if e.code in (404, 410):
                return "dead", f"HTTP {e.code}"
            last = f"HTTP {e.code}"
        except Exception as e:  # URLError, timeout, ConnectionReset, ...
            last = f"{type(e).__name__}: {e}"
        time.sleep(1 + attempt)
    return "dead", last or "unknown failure"


def main():
    output = None
    if "--output" in sys.argv:
        output = sys.argv[sys.argv.index("--output") + 1]

    urls = collect_urls()
    print(f"checking {len(urls)} unique URLs...")
    dead, unverifiable = [], 0
    for url, cited_by in sorted(urls.items()):
        status, detail = check(url)
        if status == "dead":
            dead.append((url, detail, cited_by))
            print(f"  DEAD ({detail}): {url}")
        elif status == "unverifiable":
            unverifiable += 1
    print(f"done: {len(dead)} dead, {unverifiable} unverifiable (treated alive), "
          f"{len(urls) - len(dead) - unverifiable} alive")

    if dead and output:
        with open(output, "w") as f:
            f.write("Weekly link check found dead citation URLs. "
                    "403/429 (bot-blocked) links are NOT listed — only "
                    "confirmed failures.\n\n")
            for url, detail, cited_by in dead:
                f.write(f"- `{url}` — {detail}\n")
                for w in cited_by:
                    f.write(f"  - cited by {w}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
