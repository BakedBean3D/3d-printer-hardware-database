#!/usr/bin/env python3
"""Validate all YAML data files against expected schemas."""
import datetime
import sys
import os
import glob
import yaml

ROOT = os.path.join(os.path.dirname(__file__), "..")


def _mount_region_margins():
    """The margins for "a hole lies on the body", from mount_region.yaml (the one place they are written)."""
    with open(os.path.join(ROOT, "mount_region.yaml")) as f:
        data = yaml.safe_load(f)
    return float(data["psu_edge_margin_mm"]), float(data["board_edge_margin_mm"])


PSU_EDGE_MARGIN_MM, BOARD_EDGE_MARGIN_MM = _mount_region_margins()


def _hole_on_board(x, y, length, width):
    """The one definition of "a drilled hole's centre lies on the board": strictly
    inside [0, length] x [0, width] widened by BOARD_EDGE_MARGIN_MM (0 today, so a
    centre exactly on an edge is rejected: a hole cannot be drilled on the edge)."""
    m = BOARD_EDGE_MARGIN_MM
    return -m < x < length + m and -m < y < width + m


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
    "id", "name", "manufacturer", "category", "mount_location",
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
    "id", "name", "manufacturer", "series", "category", "mount_locations",
    "length_mm", "width_mm", "height_mm", "weight_g", "wattage_w", "output_voltages_v",
    "bottom_mount_screw", "bottom_mount_interface", "bottom_mount_hole_dia_mm", "bottom_mount_hole_count",
    "bottom_mount_pattern", "bottom_mount_pitch_x_mm", "bottom_mount_pitch_y_mm", "bottom_mount_holes_xy",
    "bottom_mount_max_penetration_mm", "bottom_mount_slot_travel_mm",
    "side_mount_screw", "side_mount_hole_dia_mm", "side_mount_hole_count", "side_mount_pattern",
    "side_mount_pitch_x_mm", "side_mount_holes_xy", "side_mount_max_penetration_mm",
    "din_rail_compatible", "din_rail_type",
    "terminal_location", "terminal_faces", "mount_hole_frame",
    "connector_notes", "sources", "confidence", "notes",
]

CONFIDENCE_VALUES = {"high", "medium", "low"}

# reverify: optional {checked: "YYYY-MM-DD", outcome: <key below>} on a
# `confidence: low` record = the last re-verification pass that LEFT it low,
# and why. It is the one place that fact is recorded: the worklist
# (scripts/reverify_worklist.py) reads it to skip the record until it is due
# again, instead of re-hunting the same blocked entries every batch. The
# places checked stay in `notes`; the date and outcome live only here.
#   source_unreachable -- a primary source exists (or is cited) but could not
#                         be loaded from the verifying environment.
#   unpublished        -- the sources were reachable and read; the values (or
#                         the product itself) are not published anywhere.
# Value = days until the record is due for re-verification again. Absent =
# never re-verified = due now. Upgrading confidence off low removes the field.
REVERIFY_RECHECK_DAYS = {"source_unreachable": 90, "unpublished": 365}
REVERIFY_OUTCOME_VALUES = set(REVERIFY_RECHECK_DAYS)
REVERIFY_KEYS = ("checked", "outcome")
CONTROLLER_MOUNT_PATTERN_VALUES = {
    "rectangular", "L-shaped", "linear", "2-hole", "3-hole", "4-hole", "none", "other",
}

# WHERE THE DEVICE LIVES ON A PRINTER. Not a Partsmith/consumer policy and not
# a measurement -- a fact about the hardware, and the axis every mount
# generator has to filter on first, because the three take physically
# different parts:
#   bay      -- the electronics compartment. Includes boards that socket onto
#               a board that lives there (StepStick-footprint RTD amps, plug-in
#               drivers, mainboard daughterboards): they have no mount pattern
#               of their own, and where they end up is where their host is.
#   toolhead -- rides the printhead / moving carriage. Mass, cable strain and
#               chamber temperature all matter here and none of them matter in
#               a bay, which is why this is the split that earns a field.
#   frame    -- static and OUTSIDE the electronics bay: frame, gantry,
#               extrusion, front panel, bed, or an accessory unit's own chassis
#               (ERCF, Box Turtle).
# Required and NON-NULL, unlike the dimension fields. A dimension can be
# genuinely unmeasured; nobody adds a board record without knowing where the
# board goes, and a null here would silently drop the record out of every
# consumer's catalog -- the one failure mode worth designing out.
MOUNT_LOCATION_VALUES = {"bay", "toolhead", "frame"}
PSU_MOUNT_PATTERN_VALUES = {"rectangular", "2-hole", "3-hole", "other", "none"}

