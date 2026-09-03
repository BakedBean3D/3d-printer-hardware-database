# 3D Printer Hardware Database

Community-maintained database of 3D printer hardware specifications for Klipper-based printers.

Covers stepper motors, hotends, extruders, toolheads, probes, controller-board mounting dimensions, and power-supply mounting dimensions — focused on the Voron, RatRig, Annex, and RepRap ecosystem.

## Directory Structure

```
motors/                  # Split by manufacturer
  ldo.yaml
  moons.yaml
  omc.yaml
  ...
hotends/                 # Split by manufacturer
  phaetus.yaml
  e3d.yaml
  slice_engineering.yaml
  ...
probes/                  # Split by manufacturer
  beacon3d.yaml
  antclabs.yaml
  ...
extruders/               # Single file (community designs)
  extruders.yaml
toolheads/               # Single file (community designs)
  toolheads.yaml
controller_boards/       # PCB mounting dimensions, split by manufacturer
  bigtreetech.yaml
  fysetc.yaml
  duet3d.yaml
  makerbase.yaml
  mellow.yaml
  ldo.yaml
  community.yaml         # github-username designs (Huvud, HartK, Enraged Rabbit, timmit99, ...)
  modules.yaml           # generic add-on modules (StepStick drivers, RTD amps, accelerometers, relays)
  controller_boards.json # generated aggregate (run gen.py)
  CONTROLLER_BOARDS.md   # generated human-readable reference
  gen.py                 # regenerates the .json + .md from the YAML
psu/                     # Power supply mounting dimensions, split by manufacturer
  meanwell.yaml
  psu.json               # generated aggregate (run gen.py)
  PSU.md                 # generated human-readable reference
  gen.py                 # regenerates the .json + .md from the YAML
```

Hardware with clear brand ownership (motors, hotends, probes, controller boards) is split by manufacturer — one file per brand. Community/open-source designs (extruders, toolheads, and community PCBs) stay in a single file since "manufacturer" is often just a GitHub username.

### Controller board fields

PCB mounting geometry for parametric CAD mount design. **`null` means genuinely unknown — never assume 0** (a 0 mm dimension reads as real). After editing any YAML, run `python controller_boards/gen.py` to refresh the JSON aggregate and markdown.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (lowercase, underscores) |
| `name` | string | Board name |
| `manufacturer` | string | Brand or GitHub username |
| `category` | string | mainboard, toolhead_can, sbc, usb_can_bridge, driver_module, thermocouple_amp, accelerometer, relay, ssr, buck_converter, mosfet, sensor, expander, ercf, accessory |
| `pcb_length_mm` | float | X — longer edge |
| `pcb_width_mm` | float | Y — shorter edge |
| `pcb_thickness_mm` | float | PCB thickness (defaults to 1.6 where unstated) |
| `mount_screw` | string | Screw that fits the holes (M3, M2.5, ...; null if header-mounted) |
| `mount_hole_dia_mm` | float | Hole diameter (often inferred from screw size) |
| `mount_pattern` | string | rectangular, L-shaped, linear, 2-hole, 3-hole, 4-hole, none, other |
| `mount_pitch_x_mm` / `mount_pitch_y_mm` | float | Center-to-center hole spacing |
| `mount_hole_count` | int | Number of mounting holes |
| `mount_holes_xy` | list | Optional `[[x,y], ...]` from PCB bottom-left corner (read `notes`) |
| `mount_inset_from_edge_mm` | float | Hole-center distance in from the PCB edge |
| `standoff_height_mm` | float | Recommended clearance under the board |
| `component_height_top_mm` | float | Tallest component / module body height above board |
| `connector_notes` | string | Which edge carries power / steppers / USB / etc. |
| `sources` | list | Datasheet / GitHub hardware repo / KiCad URLs |
| `confidence` | string | high (vendor/community CAD), medium (outline firm, pitch inferred), low (measure first) |
| `notes` | string | Source citation + anything to double-check |

### PSU fields

Power-supply mounting geometry for parametric mount generation (enclosure cutouts, bracket clips, DIN-rail carriers). **`null` means genuinely unknown — never assume 0.** After editing any YAML, run `python psu/gen.py` to refresh the JSON aggregate and markdown.

