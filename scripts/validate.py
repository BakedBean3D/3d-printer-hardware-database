#!/usr/bin/env python3
"""Validate all YAML data files against expected schemas."""
import sys
import os
import yaml

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

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

SCHEMAS = {
    "motors.yaml": MOTOR_REQUIRED,
    "hotends.yaml": HOTEND_REQUIRED,
    "extruders.yaml": EXTRUDER_REQUIRED,
    "probes.yaml": PROBE_REQUIRED,
    "toolheads.yaml": TOOLHEAD_REQUIRED,
}


def validate_file(filename, required_fields):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  MISSING: {filename}")
        return 1

    with open(filepath) as f:
        data = yaml.safe_load(f)

    if not isinstance(data, list):
        print(f"  ERROR: {filename} root must be a list")
        return 1

    errors = 0
    ids_seen = set()

    for i, entry in enumerate(data):
        entry_id = entry.get("id", f"<index {i}>")

        if entry_id in ids_seen:
            print(f"  DUPLICATE ID: {entry_id} in {filename}")
            errors += 1
        ids_seen.add(entry_id)

        for field in required_fields:
            if field not in entry:
                print(f"  MISSING FIELD: {filename}[{entry_id}].{field}")
                errors += 1

        if "id" in entry and not entry["id"].replace("_", "").replace("0123456789", "").isascii():
            pass  # basic check
        if "id" in entry and " " in entry["id"]:
            print(f"  BAD ID (spaces): {entry_id} in {filename}")
            errors += 1

    if errors == 0:
        print(f"  OK: {filename} ({len(data)} entries)")
    return errors


def main():
    print("Validating hardware database...")
    total_errors = 0

    for filename, fields in SCHEMAS.items():
        total_errors += validate_file(filename, fields)

    # Check performance_profiles exists (looser schema)
    pp_path = os.path.join(DATA_DIR, "performance_profiles.yaml")
    if os.path.exists(pp_path):
        with open(pp_path) as f:
            data = yaml.safe_load(f)
        print(f"  OK: performance_profiles.yaml ({len(data)} entries)")
    else:
        print("  MISSING: performance_profiles.yaml")
        total_errors += 1

    print(f"\n{'PASSED' if total_errors == 0 else 'FAILED'} ({total_errors} errors)")
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
