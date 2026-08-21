#!/usr/bin/env python3
"""Emit the confidence re-verification worklist: every `confidence: low`
entry, prioritized by how likely a primary source exists.

Priority order: motors (part numbers -> datasheets almost certainly exist),
hotends, extruders, probes, controller_boards, psu, then toolheads last
(most are community designs whose weights/CFMs may be genuinely unpublished
— for those, "confirmed unpublished" is a valid outcome that keeps the
entry low/medium with a note, not a failure).

Usage:
    python3 scripts/reverify_worklist.py [--limit N] [--json]
"""
import glob
import json
import os
import sys

import yaml

ROOT = os.path.join(os.path.dirname(__file__), "..")
PRIORITY = ["motors", "hotends", "extruders", "probes",
            "controller_boards", "psu", "toolheads"]


def worklist():
    items = []
    for cat in PRIORITY:
        for path in sorted(glob.glob(os.path.join(ROOT, cat, "*.yaml"))):
            rel = os.path.relpath(path, ROOT)
            with open(path) as f:
                data = yaml.safe_load(f) or []
            for e in data:
                if isinstance(e, dict) and e.get("confidence") == "low":
                    items.append({
                        "category": cat,
                        "file": rel,
                        "id": e.get("id"),
                        "name": e.get("name"),
                        "manufacturer": e.get("manufacturer"),
                        "notes": e.get("notes"),
                    })
    return items


def main():
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    items = worklist()
    total = len(items)
    if limit is not None:
        items = items[:limit]

    if "--json" in sys.argv:
        print(json.dumps(items, indent=2))
        return

    print(f"{total} low-confidence entries"
          + (f" (showing first {len(items)})" if limit is not None else "") + ":\n")
    for it in items:
        print(f"[{it['file']}] {it['id']} — {it['name']} ({it['manufacturer']})")
        print(f"    notes: {it['notes']}\n")


if __name__ == "__main__":
    main()