# WHERE A SUPPLY MAY BE INSTALLED. The psu counterpart of a board's
# mount_location, and a list because a board lives in one place while a
# supply is fitted in several: the same LRS-150 sits on a plate in the
# electronics bay or hangs on the frame from a bracket. Same vocabulary and
# meaning as MOUNT_LOCATION_VALUES, restricted to the two places a supply is
# ever installed (a supply never rides the toolhead):
#   bay   -- the electronics compartment (a plate on a DIN rail or panel, or
#            a rail clip for the DIN-rail units).
#   frame -- static and outside the bay: bolted to the printer's frame or an
#            upright by its own case holes.
# Required, non-empty and duplicate-free: a consumer decides from this field
# where it may offer the supply, so an empty list would silently drop it.
PSU_MOUNT_LOCATION_VALUES = {"bay", "frame"}

# v2 controlled vocabularies. drive is the transmission class (exact-match
# filterable); free-text flavor lives in type_detail. Probe type folds the
# sensing principle with the dock/deploy integration axis (mechanically
# distinct for CAD); scanning stays in scanning_capable — not duplicated here.
EXTRUDER_DRIVE_VALUES = {"dual_gear", "planetary", "worm", "belt"}
PROBE_TYPE_VALUES = {
    "contact", "contact_deploy", "contact_dock",
    "inductive", "inductive_dock", "eddy_current",
}
PSU_INTERFACE_VALUES = {"threaded_case", "clearance_ears"}

# terminal_faces: structured screw-terminal-block position(s), so consumers can
# chart them without parsing `terminal_location` prose. Expressed in the
# record's OWN body-origin frame (x along length_mm, y along width_mm, z along
# height_mm, origin at the same case corner the record's hole coordinates
# use) -- not a global convention, because DIN-rail units (MDR/EDR) describe
# their frame differently (see their notes) than the bolt-down enclosed units.
# null-able: leave null until a primary-source drawing has been read for that
# record (never guessed from series-family pattern-matching alone).
PSU_TERMINAL_FACE_VALUES = {
    "x_min_end", "x_max_end", "y_min_side", "y_max_side", "top", "bottom",
}
PSU_TERMINAL_CIRCUIT_VALUES = {"ac_in", "dc_in", "dc_out", "signal"}

# mount_hole_frame: makes explicit what terminal_faces already assumes -- the
# coordinate FRAME that bottom_mount_holes_xy / side_mount_holes_xy are given
# in. Free-text notes on individual records claim things like "x=0 at the
# terminal-block end, y=0 at the front long face" or "bottom-left case
# origin", but nothing structural let a consumer tell a case-corner frame
# (draw the real case rectangle around the holes) from a vendor-drawing datum
# that happens not to be case-relative. Two values only, plus null:
#   - case_corner    = x=0,y=0 at a case corner; x runs along length_mm, y
#                       along width_mm; every case-body point lies in
#                       [0, length_mm] x [0, width_mm]. Mounting ears/flanges
#                       that protrude past that rectangle are never admitted
#                       by a tolerance: the record states them in
#                       mount_footprint_mm (see _mount_region).
#   - vendor_drawing  = some other datum (a drawing-sheet origin, a
#                       non-case feature, an asymmetric convenience choice
#                       not tied to a case edge). Do NOT treat as
#                       case-relative -- a consumer cannot infer the case
#                       rectangle from these coordinates alone.
#   - null            = unknown / not yet established from the record's own
#                       provenance. Never guessed from a sibling record's
#                       case family.
PSU_MOUNT_HOLE_FRAME_VALUES = {"case_corner", "vendor_drawing"}

