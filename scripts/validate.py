#!/usr/bin/env python3
"""Validate all YAML data files against expected schemas."""
import sys
import os
import glob
import yaml

ROOT = os.path.join(os.path.dirname(__file__), "..")


class StrictLoader(yaml.SafeLoader):
    """SafeLoader that rejects duplicate mapping keys.

    Stock safe_load is silently last-wins: a `weight:` appearing twice in one
    entry drops the first value with no diagnostic — exactly the failure mode
    a hand-edited database can't afford. Raises ConstructorError with both
    marks so the offending line is printed."""

    def construct_mapping(self, node, deep=False):
        seen = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                dupe = key in seen
            except TypeError:  # unhashable key; base class will report it
                continue
            if dupe:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping", node.start_mark,
                    f"found duplicate key {key!r}", key_node.start_mark)
            seen.add(key)
        return super().construct_mapping(node, deep)

MOTOR_REQUIRED = [
    "id", "name", "manufacturer", "frame_size", "body_length_mm",
    "rated_current_amps", "recommended_run_current", "holding_torque_ncm",
    "inductance_mh", "resistance_ohms", "step_angle", "weight_g", "tooth_count",
    "confidence", "notes",
]

HOTEND_REQUIRED = [
    "id", "name", "manufacturer", "meltzone_length", "max_volumetric_flow",
    "max_temp", "recommended_temp_pla", "recommended_temp_abs",
    "recommended_temp_petg", "nozzle_thread", "weight_g", "recommended_max_speed",
    "confidence", "notes",
]

EXTRUDER_REQUIRED = [
    "id", "name", "manufacturer", "drive", "type_detail", "gear_ratio",
    "rotation_distance", "uses_gear_ratio_in_config", "motor", "motor_current",
    "max_speed", "max_accel", "weight_g", "filament_path_length",
    "recommended_pressure_advance", "confidence", "notes",
]

PROBE_REQUIRED = [
    "id", "name", "type", "accuracy", "repeatability", "z_offset_typical",
    "speed", "samples", "sample_retract_dist", "scanning_capable", "confidence", "notes",
]

TOOLHEAD_REQUIRED = [
    "id", "name", "manufacturer", "compatible_extruders", "compatible_hotends",
    "compatible_printer_types", "weight_g", "fan_config", "part_cooling_cfm",
    "supports_neopixels", "supports_klicky", "supports_tap", "mounting_method",
    "confidence", "notes",
]

