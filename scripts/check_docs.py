#!/usr/bin/env python3
"""Sync checks between scripts/validate.py (the schema source of truth) and
the artifacts that must agree with it but can silently drift:

1. scripts/submit-hardware.sh must know every category in CATEGORIES.
   (Its router bug existed because it hardcoded 5 of 7 categories.)
2. README.md field tables must match the required-field lists for the
   categories that have tables (motors, controller_boards, psu), in both
   directions: no required field missing from the table, no table row
   documenting a field the schema doesn't have.

Lives here (one script, run in CI) rather than making submit-hardware.sh
import its list at runtime: the shell script stays dependency-free and the
CI gate still guarantees the lists can't drift apart.
"""
import importlib.util
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")

_spec = importlib.util.spec_from_file_location(
    "validate", os.path.join(os.path.dirname(__file__), "validate.py"))
assert _spec is not None and _spec.loader is not None
validate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate)

# README section heading -> (category, required list). Only these three
# categories have README field tables today; extend when tables are added.
README_TABLES = {
    "### Motor fields": ("motors", validate.MOTOR_REQUIRED),
    "### Hotend fields": ("hotends", validate.HOTEND_REQUIRED),
    "### Extruder fields": ("extruders", validate.EXTRUDER_REQUIRED),
    "### Probe fields": ("probes", validate.PROBE_REQUIRED),
    "### Toolhead fields": ("toolheads", validate.TOOLHEAD_REQUIRED),
    "### Controller board fields": ("controller_boards", validate.CONTROLLER_BOARD_REQUIRED),
    "### PSU fields": ("psu", validate.PSU_REQUIRED),
}

# Documented-but-optional fields: present in the README table (and in the
# data) but deliberately not required on every entry.
OPTIONAL_DOCUMENTED = {
    "motors": {"datasheet_url"},
    "extruders": {"motor_id"},
    "probes": {"manufacturer"},
    "controller_boards": {"mount_holes_xy"},
    "psu": set(),
}


def check_submit_script():
    errors = 0
    path = os.path.join(ROOT, "scripts", "submit-hardware.sh")
    with open(path) as f:
        script = f.read()
    for cat in validate.CATEGORIES:
        if not re.search(rf"\b{re.escape(cat)}\b", script):
            print(f"  CATEGORY NOT ROUTED: {cat!r} missing from scripts/submit-hardware.sh")
            errors += 1
    return errors


def _table_fields(readme_lines, heading):
    """Backticked field names from the markdown table under `heading`.
    Slash-separated names (`a_mm` / `b_mm`) share a row; each counts."""
    fields = set()
    in_section = False
    for line in readme_lines:
        if line.startswith(heading):
            in_section = True
            continue
        if in_section and line.startswith("#"):
            break
        if in_section and line.startswith("|"):
            first_cell = line.split("|")[1]
            fields.update(re.findall(r"`([a-z0-9_]+)`", first_cell))
    return fields


def check_readme_tables():
    errors = 0
    with open(os.path.join(ROOT, "README.md")) as f:
        readme_lines = f.read().splitlines()

    for heading, (category, required) in README_TABLES.items():
        documented = _table_fields(readme_lines, heading)
        if not documented:
            print(f"  TABLE NOT FOUND: README section {heading!r}")
            errors += 1
            continue
        allowed_extra = OPTIONAL_DOCUMENTED.get(category, set())
        for field in required:
            if field not in documented:
                print(f"  UNDOCUMENTED FIELD: {category}.{field} required by "
                      f"validate.py but missing from README table {heading!r}")
                errors += 1
        for field in documented - set(required) - allowed_extra:
            print(f"  STALE DOC ROW: README table {heading!r} documents "
                  f"{category}.{field} which is not in the required list "
                  "(add to the list or to OPTIONAL_DOCUMENTED)")
            errors += 1
    return errors


def main():
    print("Checking doc/script sync with validate.py...\n")
    errors = check_submit_script() + check_readme_tables()
    print(f"\n{'PASSED' if errors == 0 else 'FAILED'} — {errors} sync errors")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