Every enclosed/slim_enclosed unit carries **two** mount patterns — `bottom_mount_*` (the vertical-entry hole pattern used for flat/plate mounting; the one almost every printer mount uses) and `side_mount_*` (the vendor's second documented pattern — a true horizontal side-wall entry on the larger LRS-200/350/RSP-500 case family, or a second vertical top-flange pattern on the smaller LRS-50/100/150 case family). Read each record's `notes` to know which physical face `side_mount` refers to — it is not always a horizontal entry. DIN-rail units (MDR/EDR series) clip onto a rail instead of bolting down; they carry `din_rail_compatible`/`din_rail_type` and leave both mount-pattern groups `none`.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (lowercase, underscores) |
| `name` | string | Unit name |
| `manufacturer` | string | Brand |
| `series` | string | Product series (e.g. LRS-50, RSP-500) |
| `category` | string | enclosed, slim_enclosed, din_rail |
| `length_mm` / `width_mm` / `height_mm` | float | Case dimensions. DIN-rail units use the vendor's W×H×D convention, remapped length=D, width=W, height=H (see `notes`) |
| `weight_g` | int | Weight in grams |
| `wattage_w` | int | Nominal series wattage (exact rated power varies slightly per output voltage — see `notes`) |
| `output_voltages_v` | list | Available DC output voltage variants in this series |
| `bottom_mount_screw` / `side_mount_screw` | string | Screw that fits the holes (M3, M4, ...; null if not applicable) |
| `bottom_mount_interface` | string | What the case-side holes physically are: threaded_case (screw threads into the case) or clearance_ears (through-holes in mounting ears) — must be declared whenever `bottom_mount_screw` is set |
| `bottom_mount_hole_dia_mm` / `side_mount_hole_dia_mm` | float | Hole diameter (often inferred from screw size) |
| `bottom_mount_hole_count` / `side_mount_hole_count` | int | Number of mounting holes in that pattern |
| `bottom_mount_pattern` / `side_mount_pattern` | string | rectangular, 2-hole, 3-hole, other, none |
| `bottom_mount_pitch_x_mm` / `bottom_mount_pitch_y_mm` / `side_mount_pitch_x_mm` | float | Center-to-center hole spacing |
| `bottom_mount_holes_xy` / `side_mount_holes_xy` | list | Optional `[[x,y], ...]` from the case's bottom-left corner (read `notes`) — populated only where the vendor drawing gave clean, cross-validated dimensions |
| `bottom_mount_max_penetration_mm` / `side_mount_max_penetration_mm` | float | Max screw length into the case before risking the internal PCB — a safety spec, not just a fit spec |
| `bottom_mount_slot_travel_mm` | float | Screw-centre travel along an open ear SLOT, from the recorded `bottom_mount_holes_xy` position (the slot's CLOSED end) toward the ear's open mouth. Required for `bottom_mount_interface: clearance_ears`, null otherwise — it is how a consumer tells a slot from a round hole |
| `din_rail_compatible` | bool | True for spring-clip DIN-rail units (MDR/EDR series) |
| `din_rail_type` | string | Admissible rail profile (e.g. "TS35/7.5 or TS35/15") |
| `terminal_location` | string | Where the AC/DC terminal block(s) sit relative to the mounting face(s) |
| `connector_notes` | string | Terminal pinout, connector part numbers, fan/thermal notes |
| `sources` | list | Manufacturer datasheet/mechanical-drawing URLs |
| `confidence` | string | high (vector-PDF extracted, cross-validated), medium (case dims + screw/depth verified, exact hole XY unresolved), low (measure first) |
| `notes` | string | Source citation + anything to double-check |

## Schema

Each hardware category has a defined set of fields, enforced by `scripts/validate.py` — the per-category required-field lists live at the top of that script. Run `python3 scripts/validate.py` to validate the whole database.

Machine-readable JSON Schemas (draft 2020-12) for every category live in [`schema/`](schema/) — generated from `validate.py` by `scripts/gen_schema.py` (CI keeps them in sync; never hand-edited), so downstream consumers can validate without running this repo's tooling. They cover structure, types, and enums; the physics/plausibility gates only exist in `validate.py`.

> **v2 field names:** as of v2.0.0 every weight field is `weight_g`, extruders use the `drive` enum + `type_detail`, and probe `type` is a controlled vocabulary. The `v1` git tag is the last release with the old field names (`weight`; free-text `type`).

### Motor fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (lowercase, underscores) |
| `name` | string | Official manufacturer name |
| `manufacturer` | string | Brand |
| `frame_size` | string | NEMA14, NEMA17, NEMA23 |
| `body_length_mm` | float | Motor body length in mm |
| `rated_current_amps` | float | Rated RMS current per phase |
| `recommended_run_current` | float | Klipper `run_current` (RMS) |
| `holding_torque_ncm` | float | Holding torque in N·cm |
| `inductance_mh` | float | Phase inductance in mH |
| `resistance_ohms` | float | Phase resistance in Ohms |
| `step_angle` | float | Degrees per full step (1.8 or 0.9) |
| `weight_g` | int | Weight in grams |
| `tooth_count` | int | Integrated pinion teeth (0 = none) |
| `datasheet_url` | string | Link to manufacturer datasheet |
| `confidence` | string | high, medium, low — see [Confidence tiers](#confidence-tiers) |
| `notes` | string | Verification source and usage context |

### Hotend fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (lowercase, underscores) |
| `name` | string | Hotend name |
| `manufacturer` | string | Brand |
| `meltzone_length` | float | Melt zone length in mm (start of melt zone to nozzle tip) |
| `max_volumetric_flow` | float | Max flow in mm³/s (0.4 mm nozzle PLA baseline unless noted) |
| `max_temp` | int | Rated max temperature in °C |
| `recommended_temp_pla` / `recommended_temp_abs` / `recommended_temp_petg` | int | Recommended print temps in °C |
| `nozzle_thread` | string | Nozzle thread standard (M6, V6, Volcano, proprietary, ...) |
| `weight_g` | float | Weight in grams |
| `recommended_max_speed` | int | Recommended max print speed in mm/s |
| `confidence` | string | high, medium, low — see [Confidence tiers](#confidence-tiers) |
| `notes` | string | Verification source and usage context |

### Extruder fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (lowercase, underscores) |
| `name` | string | Extruder name |
| `manufacturer` | string | Brand or GitHub username |
| `drive` | string | Transmission class: dual_gear, planetary, worm, belt |
| `type_detail` | string | Free-text flavor (e.g. "Dual Gear BMG Style") |
| `gear_ratio` | string | Reduction ratio (e.g. "50:10") |
| `rotation_distance` | float | Klipper rotation_distance |
| `uses_gear_ratio_in_config` | bool | Whether printer.cfg uses gear_ratio separately |
| `motor` | string | Motor description |
| `motor_id` | string | Optional cross-reference to a motors/ entry id |
| `motor_current` | float | Recommended run current (RMS) |
| `max_speed` | int | Max print speed in mm/s |
| `max_accel` | int | Max acceleration in mm/s² |
| `weight_g` | float | Weight in grams |
| `filament_path_length` | float | Filament path length in mm |
| `recommended_pressure_advance` | float | Typical Klipper pressure_advance |
| `confidence` | string | high, medium, low — see [Confidence tiers](#confidence-tiers) |
| `notes` | string | Verification source and usage context |

### Probe fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (lowercase, underscores) |
| `name` | string | Probe name |
| `manufacturer` | string | Brand or project |
| `type` | string | contact, contact_deploy, contact_dock, inductive, inductive_dock, eddy_current |
| `accuracy` | float | Accuracy in mm |
| `repeatability` | float | Repeatability (std dev) in mm |
| `z_offset_typical` | float | Typical Z offset in mm |
| `speed` | int | Probing speed in mm/s |
| `samples` | int | Recommended sample count |
| `sample_retract_dist` | float | Retract distance between samples in mm |
| `scanning_capable` | bool | True for surface-scanning (mesh without touching) probes |
| `confidence` | string | high, medium, low — see [Confidence tiers](#confidence-tiers) |
| `notes` | string | Verification source and usage context |

### Toolhead fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier (lowercase, underscores) |
| `name` | string | Toolhead name |
| `manufacturer` | string | Design project or GitHub username |
| `compatible_extruders` | list | extruders/ entry ids (referential integrity enforced) |
| `compatible_hotends` | list | hotends/ entry ids (referential integrity enforced) |
| `compatible_printer_types` | list | Printer families the toolhead targets |
| `weight_g` | float | Weight in grams |
| `fan_config` | string | Part-cooling / hotend fan arrangement |
| `part_cooling_cfm` | float | Part-cooling airflow in CFM |
| `supports_neopixels` / `supports_klicky` / `supports_tap` | bool | Accessory support flags |
| `mounting_method` | string | Carriage / rail mounting |
| `confidence` | string | high, medium, low — see [Confidence tiers](#confidence-tiers) |
| `notes` | string | Verification source and usage context |

## Safety Notice

This data is used to configure expensive 3D printers. Incorrect motor currents can damage drivers or motors. Incorrect flow rates can cause jams or failed prints.

**Every spec must cite its source** in the `notes` field. Acceptable citations:
- Manufacturer datasheet (Tier 1)
- Trusted retailer tested (Tier 2)
- Community tested / estimated (Tier 3)

### Confidence tiers

Every entry in every category carries a required `confidence` field summarizing
the provenance of its key values (the validator enforces the enum):

| Value | Meaning |
|-------|---------|
| `high` | Key values cite a manufacturer datasheet, official drawing, or the design's official repo/docs; a source URL is required (`datasheet_url`, `sources`, or a link in `notes` — enforced) |
| `medium` | Trusted-retailer specs, or official sources with some key values estimated/uncited |
| `low` | Community spreadsheet, unverified, or estimated values — re-verify before trusting in CAD or config |

## Motor Current Convention

All current values are **RMS**, not peak. This matches Klipper's TMC `run_current` parameter.

- Peak = RMS x 1.414
- Safe starting `run_current`: 40-50% of rated RMS
- Upper safe limit: 70% of rated RMS
- TMC2209/2226 max: ~1.4A RMS
- TMC5160 max: ~3.0A RMS

## Usage

This repo is designed to be consumed as a git submodule or downloaded directly:

```bash
# As a submodule
git submodule add https://github.com/BakedBean3D/3d-printer-hardware-database.git hardware-db

# Direct clone
git clone https://github.com/BakedBean3D/3d-printer-hardware-database.git
```

Parse the YAML in any language. Files are split per manufacturer (e.g. `motors/ldo.yaml`, `motors/moons.yaml`), so load one file or glob the category directory:

```python
import glob
import yaml

motors = []
for path in glob.glob("motors/*.yaml"):
    with open(path) as f:
        motors.extend(yaml.safe_load(f))
```

```dart
import 'package:yaml/yaml.dart';
final motors = loadYaml(File('motors/ldo.yaml').readAsStringSync());
```

For `controller_boards/` and `psu/`, the generated `controller_boards.json` / `psu.json` aggregates are the easiest single-file entry points.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding or correcting hardware specs.

## License

This is an **open database**, dual-licensed so it can be used freely — including in
commercial and freemium tools — while staying open and attributed:

| What | License |
|---|---|
| **Database** (structure, selection, arrangement) | [**ODbL-1.0**](LICENSE) |
| **Contents** (the individual records / specs) | [**DbCL-1.0**](LICENSE-DbCL) |
| **Code** (`gen.py`, `scripts/`, and other tooling) | [**MIT**](LICENSE-CODE) |

You may build apps and generate parts (STL/STEP/3MF, layouts, BOMs) from this data,
commercially, without open-sourcing your app. In return you must **attribute** the
database and keep any **modified copy of the database itself** open under ODbL
(share-alike applies to the database, not to your app or generated parts).

See **[DATA_LICENSE.md](DATA_LICENSE.md)** for the full explanation, your exact
obligations, and the attribution string to copy. By contributing you agree to license
your contribution under these same terms.

> Attribution: *Contains data from the 3D Printer Hardware Database © BakedBean3D,
> licensed under ODbL-1.0 (database) and DbCL-1.0 (contents).*
