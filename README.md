# 3D Printer Hardware Database

Community-maintained database of 3D printer hardware specifications for Klipper-based printers.

Covers stepper motors, hotends, extruders, toolheads, probes, and controller-board mounting dimensions — focused on the Voron, RatRig, Annex, and RepRap ecosystem.

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
| `mount_pattern` | string | rectangular, L-shaped, linear, 2-hole, 3-hole, none, other |
| `mount_pitch_x_mm` / `mount_pitch_y_mm` | float | Center-to-center hole spacing |
| `mount_hole_count` | int | Number of mounting holes |
| `mount_holes_xy` | list | Optional `[[x,y], ...]` from PCB bottom-left corner (read `notes`) |
| `standoff_height_mm` | float | Recommended clearance under the board |
| `component_height_top_mm` | float | Tallest component / module body height above board |
| `connector_notes` | string | Which edge carries power / steppers / USB / etc. |
| `sources` | list | Datasheet / GitHub hardware repo / KiCad URLs |
| `confidence` | string | high (vendor/community CAD), medium (outline firm, pitch inferred), low (measure first) |
| `notes` | string | Source citation + anything to double-check |

## Schema

Each hardware category has a defined set of fields. See `schema/` for JSON Schema definitions that can be used for validation.

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
| `weight` | int | Weight in grams |
| `tooth_count` | int | Integrated pinion teeth (0 = none) |
| `datasheet_url` | string | Link to manufacturer datasheet |
| `notes` | string | Verification source and usage context |

## Safety Notice

This data is used to configure expensive 3D printers. Incorrect motor currents can damage drivers or motors. Incorrect flow rates can cause jams or failed prints.

**Every spec must cite its source** in the `notes` field. Acceptable citations:
- Manufacturer datasheet (Tier 1)
- Trusted retailer tested (Tier 2)
- Community tested / estimated (Tier 3)

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

Parse the YAML in any language:

```python
import yaml
with open("data/motors.yaml") as f:
    motors = yaml.safe_load(f)
```

```dart
import 'package:yaml/yaml.dart';
final motors = loadYaml(File('data/motors.yaml').readAsStringSync());
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding or correcting hardware specs.

## License

This is an **open database**, dual-licensed so it can be used freely — including in
commercial and freemium tools — while staying open and attributed:

| What | License |
|---|---|
| **Database** (structure, selection, arrangement) | [**ODbL-1.0**](LICENSE) |
| **Contents** (the individual records / specs) | [**DbCL-1.0**](LICENSE-DbCL) |
| **Code** (`gen.py`, `convert_data.py`, scripts) | [**MIT**](LICENSE-CODE) |

You may build apps and generate parts (STL/STEP/3MF, layouts, BOMs) from this data,
commercially, without open-sourcing your app. In return you must **attribute** the
database and keep any **modified copy of the database itself** open under ODbL
(share-alike applies to the database, not to your app or generated parts).

See **[DATA_LICENSE.md](DATA_LICENSE.md)** for the full explanation, your exact
obligations, and the attribution string to copy. By contributing you agree to license
your contribution under these same terms.

> Attribution: *Contains data from the 3D Printer Hardware Database © BakedBean3D,
> licensed under ODbL-1.0 (database) and DbCL-1.0 (contents).*
