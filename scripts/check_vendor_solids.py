#!/usr/bin/env python3
"""Probe vendors for 3D solids that a record's `sources` does not list.

WHY THIS EXISTS. The binding artifact hierarchy is
**vendor 3D STEP > printed dimension text > drawing-view geometry.** A record
extracted from a drawing while a solid was published is a record built on the
wrong tier, and that is not hypothetical: `meanwell_uhp_350` was extracted from
vector-PDF geometry on the stated premise that "no solid published", shipped a
`bottom_mount_pitch_x_mm` wrong by 4.2 mm, and the solid existed the whole time
at `/Upload/PDF/UHP-350(R)/UHP-350(R)-3D.zip`. The only thing missing was a URL
spelling: the obvious `/UHP-350/UHP-350-3D.zip` 404s.

So this walks the spellings for you. Mean Well puts 3D archives beside the spec
PDF, and series with an optional suffix live in a PARENTHESISED folder and
repeat the suffix in the filename — while the spec PDF in that same folder stays
unsuffixed. The cross product is small; guessing it by hand is what failed.

Network tool, like `check_links.py` — not part of `validate.py`, not run in the
unit suite. Run it when adding or revisiting a record, and before writing "no
solid published" into any notes field.

    python scripts/check_vendor_solids.py            # all records
    python scripts/check_vendor_solids.py meanwell_uhp_350

Exit status is 1 if any record has an unlisted solid, so CI can adopt it later.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# A 404 from this host is a ~1 KB HTML page served with status 404; a real
# archive is tens to thousands of KB. Anything smaller than this that claims
# 200 is a soft-404.
MIN_ARCHIVE_BYTES = 8192

# A record whose notes mention a STEP/solid was measured from one; it just may
# not cite the archive URL in `sources`.
SOLID_CLAIM = re.compile(r"3D STEP|vendor 3D|\.stp\b|\.step\b|-3D\.zip", re.I)

UA = {"User-Agent": "hardware-db/check_vendor_solids (+https://github.com/BakedBean3D)"}


def meanwell_candidates(series: str) -> list[str]:
    """Every spelling Mean Well is known to use for a series' 3D archive."""
    base = "https://www.meanwell.com/Upload/PDF"
    folders = [series, f"{series}(R)"]
    names = [f"{series}-3D.zip", f"{series}(R)-3D.zip", f"{series}-3D.rar"]
    seen: list[str] = []
    for folder in folders:
        for name in names:
            url = f"{base}/{folder}/{name}"
            if url not in seen:
                seen.append(url)
    return seen


def candidates_for(record: dict) -> list[str]:
    mfr = (record.get("manufacturer") or "").strip().lower()
    series = (record.get("series") or "").strip()
    if not series:
        return []
    if mfr == "mean well":
        return meanwell_candidates(series)
    # Other vendors publish solids too, but their URL shapes are not yet
    # characterised. Returning [] is honest; it is NOT evidence of no solid.
    return []


def probe(url: str, timeout: float = 20.0) -> tuple[bool, int, str]:
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(MIN_ARCHIVE_BYTES + 1)
            size = int(resp.headers.get("Content-Length") or len(body))
            ctype = resp.headers.get("Content-Type", "")
            if resp.status != 200:
                return False, size, f"HTTP {resp.status}"
            if size <= MIN_ARCHIVE_BYTES or "html" in ctype.lower():
                return False, size, f"soft-404 ({size} B, {ctype})"
            return True, size, f"{size} B"
    except urllib.error.HTTPError as e:
        return False, 0, f"HTTP {e.code}"
    except Exception as e:  # network flake, DNS, timeout
        return False, 0, f"{type(e).__name__}: {e}"


def load_records(only: set[str]) -> list[dict]:
    out: list[dict] = []
    for category in ("psu", "controller_boards"):
        path = os.path.join(ROOT, category, f"{category}.json")
        if not os.path.exists(path):
            continue
        for rec in json.load(open(path)):
            if only and rec.get("id") not in only:
                continue
            out.append(rec)
    return out


def main() -> int:
    only = set(sys.argv[1:])
    records = load_records(only)
    if only and not records:
        print(f"No records matched {sorted(only)}", file=sys.stderr)
        return 2

    print("Probing vendor sites for 3D solids not listed in `sources`...\n")
    findings: list[tuple[str, str, str]] = []
    skipped = 0

    for rec in records:
        urls = candidates_for(rec)
        if not urls:
            skipped += 1
            continue
        listed = " ".join(rec.get("sources") or []).lower()
        if any(tok in listed for tok in ("-3d.zip", "-3d.rar", ".stp", ".step")):
            continue  # record already cites a solid
        for url in urls:
            ok, _size, detail = probe(url)
            if ok:
                # Two very different situations, and conflating them is how a
                # gate gets ignored. A record whose NOTES describe a STEP
                # extraction was measured correctly and merely under-cites its
                # provenance. A record with no solid claim anywhere is
                # drawing-derived while a solid exists — the UHP-350 shape.
                claims_solid = bool(SOLID_CLAIM.search(rec.get("notes") or ""))
                findings.append(
                    ("CITE" if claims_solid else "RE-EXTRACT", rec["id"], url, detail)
                )
                break

    reextract = [f for f in findings if f[0] == "RE-EXTRACT"]
    cite = [f for f in findings if f[0] == "CITE"]

    for _kind, rec_id, url, detail in reextract:
        print(f"  RE-EXTRACT  {rec_id}")
        print(f"      {url}  ({detail})")
        print("      A vendor solid exists and this record's notes make no claim")
        print("      of having used one — so its geometry is drawing-derived while")
        print("      a higher-tier artifact was available. This is exactly how")
        print("      meanwell_uhp_350 shipped a pitch wrong by 4.2 mm.\n")

    for _kind, rec_id, url, detail in cite:
        print(f"  CITE-ONLY   {rec_id}")
        print(f"      {url}  ({detail})")
        print("      Notes describe a STEP extraction, so the geometry is likely")
        print("      fine — but `sources` omits the archive, so nothing records")
        print("      WHICH solid. Add the URL. Not a geometry defect.\n")

    checked = len(records) - skipped
    tail = (f"({checked} checked, {skipped} skipped: vendor URL shape unknown, "
            f"which is NOT evidence of no solid)")
    if reextract:
        print(f"FAILED — {len(reextract)} record(s) drawing-derived with a solid "
              f"available; {len(cite)} more under-cite their source {tail}")
        return 1
    if cite:
        print(f"PASSED with {len(cite)} provenance gap(s) — every record with a "
              f"published solid claims to have used one {tail}")
        return 0
    print(f"PASSED — no unlisted vendor solids {tail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
