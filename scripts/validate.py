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

# Controller / toolhead / SBC / accessory PCB mounting dimensions.
# null is permitted for any numeric whose value is genuinely unknown (do NOT
# substitute 0 — a 0 mm dimension reads as real). Unknowns must be flagged in notes.
CONTROLLER_BOARD_REQUIRED = [
    "id", "name", "manufacturer", "category",
    "pcb_length_mm", "pcb_width_mm", "pcb_thickness_mm",
    "mount_screw", "mount_hole_dia_mm", "mount_pattern",
    "mount_pitch_x_mm", "mount_pitch_y_mm", "mount_hole_count",
    "standoff_height_mm", "connector_notes", "sources", "confidence", "notes",
]

# Power supply mounting dimensions for parametric mount generation. Every unit
# carries TWO mount patterns (bottom = vertical-entry flat/plate mount, side =
# the vendor's second documented pattern -- see psu/README conventions in
# psu/gen.py's PSU.md header for what "side" means per case family) plus
# DIN-rail clip fields for MDR/EDR-style units. null is permitted for any
# numeric whose value is genuinely unknown (do NOT substitute 0).
PSU_REQUIRED = [
    "id", "name", "manufacturer", "series", "category",
    "length_mm", "width_mm", "height_mm", "weight_g", "wattage_w", "output_voltages_v",
    "bottom_mount_screw", "bottom_mount_interface", "bottom_mount_hole_dia_mm", "bottom_mount_hole_count",
    "bottom_mount_pattern", "bottom_mount_pitch_x_mm", "bottom_mount_pitch_y_mm", "bottom_mount_holes_xy",
    "bottom_mount_max_penetration_mm",
    "side_mount_screw", "side_mount_hole_dia_mm", "side_mount_hole_count", "side_mount_pattern",
    "side_mount_pitch_x_mm", "side_mount_holes_xy", "side_mount_max_penetration_mm",
    "din_rail_compatible", "din_rail_type",
    "terminal_location", "connector_notes", "sources", "confidence", "notes",
]

CATEGORIES = {
    "motors": MOTOR_REQUIRED,
    "hotends": HOTEND_REQUIRED,
    "extruders": EXTRUDER_REQUIRED,
    "probes": PROBE_REQUIRED,
    "toolheads": TOOLHEAD_REQUIRED,
    "controller_boards": CONTROLLER_BOARD_REQUIRED,
    "psu": PSU_REQUIRED,
}


def _num(entry, key):
    """Value of a numeric field, or None if absent/null/non-numeric."""
    v = entry.get(key)
    return v if isinstance(v, (int, float)) else None


def _check_mount_group(entry_id, filepath, entry, prefix, dim_x_key, dim_y_key):
    """Physical-consistency checks for one mount-hole group.

    Catches the class of error where a hole grid cannot physically exist on
    the part (e.g. a pitch equal to or larger than the face it sits on, or
    explicit hole coordinates outside the case) — a real defect class: the
    LRS-200/350 records initially shipped a 150x115 grid on a 115 mm-wide
    case because a drawing envelope was misread as the mounting face.
    """
    errors = 0
    L, W = _num(entry, dim_x_key), _num(entry, dim_y_key)
    px = _num(entry, prefix + "pitch_x_mm")
    py = _num(entry, prefix + "pitch_y_mm")
    holes = entry.get(prefix + "holes_xy")
    tag = f"{filepath}[{entry_id}].{prefix.rstrip('_')}"

    # A pitch can never equal or exceed the face dimension on its axis:
    # hole centers need at least a hole radius of material inboard.
    for pitch, dim, axis in ((px, L, "x"), (py, W, "y")):
        if pitch is not None and dim is not None and pitch >= dim - 1.0:
            print(f"  IMPOSSIBLE PITCH: {tag} pitch_{axis}={pitch} on {dim} mm face")
            errors += 1

    if isinstance(holes, list) and holes:
        xs = [h[0] for h in holes if isinstance(h, (list, tuple)) and len(h) == 2]
        ys = [h[1] for h in holes if isinstance(h, (list, tuple)) and len(h) == 2]
        if len(xs) != len(holes):
            print(f"  MALFORMED holes_xy: {tag}")
            return errors + 1
        # holes must lie on the part (0.5 mm tolerance for edge-breaking chamfers)
        for lo_hi, dim, axis in ((xs, L, "x"), (ys, W, "y")):
            if dim is None:
                continue
            for v in lo_hi:
                if v < -0.5 or v > dim + 0.5:
                    print(f"  HOLE OFF PART: {tag} {axis}={v} outside 0..{dim}")
                    errors += 1
        # explicit coordinates must agree with the declared pitch
        for pitch, vals, axis in ((px, xs, "x"), (py, ys, "y")):
            if pitch is not None and len(set(round(v, 1) for v in vals)) > 1:
                spread = max(vals) - min(vals)
                if abs(spread - pitch) > 0.2:
                    print(f"  PITCH/HOLES MISMATCH: {tag} {axis} spread {spread:.2f} vs pitch_{axis} {pitch}")
                    errors += 1
    return errors


