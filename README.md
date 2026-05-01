# 3D Printer Hardware Database

Community-maintained database of 3D printer hardware specifications for Klipper-based printers.

Covers stepper motors, hotends, extruders, toolheads, probes, and printer performance profiles — focused on the Voron, RatRig, Annex, and RepRap ecosystem.

## Data Format

All data lives in `data/` as YAML files:

| File | Description |
|------|-------------|
| `hotends.yaml` | Meltzone lengths, max volumetric flow, temperature ranges |
| `extruders.yaml` | Gear ratios, rotation distances, motor current, compatible motors |
| `toolheads.yaml` | Compatible extruders/hotends, fan configs, probe support |
| `motors.yaml` | Stepper specs: torque, current, inductance, resistance, step angle |
| `probes.yaml` | Accuracy, repeatability, probe speed, sample config |
| `performance_profiles.yaml` | Per-printer speed/accel/input shaper/belt tension configs |

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

MIT — see [LICENSE](LICENSE).