# mount_footprint_mm: optional psu box {x_min, x_max, y_min, y_max} in the
# record's own frame = the case rectangle plus the mounting ears/flanges that
# stand outside it. It is a recorded fact, not an allowance: holes must lie on
# the body or inside this box, and the box must contain the body and every hole.
# Only meaningful in a case_corner frame (a box needs a frame to be in).
PSU_MOUNT_FOOTPRINT_KEYS = ("x_min", "x_max", "y_min", "y_max")

# Declarative enum registry: category -> field -> (allowed values, null_ok).
# The single source for both the runtime enum checks and the generated JSON
# Schemas (scripts/gen_schema.py) — add enums here, not as ad-hoc checks.
BOARD_MOUNT_HOLE_FRAME_VALUES = {"pcb_corner"}

ENUM_FIELDS = {
    "motors": {},
    "hotends": {},
    "extruders": {"drive": (EXTRUDER_DRIVE_VALUES, False)},
    "probes": {"type": (PROBE_TYPE_VALUES, False)},
    "toolheads": {},
    "controller_boards": {
        "mount_pattern": (CONTROLLER_MOUNT_PATTERN_VALUES, True),
        "mount_location": (MOUNT_LOCATION_VALUES, False),
        # Optional (absent = null = unknown): the frame mount_holes_xy are
        # given in. "pcb_corner" licenses a consumer to draw the PCB rectangle
        # [0, pcb_length_mm] x [0, pcb_width_mm] around the holes, i.e. the
        # exact board footprint (2026-10-01; the board counterpart of the psu
        # case_corner frame). Never inferred from positive coordinates.
        "mount_hole_frame": (BOARD_MOUNT_HOLE_FRAME_VALUES, True),
    },
    "psu": {
        "bottom_mount_pattern": (PSU_MOUNT_PATTERN_VALUES, True),
        "side_mount_pattern": (PSU_MOUNT_PATTERN_VALUES, True),
        # bottom_mount_interface: what the case-side holes physically are.
        # A mount generator that threads into "clearance_ears" (UHP class)
        # produces a part that cannot fasten at all — never guessed. The
        # conditional rules (required when bottom_mount_screw is set;
        # threaded_case requires a penetration depth) stay in check_physics.
        "bottom_mount_interface": (PSU_INTERFACE_VALUES, True),
        "mount_hole_frame": (PSU_MOUNT_HOLE_FRAME_VALUES, True),
    },
}
# Enumerated LIST fields: category -> field -> allowed members. The list must be
# non-empty and hold each member at most once. Like ENUM_FIELDS this is the
# single source for the runtime check and the generated JSON Schema.
LIST_ENUM_FIELDS = {
    "psu": {"mount_locations": PSU_MOUNT_LOCATION_VALUES},
}

for _cat_enums in ENUM_FIELDS.values():
    _cat_enums["confidence"] = (CONFIDENCE_VALUES, False)

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
_T_STR, _T_NUM, _T_INT, _T_BOOL, _T_LIST, _T_MAP = (
    "string", "number", "integer", "bool", "list", "map")

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
    "mount_hole_frame": _T_STR,
    "stack_mounts": _T_LIST,
}

