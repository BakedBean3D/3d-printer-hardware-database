#!/usr/bin/env python3
"""Validate all YAML data files against expected schemas."""
import sys
import os
import glob
import yaml

ROOT = os.path.join(os.path.dirname(__file__), "..")

MOTOR_REQUIRED = [
    "id", "name", "manufacturer", "frame_size", "body_length_mm",
    "rated_current_amps", "recommended_run_current", "holding_torque_ncm",
    "inductance_mh", "resistance_ohms", "step_angle", "weight", "tooth_count", "notes",
]

HOTEND_REQUIRED = [
    "id", "name", "manufacturer", "meltzone_length", "max_volumetric_flow",
    "max_temp", "recommended_temp_pla", "recommended_temp_abs",
    "recommended_temp_petg", "nozzle_thread", "weight", "recommended_max_speed", "notes",
]

EXTRUDER_REQUIRED = [
    "id", "name", "manufacturer", "type", "gear_ratio", "steps_per_mm",
    "rotation_distance", "uses_gear_ratio_in_config", "motor", "motor_current",
    "max_speed", "max_accel", "weight", "filament_path_length",
    "recommended_pressure_advance", "notes",
]

PROBE_REQUIRED = [
    "id", "name", "type", "accuracy", "repeatability", "z_offset_typical",
    "speed", "samples", "sample_retract_dist", "notes",
]

TOOLHEAD_REQUIRED = [
    "id", "name", "manufacturer", "compatible_extruders", "compatible_hotends",
    "compatible_printer_types", "weight", "fan_config", "part_cooling_cfm",
    "supports_neopixels", "supports_klicky", "supports_tap", "mounting_method", "notes",
]

CATEGORIES = {
    "motors": MOTOR_REQUIRED,
    "hotends": HOTEND_REQUIRED,
    "extruders": EXTRUDER_REQUIRED,
    "probes": PROBE_REQUIRED,
    "toolheads": TOOLHEAD_REQUIRED,
}


def validate_file(filepath, required_fields):
    with open(filepath) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, list):
        print(f"  ERROR: {filepath} root must be a list")
        return 1, 0

    errors = 0
    ids_seen = set()

    for i, entry in enumerate(data):
        entry_id = entry.get("id", f"<index {i}>")

        if entry_id in ids_seen:
            print(f"  DUPLICATE ID: {entry_id} in {filepath}")
            errors += 1
        ids_seen.add(entry_id)

        for field in required_fields:
            if field not in entry:
                print(f"  MISSING FIELD: {filepath}[{entry_id}].{field}")
                errors += 1

        if "id" in entry and " " in entry["id"]:
            print(f"  BAD ID (spaces): {entry_id} in {filepath}")
            errors += 1

    return errors, len(data)


def main():
    print("Validating hardware database...\n")
    total_errors = 0
    total_entries = 0

    for category, fields in CATEGORIES.items():
        cat_dir = os.path.join(ROOT, category)
        if not os.path.isdir(cat_dir):
            print(f"  MISSING DIR: {category}/")
            total_errors += 1
            continue

        yaml_files = sorted(glob.glob(os.path.join(cat_dir, "*.yaml")))
        if not yaml_files:
            print(f"  EMPTY: {category}/ (no YAML files)")
            total_errors += 1
            continue

        cat_ids = set()
        cat_entries = 0
        for filepath in yaml_files:
            errors, count = validate_file(filepath, fields)
            total_errors += errors
            cat_entries += count

            with open(filepath) as f:
                data = yaml.safe_load(f)
            for entry in data:
                eid = entry.get("id")
                if eid in cat_ids:
                    print(f"  CROSS-FILE DUPLICATE: {eid} in {category}/")
                    total_errors += 1
                cat_ids.add(eid)

        total_entries += cat_entries
        print(f"  {category}/: {cat_entries} entries across {len(yaml_files)} files")

    pp_dir = os.path.join(ROOT, "performance_profiles")
    pp_files = glob.glob(os.path.join(pp_dir, "*.yaml"))
    if pp_files:
        with open(pp_files[0]) as f:
            data = yaml.safe_load(f)
        total_entries += len(data)
        print(f"  performance_profiles/: {len(data)} entries")
    else:
        print("  MISSING: performance_profiles/")
        total_errors += 1

    print(f"\n{'PASSED' if total_errors == 0 else 'FAILED'} — {total_entries} total entries, {total_errors} errors")
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