# Controller / toolhead / SBC / accessory PCB mounting dimensions.
# null is permitted for any numeric whose value is genuinely unknown (do NOT
# substitute 0 — a 0 mm dimension reads as real). Unknowns must be flagged in notes.
CONTROLLER_BOARD_REQUIRED = [
    "id", "name", "manufacturer", "category",
    "pcb_length_mm", "pcb_width_mm", "pcb_thickness_mm",
    "mount_screw", "mount_hole_dia_mm", "mount_pattern",
    "mount_pitch_x_mm", "mount_pitch_y_mm", "mount_hole_count",
    "mount_inset_from_edge_mm", "component_height_top_mm",
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

CONFIDENCE_VALUES = {"high", "medium", "low"}
CONTROLLER_MOUNT_PATTERN_VALUES = {
    "rectangular", "L-shaped", "linear", "2-hole", "3-hole", "4-hole", "none", "other",
}
PSU_MOUNT_PATTERN_VALUES = {"rectangular", "2-hole", "3-hole", "other", "none"}

# v2 controlled vocabularies. drive is the transmission class (exact-match
# filterable); free-text flavor lives in type_detail. Probe type folds the
# sensing principle with the dock/deploy integration axis (mechanically
# distinct for CAD); scanning stays in scanning_capable — not duplicated here.
EXTRUDER_DRIVE_VALUES = {"dual_gear", "planetary", "worm", "belt"}
PROBE_TYPE_VALUES = {
    "contact", "contact_deploy", "contact_dock",
    "inductive", "inductive_dock", "eddy_current",
}

# Upper NEMA17 bound accommodates the heaviest real part in class: the LDO
# Kraken 42STH60-3004AHS37 at 620 g / 60 mm body (10.3 g/mm, vendor spec).
NEMA_WEIGHT_PER_MM_BAND = {
    "NEMA14": (2.0, 7.0),
    "NEMA17": (4.5, 10.5),
    "NEMA23": (7.0, 20.0),
}

# Same defect class as the rotor-inertia-as-weight imports: a torque that is
# impossible for the frame size is a unit or transcription error, not a spec.
# Upper NEMA14 bound accommodates the strongest real long-body parts in class:
# FYSETC 35HSH7402-24B-400A at 42 N·cm / 51 mm (vendor datasheet) and the
# 52 mm 40 N·cm class (OMC 14HS20-1504S, LDO 35STH52). This gate caught the
# MOONS MS14HS5P4150 record carrying a 35 mm body length (frame size /
# rotor-inertia figure) against its real 55 mm body.
NEMA_HOLDING_TORQUE_NCM_BAND = {
    "NEMA14": (5.0, 45.0),
    "NEMA17": (12.0, 90.0),
    "NEMA23": (50.0, 350.0),
}

CATEGORIES = {
    "motors": MOTOR_REQUIRED,
    "hotends": HOTEND_REQUIRED,
    "extruders": EXTRUDER_REQUIRED,
    "probes": PROBE_REQUIRED,
    "toolheads": TOOLHEAD_REQUIRED,
    "controller_boards": CONTROLLER_BOARD_REQUIRED,
    "psu": PSU_REQUIRED,
}

# Expected YAML type per field, checked only when the value is present and
# non-null (null always means unknown and is governed by the required lists).
# "number" accepts int or float; "integer" is for true counts where a
# fraction is meaningless. Without this, `weight: "350"` (a string) silently
# skips every numeric plausibility check because _num() returns None.
_T_STR, _T_NUM, _T_INT, _T_BOOL, _T_LIST = "string", "number", "integer", "bool", "list"

MOTOR_FIELD_TYPES = {
    "id": _T_STR, "name": _T_STR, "manufacturer": _T_STR, "frame_size": _T_STR,
    "notes": _T_STR, "datasheet_url": _T_STR, "confidence": _T_STR,
    "body_length_mm": _T_NUM, "rated_current_amps": _T_NUM,
    "recommended_run_current": _T_NUM, "holding_torque_ncm": _T_NUM,
    "inductance_mh": _T_NUM, "resistance_ohms": _T_NUM, "step_angle": _T_NUM,
    "weight_g": _T_NUM, "tooth_count": _T_INT,
}

HOTEND_FIELD_TYPES = {
    "id": _T_STR, "name": _T_STR, "manufacturer": _T_STR,
    "nozzle_thread": _T_STR, "notes": _T_STR, "confidence": _T_STR,
    "meltzone_length": _T_NUM, "max_volumetric_flow": _T_NUM, "max_temp": _T_NUM,
    "recommended_temp_pla": _T_NUM, "recommended_temp_abs": _T_NUM,
    "recommended_temp_petg": _T_NUM, "weight_g": _T_NUM, "recommended_max_speed": _T_NUM,
}

EXTRUDER_FIELD_TYPES = {
    "id": _T_STR, "name": _T_STR, "manufacturer": _T_STR, "drive": _T_STR,
    "type_detail": _T_STR,
    "gear_ratio": _T_STR, "motor": _T_STR, "motor_id": _T_STR, "notes": _T_STR,
    "confidence": _T_STR,
    "rotation_distance": _T_NUM, "motor_current": _T_NUM, "max_speed": _T_NUM,
    "max_accel": _T_NUM, "weight_g": _T_NUM, "filament_path_length": _T_NUM,
    "recommended_pressure_advance": _T_NUM,
    "uses_gear_ratio_in_config": _T_BOOL,
}

PROBE_FIELD_TYPES = {
    "id": _T_STR, "name": _T_STR, "manufacturer": _T_STR, "type": _T_STR,
    "notes": _T_STR, "confidence": _T_STR,
    "accuracy": _T_NUM, "repeatability": _T_NUM, "z_offset_typical": _T_NUM,
    "speed": _T_NUM, "sample_retract_dist": _T_NUM,
    "samples": _T_INT, "scanning_capable": _T_BOOL,
}

TOOLHEAD_FIELD_TYPES = {
    "id": _T_STR, "name": _T_STR, "manufacturer": _T_STR, "fan_config": _T_STR,
    "mounting_method": _T_STR, "notes": _T_STR, "confidence": _T_STR,
    "compatible_extruders": _T_LIST, "compatible_hotends": _T_LIST,
    "compatible_printer_types": _T_LIST,
    "weight_g": _T_NUM, "part_cooling_cfm": _T_NUM,
    "supports_neopixels": _T_BOOL, "supports_klicky": _T_BOOL, "supports_tap": _T_BOOL,
}

CONTROLLER_BOARD_FIELD_TYPES = {
    "id": _T_STR, "name": _T_STR, "manufacturer": _T_STR, "category": _T_STR,
    "mount_screw": _T_STR, "mount_pattern": _T_STR, "connector_notes": _T_STR,
    "confidence": _T_STR, "notes": _T_STR,
    "pcb_length_mm": _T_NUM, "pcb_width_mm": _T_NUM, "pcb_thickness_mm": _T_NUM,
    "mount_hole_dia_mm": _T_NUM, "mount_pitch_x_mm": _T_NUM, "mount_pitch_y_mm": _T_NUM,
    "mount_inset_from_edge_mm": _T_NUM, "component_height_top_mm": _T_NUM,
    "standoff_height_mm": _T_NUM,
    "mount_hole_count": _T_INT,
    "mount_holes_xy": _T_LIST, "sources": _T_LIST,
}

PSU_FIELD_TYPES = {
    "id": _T_STR, "name": _T_STR, "manufacturer": _T_STR, "series": _T_STR,
    "category": _T_STR, "bottom_mount_screw": _T_STR, "bottom_mount_interface": _T_STR,
    "bottom_mount_pattern": _T_STR, "side_mount_screw": _T_STR,
    "side_mount_pattern": _T_STR, "din_rail_type": _T_STR,
    "terminal_location": _T_STR, "connector_notes": _T_STR,
    "confidence": _T_STR, "notes": _T_STR,
    "length_mm": _T_NUM, "width_mm": _T_NUM, "height_mm": _T_NUM,
    "weight_g": _T_NUM, "wattage_w": _T_NUM,
    "bottom_mount_hole_dia_mm": _T_NUM, "bottom_mount_pitch_x_mm": _T_NUM,
    "bottom_mount_pitch_y_mm": _T_NUM, "bottom_mount_max_penetration_mm": _T_NUM,
    "side_mount_hole_dia_mm": _T_NUM, "side_mount_pitch_x_mm": _T_NUM,
    "side_mount_max_penetration_mm": _T_NUM,
    "bottom_mount_hole_count": _T_INT, "side_mount_hole_count": _T_INT,
    "output_voltages_v": _T_LIST, "bottom_mount_holes_xy": _T_LIST,
    "side_mount_holes_xy": _T_LIST,
    "din_rail_compatible": _T_BOOL,
}

FIELD_TYPES = {
    "motors": MOTOR_FIELD_TYPES,
    "hotends": HOTEND_FIELD_TYPES,
    "extruders": EXTRUDER_FIELD_TYPES,
    "probes": PROBE_FIELD_TYPES,
    "toolheads": TOOLHEAD_FIELD_TYPES,
    "controller_boards": CONTROLLER_BOARD_FIELD_TYPES,
    "psu": PSU_FIELD_TYPES,
}

# bool is an int subclass in Python — exclude it from the numeric types so
# `weight: true` can never pass as a number.
_TYPE_CHECKS = {
    _T_STR: lambda v: isinstance(v, str),
    _T_NUM: lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    _T_INT: lambda v: isinstance(v, int) and not isinstance(v, bool),
    _T_BOOL: lambda v: isinstance(v, bool),
    _T_LIST: lambda v: isinstance(v, list),
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


def _check_hole_count(entry_id, filepath, entry, prefix):
    """A declared hole_count must agree with an explicit holes_xy list, when
    both are actually specified. An empty holes_xy list means "not specified"
    and is not a claim of zero holes, so it's skipped."""
    holes = entry.get(prefix + "holes_xy")
    hole_count = entry.get(prefix + "hole_count")
    if isinstance(holes, list) and holes and isinstance(hole_count, int) and hole_count > 0:
        if len(holes) != hole_count:
            tag = f"{filepath}[{entry_id}].{prefix.rstrip('_')}"
            print(f"  HOLE COUNT MISMATCH: {tag} holes_xy has {len(holes)} entries but hole_count={hole_count}")
            return 1
    return 0


def _check_enum(entry_id, filepath, entry, key, allowed, null_ok=True):
    v = entry.get(key)
    if v is None:
        if null_ok:
            return 0
        print(f"  BAD ENUM (must be set): {filepath}[{entry_id}].{key} is null")
        return 1
    if v not in allowed:
        print(f"  BAD ENUM: {filepath}[{entry_id}].{key}={v!r} not in {sorted(allowed)}")
        return 1
    return 0


def _check_confidence_provenance(entry_id, filepath, entry):
    """confidence: high claims a primary source — require a URL somewhere the
    schema can carry one (datasheet_url, sources, or notes). An entry whose
    provenance is a vague citation can be at most medium."""
    if entry.get("confidence") != "high":
        return 0
    for key in ("datasheet_url", "sources", "notes"):
        v = entry.get(key)
        if isinstance(v, str) and "http" in v:
            return 0
        if isinstance(v, list) and any(isinstance(x, str) and "http" in x for x in v):
            return 0
    print(f"  UNSOURCED HIGH CONFIDENCE: {filepath}[{entry_id}] confidence=high "
          "requires an http(s) URL in datasheet_url/sources/notes")
    return 1


def _check_motor_physics(entry_id, filepath, entry):
    """Stepper motor sanity: positive physical/electrical fields, a valid
    step angle, and a plausible weight-per-mm-of-body-length for the frame
    size (catches weights that are off by an order of magnitude)."""
    errors = 0
    tag = f"{filepath}[{entry_id}]"

    for key in ("body_length_mm", "rated_current_amps", "holding_torque_ncm",
                "inductance_mh", "resistance_ohms", "step_angle", "weight_g"):
        v = _num(entry, key)
        if v is not None and v <= 0:
            print(f"  NON-POSITIVE VALUE: {tag}.{key}={v}")
            errors += 1

    tooth_count = _num(entry, "tooth_count")
    if tooth_count is not None and tooth_count < 0:
        print(f"  NEGATIVE VALUE: {tag}.tooth_count={tooth_count}")
        errors += 1

    step_angle = _num(entry, "step_angle")
    if step_angle is not None and step_angle not in (0.9, 1.8):
        print(f"  BAD STEP ANGLE: {tag}.step_angle={step_angle} (must be 0.9 or 1.8)")
        errors += 1

    frame_size = entry.get("frame_size")
    weight = _num(entry, "weight_g")
    body_length = _num(entry, "body_length_mm")
    band = NEMA_WEIGHT_PER_MM_BAND.get(frame_size)
    if band is not None and weight is not None and body_length is not None and body_length > 0:
        gpm = weight / body_length
        lo, hi = band
        if not (lo <= gpm <= hi):
            print(f"  IMPLAUSIBLE WEIGHT: {tag} weight={weight}g body_length={body_length}mm "
                  f"-> {gpm:.2f} g/mm outside {frame_size} band {lo}-{hi}")
            errors += 1

    torque = _num(entry, "holding_torque_ncm")
    tband = NEMA_HOLDING_TORQUE_NCM_BAND.get(frame_size)
    if tband is not None and torque is not None:
        lo, hi = tband
        if not (lo <= torque <= hi):
            print(f"  IMPLAUSIBLE TORQUE: {tag} holding_torque_ncm={torque} "
                  f"outside {frame_size} band {lo}-{hi}")
            errors += 1
    return errors


def _check_hotend_physics(entry_id, filepath, entry):
    """Hotend sanity: temps in a plausible range, recommended temps never
    exceed the rated max, and positive weight/flow."""
    errors = 0
    tag = f"{filepath}[{entry_id}]"

    max_temp = _num(entry, "max_temp")
    if max_temp is not None and not (200 <= max_temp <= 550):
        print(f"  IMPLAUSIBLE MAX TEMP: {tag}.max_temp={max_temp} (expected 200-550)")
        errors += 1

    for key in ("recommended_temp_pla", "recommended_temp_abs", "recommended_temp_petg"):
        v = _num(entry, key)
        if v is not None and max_temp is not None and v > max_temp:
            print(f"  TEMP EXCEEDS MAX: {tag}.{key}={v} > max_temp={max_temp}")
            errors += 1

    for key in ("weight_g", "max_volumetric_flow"):
        v = _num(entry, key)
        if v is not None and v <= 0:
            print(f"  NON-POSITIVE VALUE: {tag}.{key}={v}")
            errors += 1
    return errors


def check_physics(entry_id, filepath, entry, category):
    """Category-specific geometric sanity. Errors here mean the record cannot
    describe a real part, regardless of what the source drawing said."""
    errors = _check_enum(entry_id, filepath, entry, "confidence", CONFIDENCE_VALUES, null_ok=False)
    errors += _check_confidence_provenance(entry_id, filepath, entry)
    if category == "controller_boards":
        errors += _check_mount_group(entry_id, filepath, entry, "mount_",
                                     "pcb_length_mm", "pcb_width_mm")
        errors += _check_hole_count(entry_id, filepath, entry, "mount_")
        errors += _check_enum(entry_id, filepath, entry, "mount_pattern", CONTROLLER_MOUNT_PATTERN_VALUES)
        for key in ("pcb_length_mm", "pcb_width_mm", "pcb_thickness_mm",
                    "mount_hole_dia_mm", "mount_pitch_x_mm", "mount_pitch_y_mm"):
            v = _num(entry, key)
            if v is not None and v <= 0:
                print(f"  NON-POSITIVE DIM: {filepath}[{entry_id}].{key}={v} (use null for unknown, never 0)")
                errors += 1
    elif category == "psu":
        errors += _check_mount_group(entry_id, filepath, entry, "bottom_mount_",
                                     "length_mm", "width_mm")
        errors += _check_hole_count(entry_id, filepath, entry, "bottom_mount_")
        errors += _check_hole_count(entry_id, filepath, entry, "side_mount_")
        errors += _check_enum(entry_id, filepath, entry, "bottom_mount_pattern", PSU_MOUNT_PATTERN_VALUES)
        errors += _check_enum(entry_id, filepath, entry, "side_mount_pattern", PSU_MOUNT_PATTERN_VALUES)
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
                    "bottom_mount_max_penetration_mm", "side_mount_max_penetration_mm",
                    "bottom_mount_pitch_x_mm", "bottom_mount_pitch_y_mm", "side_mount_pitch_x_mm"):
            v = _num(entry, key)
            if v is not None and v <= 0:
                print(f"  NON-POSITIVE DIM: {filepath}[{entry_id}].{key}={v} (use null for unknown, never 0)")
                errors += 1
    elif category == "motors":
        errors += _check_motor_physics(entry_id, filepath, entry)
    elif category == "extruders":
        errors += _check_enum(entry_id, filepath, entry, "drive", EXTRUDER_DRIVE_VALUES, null_ok=False)
    elif category == "probes":
        errors += _check_enum(entry_id, filepath, entry, "type", PROBE_TYPE_VALUES, null_ok=False)
    elif category == "hotends":
        errors += _check_hotend_physics(entry_id, filepath, entry)
    return errors


def validate_file(filepath, required_fields, category=None):
    """Parse filepath once and validate its entries.

    Returns (errors, count, data) so callers (cross-file duplicate check,
    referential integrity) can reuse the already-parsed entries instead of
    re-opening and re-parsing the file.
    """
    try:
        with open(filepath) as f:
            data = yaml.load(f, Loader=StrictLoader)
    except yaml.YAMLError as e:
        print(f"  YAML ERROR: {filepath}: {e}")
        return 1, 0, []

    if data is None:
        data = []

    if not isinstance(data, list):
        print(f"  ERROR: {filepath} root must be a list")
        return 1, 0, []

    errors = 0
    ids_seen = set()

    for i, entry in enumerate(data):
        if not isinstance(entry, dict):
            print(f"  BAD ENTRY: {filepath}[index {i}] is not a mapping")
            errors += 1
            continue

        entry_id = entry.get("id", f"<index {i}>")

        if entry_id in ids_seen:
            print(f"  DUPLICATE ID: {entry_id} in {filepath}")
            errors += 1
        ids_seen.add(entry_id)

        for field in required_fields:
            if field not in entry:
                print(f"  MISSING FIELD: {filepath}[{entry_id}].{field}")
                errors += 1

        type_map = FIELD_TYPES.get(category, {}) if category is not None else {}
        for field, expected in type_map.items():
            v = entry.get(field)
            if v is not None and field in entry and not _TYPE_CHECKS[expected](v):
                print(f"  BAD TYPE: {filepath}[{entry_id}].{field}={v!r} must be {expected} (or null)")
                errors += 1

        if "id" in entry:
            if not isinstance(entry["id"], str):
                print(f"  BAD ID (not a string): {entry_id!r} in {filepath}")
                errors += 1
            elif " " in entry["id"]:
                print(f"  BAD ID (spaces): {entry_id} in {filepath}")
                errors += 1

        if category is not None:
            errors += check_physics(entry_id, filepath, entry, category)

    return errors, len(data), data


def _check_referential_integrity(entries_by_category):
    """Cross-category id references, run once all categories are loaded.

    entries_by_category maps category -> list of (filepath, entry) tuples
    for every entry that parsed as a mapping.
    """
    errors = 0

    def ids_for(category):
        return {
            entry.get("id")
            for _, entry in entries_by_category.get(category, [])
            if entry.get("id") is not None
        }

    motor_ids = ids_for("motors")
    extruder_ids = ids_for("extruders")
    hotend_ids = ids_for("hotends")

    for filepath, entry in entries_by_category.get("extruders", []):
        entry_id = entry.get("id", "<unknown>")
        motor_id = entry.get("motor_id")
        if motor_id is not None and motor_id not in motor_ids:
            print(f"  DANGLING REF: {filepath}[{entry_id}].motor_id={motor_id!r} not found in motors/")
            errors += 1

    for filepath, entry in entries_by_category.get("toolheads", []):
        entry_id = entry.get("id", "<unknown>")
        for x in entry.get("compatible_extruders") or []:
            if x not in extruder_ids:
                print(f"  DANGLING REF: {filepath}[{entry_id}].compatible_extruders contains {x!r} "
                      "not found in extruders/")
                errors += 1
        for x in entry.get("compatible_hotends") or []:
            if x not in hotend_ids:
                print(f"  DANGLING REF: {filepath}[{entry_id}].compatible_hotends contains {x!r} "
                      "not found in hotends/")
                errors += 1

    return errors


def main():
    print("Validating hardware database...\n")
    total_errors = 0
    total_entries = 0
    entries_by_category = {}

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

        cat_id_to_file = {}
        cat_entries = 0
        cat_entry_list = []
        for filepath in yaml_files:
            errors, count, data = validate_file(filepath, fields, category)
            total_errors += errors
            cat_entries += count

            seen_in_this_file = set()
            for entry in data:
                if not isinstance(entry, dict):
                    continue
                cat_entry_list.append((filepath, entry))
                eid = entry.get("id")
                if eid is None:
                    continue
                if eid in seen_in_this_file:
                    # Already reported as a within-file DUPLICATE ID.
                    continue
                seen_in_this_file.add(eid)
                if eid in cat_id_to_file and cat_id_to_file[eid] != filepath:
                    print(f"  CROSS-FILE DUPLICATE: {eid} in {category}/ "
                          f"({cat_id_to_file[eid]} and {filepath})")
                    total_errors += 1
                else:
                    cat_id_to_file.setdefault(eid, filepath)

        entries_by_category[category] = cat_entry_list
        total_entries += cat_entries
        print(f"  {category}/: {cat_entries} entries across {len(yaml_files)} files")

    total_errors += _check_referential_integrity(entries_by_category)

    print(f"\n{'PASSED' if total_errors == 0 else 'FAILED'} — {total_entries} total entries, {total_errors} errors")
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