PSU_FIELD_TYPES = {
    "id": _T_STR, "name": _T_STR, "manufacturer": _T_STR, "series": _T_STR,
    "category": _T_STR, "mount_locations": _T_LIST,
    "bottom_mount_screw": _T_STR, "bottom_mount_interface": _T_STR,
    "bottom_mount_pattern": _T_STR, "side_mount_screw": _T_STR,
    "side_mount_pattern": _T_STR, "din_rail_type": _T_STR,
    "terminal_location": _T_STR, "mount_hole_frame": _T_STR, "connector_notes": _T_STR,
    "confidence": _T_STR, "notes": _T_STR,
    "length_mm": _T_NUM, "width_mm": _T_NUM, "height_mm": _T_NUM,
    "weight_g": _T_NUM, "wattage_w": _T_NUM,
    "bottom_mount_hole_dia_mm": _T_NUM, "bottom_mount_pitch_x_mm": _T_NUM,
    "bottom_mount_pitch_y_mm": _T_NUM, "bottom_mount_max_penetration_mm": _T_NUM,
    "side_mount_hole_dia_mm": _T_NUM, "side_mount_pitch_x_mm": _T_NUM,
    "side_mount_max_penetration_mm": _T_NUM,
    "bottom_mount_hole_count": _T_INT, "side_mount_hole_count": _T_INT,
    "output_voltages_v": _T_LIST, "bottom_mount_holes_xy": _T_LIST,
    "side_mount_holes_xy": _T_LIST, "terminal_faces": _T_LIST,
    "mount_footprint_mm": _T_MAP,
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

for _cat_types in FIELD_TYPES.values():
    _cat_types["reverify"] = _T_MAP

# bool is an int subclass in Python — exclude it from the numeric types so
# `weight: true` can never pass as a number.
_TYPE_CHECKS = {
    _T_STR: lambda v: isinstance(v, str),
    _T_NUM: lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    _T_INT: lambda v: isinstance(v, int) and not isinstance(v, bool),
    _T_BOOL: lambda v: isinstance(v, bool),
    _T_LIST: lambda v: isinstance(v, list),
    _T_MAP: lambda v: isinstance(v, dict),
}


def _num(entry, key):
    """Value of a numeric field, or None if absent/null/non-numeric."""
    v = entry.get(key)
    return v if isinstance(v, (int, float)) else None


def _mount_region(entry, L, W):
    """The one owner of where a mounting hole may stand: {"x": (lo, hi), "y": (lo, hi)}
    in the record's frame. A record that states mount_footprint_mm (body plus
    ears/flanges, a recorded fact) is bounded by that box; every other record
    by its body rectangle widened by PSU_EDGE_MARGIN_MM (mount_region.yaml) for edge-breaking chamfers. There is
    deliberately no per-interface allowance: a hole outside the body is either
    inside a stated footprint or an error."""
    fp = entry.get("mount_footprint_mm")
    if isinstance(fp, dict) and all(isinstance(fp.get(k), (int, float)) and not isinstance(fp.get(k), bool)
                                    for k in PSU_MOUNT_FOOTPRINT_KEYS):
        return {"x": (fp["x_min"], fp["x_max"]), "y": (fp["y_min"], fp["y_max"])}
    m = PSU_EDGE_MARGIN_MM
    return {"x": (-m, None if L is None else L + m), "y": (-m, None if W is None else W + m)}


def _check_mount_footprint(entry_id, filepath, entry):
    """Structure of the optional psu `mount_footprint_mm` box: exactly the four
    numeric keys, min < max, only in a case_corner frame, containing the whole
    case body. Whether the holes lie inside it is _mount_region's job (shared by
    the group and frame checks), so a box that does not contain the holes fails
    there as HOLE OFF PART."""
    fp = entry.get("mount_footprint_mm")
    if fp is None:
        return 0
    tag = f"{filepath}[{entry_id}].mount_footprint_mm"
    if not isinstance(fp, dict):
        return 0  # reported as BAD TYPE by the generic type check
    if set(fp) != set(PSU_MOUNT_FOOTPRINT_KEYS):
        print(f"  BAD FOOTPRINT: {tag} keys must be exactly {list(PSU_MOUNT_FOOTPRINT_KEYS)}")
        return 1
    if any(isinstance(fp[k], bool) or not isinstance(fp[k], (int, float)) for k in fp):
        print(f"  BAD FOOTPRINT: {tag} values must be numbers")
        return 1
    errors = 0
    if entry.get("mount_hole_frame") != "case_corner":
        print(f"  FOOTPRINT WITHOUT FRAME: {tag} needs mount_hole_frame=case_corner")
        errors += 1
    if not (fp["x_min"] < fp["x_max"] and fp["y_min"] < fp["y_max"]):
        print(f"  BAD FOOTPRINT: {tag} needs x_min < x_max and y_min < y_max")
        errors += 1
    L, W = _num(entry, "length_mm"), _num(entry, "width_mm")
    if L is not None and W is not None and not (
            fp["x_min"] <= 0 and fp["x_max"] >= L and fp["y_min"] <= 0 and fp["y_max"] >= W):
        print(f"  FOOTPRINT INSIDE BODY: {tag} must contain the case 0..{L} x 0..{W}")
        errors += 1
    return errors


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
        # holes must lie on the part (PSU_EDGE_MARGIN_MM for edge-breaking chamfers)
        # or, when the record states one, inside its mount_footprint_mm (see
        # _mount_region). Clearance ears stand outside the case, so their
        # position is only checkable against a case frame and a stated
        # footprint; a record with ears and no frame is incomplete.
        if entry.get(prefix + "interface") == "clearance_ears" and entry.get("mount_hole_frame") is None:
            print(f"  EARS WITHOUT FRAME: {tag} clearance ears need mount_hole_frame case_corner and mount_footprint_mm")
            return errors + 1
        region = _mount_region(entry, L, W)
        for lo_hi, dim, axis in ((xs, L, "x"), (ys, W, "y")):
            if dim is None:
                continue
            lo, hi = region[axis]
            for v in lo_hi:
                if v < lo or (hi is not None and v > hi):
                    print(f"  HOLE OFF PART: {tag} {axis}={v} outside {lo}..{hi}")
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


def _check_list_enum(entry_id, filepath, entry, key, allowed):
    """A required enumerated list: present, a non-empty list, every member allowed, none repeated."""
    v = entry.get(key)
    tag = f"{filepath}[{entry_id}].{key}"
    if not isinstance(v, list) or not v:
        print(f"  BAD LIST ENUM (must be a non-empty list): {tag}={v!r}")
        return 1
    errors = 0
    for member in v:
        if member not in allowed:
            print(f"  BAD LIST ENUM: {tag} member {member!r} not in {sorted(allowed)}")
            errors += 1
    if len(set(map(str, v))) != len(v):
        print(f"  BAD LIST ENUM: {tag}={v!r} repeats a member")
        errors += 1
    return errors


def _check_terminal_faces(entry_id, filepath, entry):
    """Structural checks for the optional psu `terminal_faces` list.

    Each item is {face, circuits, notes}: face is a single-valued enum (one
    entry per physical face -- a duplicate face means two conflicting claims
    about the same wall), circuits is a non-empty list drawn from the
    controlled vocabulary (an empty/missing circuits list is meaningless --
    a face with no assigned circuit isn't a terminal face), and notes, when
    present, must be a string. null (the whole field, not an empty list) is
    how an unverified record stays unverified.
    """
    tf = entry.get("terminal_faces")
    if tf is None:
        return 0
    tag = f"{filepath}[{entry_id}].terminal_faces"
    if not isinstance(tf, list):
        return 0  # already reported as BAD TYPE by the generic type check
    if not tf:
        print(f"  EMPTY TERMINAL_FACES: {tag} must be null (unverified) or a non-empty list")
        return 1
    errors = 0
    seen_faces = set()
    for i, item in enumerate(tf):
        itag = f"{tag}[{i}]"
        if not isinstance(item, dict):
            print(f"  MALFORMED TERMINAL_FACE: {itag} is not a mapping")
            errors += 1
            continue
        face = item.get("face")
        if face not in PSU_TERMINAL_FACE_VALUES:
            print(f"  BAD ENUM: {itag}.face={face!r} not in {sorted(PSU_TERMINAL_FACE_VALUES)}")
            errors += 1
        elif face in seen_faces:
            print(f"  DUPLICATE TERMINAL FACE: {itag}.face={face!r} already appears "
                  f"in {tag} -- merge into one entry")
            errors += 1
        else:
            seen_faces.add(face)
        circuits = item.get("circuits")
        if not isinstance(circuits, list) or not circuits:
            print(f"  MISSING CIRCUITS: {itag}.circuits must be a non-empty list")
            errors += 1
        else:
            for c in circuits:
                if c not in PSU_TERMINAL_CIRCUIT_VALUES:
                    print(f"  BAD ENUM: {itag}.circuits contains {c!r} not in "
                          f"{sorted(PSU_TERMINAL_CIRCUIT_VALUES)}")
                    errors += 1
        notes = item.get("notes")
        if notes is not None and not isinstance(notes, str):
            print(f"  BAD TYPE: {itag}.notes={notes!r} must be string (or null)")
            errors += 1
    return errors


STACK_MOUNT_KEYS = {"kind", "screw", "hole_dia_mm", "pitch_x_mm", "pitch_y_mm", "holes_xy",
                    "standoff_height_mm", "sources", "notes"}


def _check_stack_mounts(entry_id, filepath, entry):
    """Structural checks for the optional board `stack_mounts` list: the places
    ANOTHER board stacks onto this one on standoffs (a Raspberry Pi on the LDO
    Leviathan). Each item names the guest's category (`kind`), the guest's
    screw, the clearance-hole diameter on THIS board, the guest's own hole
    pitches (so a consumer matches a guest's record by pitch and screw, never
    by id) and `holes_xy`: the standoff holes in THIS board's pcb_corner frame
    (x along pcb_length_mm, y along pcb_width_mm). Every hole must lie inside
    the PCB, and the span of holes_xy must equal the stated pitches (a pattern
    that disagrees with its own pitch is a transcription error)."""
    sm = entry.get("stack_mounts")
    if sm is None:
        return 0
    tag = f"{filepath}[{entry_id}].stack_mounts"
    if not isinstance(sm, list) or not sm:
        print(f"  EMPTY STACK_MOUNTS: {tag} must be null/absent or a non-empty list")
        return 1
    errors = 0
    L, W = _num(entry, "pcb_length_mm"), _num(entry, "pcb_width_mm")
    for i, item in enumerate(sm):
        itag = f"{tag}[{i}]"
        if not isinstance(item, dict) or set(item) != STACK_MOUNT_KEYS:
            print(f"  MALFORMED STACK_MOUNT: {itag} must be a mapping with exactly {sorted(STACK_MOUNT_KEYS)}")
            errors += 1
            continue
        if not isinstance(item["kind"], str) or not isinstance(item["screw"], str):
            print(f"  BAD TYPE: {itag}.kind and .screw must be strings")
            errors += 1
        for key in ("hole_dia_mm", "pitch_x_mm", "pitch_y_mm"):
            v = item[key]
            if not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0:
                print(f"  NON-POSITIVE DIM: {itag}.{key}={v!r}")
                errors += 1
        sh = item["standoff_height_mm"]
        if sh is not None and (not isinstance(sh, (int, float)) or isinstance(sh, bool) or sh <= 0):
            print(f"  NON-POSITIVE DIM: {itag}.standoff_height_mm={sh!r} (use null for unknown, never 0)")
            errors += 1
        holes = item["holes_xy"]
        if not (isinstance(holes, list) and len(holes) == 4
                and all(isinstance(h, list) and len(h) == 2 for h in holes)):
            print(f"  BAD HOLES: {itag}.holes_xy must be four [x, y] pairs")
            errors += 1
            continue
        xs, ys = sorted({h[0] for h in holes}), sorted({h[1] for h in holes})
        if len(xs) != 2 or len(ys) != 2 or abs((xs[1] - xs[0]) - item["pitch_x_mm"]) > 0.01 \
                or abs((ys[1] - ys[0]) - item["pitch_y_mm"]) > 0.01:
            print(f"  STACK PITCH MISMATCH: {itag}.holes_xy spans {xs}, {ys}, not {item['pitch_x_mm']} x {item['pitch_y_mm']}")
            errors += 1
        if L is None or W is None:
            print(f"  STACK_MOUNTS WITHOUT OUTLINE: {itag} needs pcb_length_mm and pcb_width_mm")
            errors += 1
        else:
            for x, y in holes:
                if not _hole_on_board(x, y, L, W):
                    print(f"  STACK HOLE OUTSIDE PCB: {itag} ({x}, {y}) not inside 0..{L} x 0..{W}")
                    errors += 1
        if not isinstance(item["sources"], list) or not item["sources"]:
            print(f"  MISSING SOURCES: {itag}.sources must be a non-empty list")
            errors += 1
    return errors


def _check_board_mount_hole_frame(entry_id, filepath, entry):
    """A board claiming mount_hole_frame=pcb_corner must have every hole on
    the PCB: strictly inside [0, pcb_length_mm] x [0, pcb_width_mm] widened by
    BOARD_EDGE_MARGIN_MM (mount_region.yaml, 0). Holes are drilled through the
    board, so unlike PSU case chamfers there is no tolerance past the edge; a
    hole on or off the edge means the frame claim is wrong."""
    if entry.get("mount_hole_frame") != "pcb_corner":
        return 0
    errors = 0
    L, W = _num(entry, "pcb_length_mm"), _num(entry, "pcb_width_mm")
    holes = entry.get("mount_holes_xy")
    tag = f"{filepath}[{entry_id}].mount_hole_frame"
    if L is None or W is None or not isinstance(holes, list) or not holes:
        print(f"  PCB_CORNER WITHOUT GEOMETRY: {tag} needs pcb_length_mm, pcb_width_mm and mount_holes_xy")
        return 1
    for h in holes:
        if not (isinstance(h, (list, tuple)) and len(h) == 2):
            continue
        x, y = h
        if not _hole_on_board(x, y, L, W):
            print(f"  HOLE OUTSIDE PCB_CORNER FRAME: {tag} ({x}, {y}) not inside 0..{L} x 0..{W}")
            errors += 1
    return errors


def _check_mount_hole_frame(entry_id, filepath, entry):
    """When mount_hole_frame=case_corner, every declared hole coordinate must
    lie in the record's mount region (_mount_region: the case rectangle, or the
    stated mount_footprint_mm). This is the structural payoff of the field: a
    consumer trusts it to draw the real case rectangle around the holes, so a
    case_corner claim that puts a hole off the case is worse than no claim at
    all. The bottom group is range-checked by _check_mount_group through the same
    region; this covers the side group, which has no other range check."""
    if entry.get("mount_hole_frame") != "case_corner":
        return 0
    errors = 0
    region = _mount_region(entry, _num(entry, "length_mm"), _num(entry, "width_mm"))
    tag = f"{filepath}[{entry_id}].mount_hole_frame"
    holes = entry.get("side_mount_holes_xy")
    if not isinstance(holes, list):
        return 0
    for h in holes:
        if not (isinstance(h, (list, tuple)) and len(h) == 2):
            continue  # already reported by the generic type check
        for axis, v in (("x", h[0]), ("y", h[1])):
            if not isinstance(v, (int, float)):
                continue
            lo, hi = region[axis]
            if (hi is not None and v > hi) or v < lo:
                print(f"  HOLE OUTSIDE CASE_CORNER FRAME: {tag}=side_mount_holes_xy {axis}={v} "
                      f"outside {lo}..{hi}")
                errors += 1
    return errors


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


def reverify_checked(entry):
    """The record's reverify.checked as a date, or None when absent or malformed
    (malformed is reported by _check_reverify). Shared with the worklist."""
    rv = entry.get("reverify")
    if not isinstance(rv, dict) or not isinstance(rv.get("checked"), str):
        return None
    try:
        return datetime.date.fromisoformat(rv["checked"])
    except ValueError:
        return None


def _check_reverify(entry_id, filepath, entry):
    """Structure of the optional `reverify` map: exactly checked + outcome, a
    quoted ISO date not in the future, an outcome from REVERIFY_RECHECK_DAYS,
    and only on a confidence: low record (it records why the record is still low)."""
    rv = entry.get("reverify")
    if rv is None:
        return 0
    tag = f"{filepath}[{entry_id}].reverify"
    errors = 0
    if not isinstance(rv, dict):
        return 0  # reported as BAD TYPE
    if set(rv) != set(REVERIFY_KEYS):
        print(f"  BAD REVERIFY: {tag} keys {sorted(rv)} must be exactly {list(REVERIFY_KEYS)}")
        errors += 1
    checked = reverify_checked(entry)
    if checked is None:
        print(f"  BAD REVERIFY: {tag}.checked={rv.get('checked')!r} must be a quoted 'YYYY-MM-DD' date")
        errors += 1
    elif checked > datetime.date.today():
        print(f"  BAD REVERIFY: {tag}.checked={checked} is in the future")
        errors += 1
    if rv.get("outcome") not in REVERIFY_OUTCOME_VALUES:
        print(f"  BAD REVERIFY: {tag}.outcome={rv.get('outcome')!r} not in {sorted(REVERIFY_OUTCOME_VALUES)}")
        errors += 1
    if entry.get("confidence") != "low":
        print(f"  STALE REVERIFY: {tag} is set but confidence={entry.get('confidence')!r}; "
              "it records why a low record stays low -- remove it when upgrading")
        errors += 1
    return errors


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
    errors = 0
    for field, (allowed, null_ok) in ENUM_FIELDS.get(category, {}).items():
        errors += _check_enum(entry_id, filepath, entry, field, allowed, null_ok=null_ok)
    for field, allowed in LIST_ENUM_FIELDS.get(category, {}).items():
        errors += _check_list_enum(entry_id, filepath, entry, field, allowed)
    errors += _check_confidence_provenance(entry_id, filepath, entry)
    errors += _check_reverify(entry_id, filepath, entry)
    if category == "controller_boards":
        errors += _check_mount_group(entry_id, filepath, entry, "mount_",
                                     "pcb_length_mm", "pcb_width_mm")
        errors += _check_hole_count(entry_id, filepath, entry, "mount_")
        errors += _check_board_mount_hole_frame(entry_id, filepath, entry)
        errors += _check_stack_mounts(entry_id, filepath, entry)
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
        errors += _check_terminal_faces(entry_id, filepath, entry)
        errors += _check_mount_footprint(entry_id, filepath, entry)
        errors += _check_mount_hole_frame(entry_id, filepath, entry)
        # bottom_mount_interface conditional rules (the value enum itself is
        # covered by ENUM_FIELDS): a record with a bottom screw size MUST
        # declare the interface, and a threaded case needs a safety depth.
        iface = entry.get("bottom_mount_interface")
        tag = f"{filepath}[{entry_id}].bottom_mount_interface"
        if entry.get("bottom_mount_screw") is not None and iface is None:
            print(f"  MISSING INTERFACE: {tag} must be declared when "
                  "bottom_mount_screw is set")
            errors += 1
        if iface == "threaded_case" and _num(entry, "bottom_mount_max_penetration_mm") is None:
            print(f"  MISSING PENETRATION: {tag}=threaded_case requires "
                  "bottom_mount_max_penetration_mm (thread-in safety depth)")
            errors += 1
        # clearance_ears is an OPEN feature, so how far the screw may travel along
        # it is part of the interface, not a detail. Without it a consumer cannot
        # tell whether its screw sits at the enclosed end or halfway out of the
        # mouth — a UHP-350 plate was printed and held before anyone noticed the
        # feature was a 2 mm slot rather than a round hole (2026-09-02).
        travel = _num(entry, "bottom_mount_slot_travel_mm")
        if iface == "clearance_ears" and travel is None:
            print(f"  MISSING SLOT TRAVEL: {tag}=clearance_ears requires "
                  "bottom_mount_slot_travel_mm (screw-centre travel from the "
                  "recorded closed end toward the ear's open mouth; 0 if the "
                  "feature is a round hole)")
            errors += 1
        if iface != "clearance_ears" and travel is not None:
            print(f"  UNEXPECTED SLOT TRAVEL: {tag}={iface!r} carries "
                  "bottom_mount_slot_travel_mm — only open ear slots have travel")
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
