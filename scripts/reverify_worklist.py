#!/usr/bin/env python3
"""Emit the confidence re-verification worklist: every `confidence: low`
entry that is due, prioritized by how likely a primary source exists.

Priority order: motors (part numbers -> datasheets almost certainly exist),
hotends, extruders, probes, controller_boards, psu, then toolheads last
(most are community designs whose weights/CFMs may be genuinely unpublished
— for those, "confirmed unpublished" is a valid outcome that keeps the
entry low/medium with a note, not a failure).

An entry is due when it has no `reverify` record, or when its
`reverify.checked` is at least REVERIFY_RECHECK_DAYS[outcome] days old
(scripts/validate.py owns both the field and the intervals). That is what
stops a blocked or unpublished entry being re-hunted every batch.

Usage:
    python3 scripts/reverify_worklist.py [--limit N] [--json] [--as-of YYYY-MM-DD]
"""
import datetime
import glob
import importlib.util
import json
import os
import sys

import yaml

ROOT = os.path.join(os.path.dirname(__file__), "..")
PRIORITY = ["motors", "hotends", "extruders", "probes",
            "controller_boards", "psu", "toolheads"]

_spec = importlib.util.spec_from_file_location(
    "validate", os.path.join(os.path.dirname(__file__), "validate.py"))
assert _spec is not None and _spec.loader is not None
validate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate)


def due_date(entry):
    """When a low entry is next due for re-verification; None = due now."""
    checked = validate.reverify_checked(entry)
    if checked is None:
        return None
    days = validate.REVERIFY_RECHECK_DAYS[entry["reverify"]["outcome"]]
    return checked + datetime.timedelta(days=days)


def worklist(as_of):
    """(due, deferred): low entries due on `as_of`, and those not yet due."""
    due, deferred = [], []
    for cat in PRIORITY:
        for path in sorted(glob.glob(os.path.join(ROOT, cat, "*.yaml"))):
            rel = os.path.relpath(path, ROOT)
            with open(path) as f:
                data = yaml.safe_load(f) or []
            for e in data:
                if not (isinstance(e, dict) and e.get("confidence") == "low"):
                    continue
                item = {
                    "category": cat,
                    "file": rel,
                    "id": e.get("id"),
                    "name": e.get("name"),
                    "manufacturer": e.get("manufacturer"),
                    "reverify": e.get("reverify"),
                    "notes": e.get("notes"),
                }
                next_due = due_date(e)
                if next_due is None or next_due <= as_of:
                    due.append(item)
                else:
                    item["due"] = next_due.isoformat()
                    deferred.append(item)
    return due, deferred


def main():
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])
    as_of = datetime.date.today()
    if "--as-of" in sys.argv:
        as_of = datetime.date.fromisoformat(sys.argv[sys.argv.index("--as-of") + 1])
    items, deferred = worklist(as_of)
    total = len(items)
    if limit is not None:
        items = items[:limit]

    if "--json" in sys.argv:
        print(json.dumps(items, indent=2))
        return

    print(f"{total} low-confidence entries due as of {as_of}"
          + (f" (showing first {len(items)})" if limit is not None else "")
          + f"; {len(deferred)} not yet due:\n")
    for it in items:
        print(f"[{it['file']}] {it['id']} — {it['name']} ({it['manufacturer']})")
        if it["reverify"]:
            print(f"    last re-verified {it['reverify']['checked']}: {it['reverify']['outcome']}")
        print(f"    notes: {it['notes']}\n")
    for it in deferred:
        print(f"  not due until {it['due']} ({it['reverify']['outcome']}): [{it['file']}] {it['id']}")


if __name__ == "__main__":
    main()