def check_physics(entry_id, filepath, entry, category):
    """Category-specific geometric sanity. Errors here mean the record cannot
    describe a real part, regardless of what the source drawing said."""
    errors = 0
    if category == "controller_boards":
        errors += _check_mount_group(entry_id, filepath, entry, "mount_",
                                     "pcb_length_mm", "pcb_width_mm")
        for key in ("pcb_length_mm", "pcb_width_mm", "pcb_thickness_mm",
                    "mount_hole_dia_mm", "mount_pitch_x_mm", "mount_pitch_y_mm"):
            v = _num(entry, key)
            if v is not None and v <= 0:
                print(f"  NON-POSITIVE DIM: {filepath}[{entry_id}].{key}={v} (use null for unknown, never 0)")
                errors += 1
    elif category == "psu":
        errors += _check_mount_group(entry_id, filepath, entry, "bottom_mount_",
                                     "length_mm", "width_mm")
        # bottom_mount_interface: what the case-side holes physically are.
        # A record with a bottom screw size MUST declare it — a mount
        # generator that threads into "clearance_ears" (UHP class) produces
        # a part that cannot fasten at all, so this may never be guessed.
        iface = entry.get("bottom_mount_interface")
        tag = f"{filepath}[{entry_id}].bottom_mount_interface"
        if iface not in ("threaded_case", "clearance_ears", None):
            print(f"  BAD INTERFACE VALUE: {tag}={iface!r}")
            errors += 1
        if entry.get("bottom_mount_screw") is not None and iface is None:
            print(f"  MISSING INTERFACE: {tag} must be declared when "
                  "bottom_mount_screw is set")
            errors += 1
        if iface == "threaded_case" and _num(entry, "bottom_mount_max_penetration_mm") is None:
            print(f"  MISSING PENETRATION: {tag}=threaded_case requires "
                  "bottom_mount_max_penetration_mm (thread-in safety depth)")
            errors += 1
        # side pattern runs along the length on the side walls
        spx = _num(entry, "side_mount_pitch_x_mm")
        L = _num(entry, "length_mm")
        if spx is not None and L is not None and spx >= L - 1.0:
            print(f"  IMPOSSIBLE PITCH: {filepath}[{entry_id}].side_mount pitch_x={spx} on {L} mm side")
            errors += 1
        for key in ("length_mm", "width_mm", "height_mm",
                    "bottom_mount_hole_dia_mm", "side_mount_hole_dia_mm",
                    "bottom_mount_max_penetration_mm", "side_mount_max_penetration_mm"):
            v = _num(entry, key)
            if v is not None and v <= 0:
                print(f"  NON-POSITIVE DIM: {filepath}[{entry_id}].{key}={v} (use null for unknown, never 0)")
                errors += 1
    return errors


def validate_file(filepath, required_fields, category=None):
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

        if category is not None:
            errors += check_physics(entry_id, filepath, entry, category)

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
            errors, count = validate_file(filepath, fields, category)
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

    print(f"\n{'PASSED' if total_errors == 0 else 'FAILED'} — {total_entries} total entries, {total_errors} errors")
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
