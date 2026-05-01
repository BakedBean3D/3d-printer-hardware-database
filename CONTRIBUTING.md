# Contributing

Thanks for helping build the community hardware database! Here's how to contribute.

## Adding New Hardware

1. Fork this repo
2. Add your entry to the appropriate YAML file in `data/`
3. Include a source citation in the `notes` field
4. Open a PR with the entry and your source

### ID Convention

IDs must be lowercase with underscores, max 80 characters:
- `ldo_42sth48_2004mah`
- `dragon_hf`
- `omc_17hs19_2004s1`

### Required Fields

Every entry needs ALL fields defined in the schema. If a value is unknown, use:
- `0` or `0.0` for numeric fields you can't find
- `"unverified - needs research"` in `notes` to flag it

### Source Requirements

The `notes` field must include a verification source. Tier hierarchy:

| Tier | Source | Example |
|------|--------|---------|
| 1 | Manufacturer datasheet | "From LDO datasheet Rev A" |
| 2 | Trusted retailer (West3D, KB-3D, Fabreeko) | "From West3D product page" |
| 3 | Community tested / estimated | "Community tested at ~45 N·cm" |

Unverified entries are accepted but must be clearly marked.

### Motor-Specific Guidelines

- **Current is always RMS**, not peak (Peak = RMS x 1.414)
- `recommended_run_current` should be a safe starting value (40-70% of rated)
- `holding_torque_ncm` is in Newton-centimeters
- `step_angle` is 1.8 (200 steps/rev) or 0.9 (400 steps/rev)
- `tooth_count` is 0 if no integrated pinion gear
- Include `datasheet_url` when available

### Hotend-Specific Guidelines

- `max_volumetric_flow` should be the 0.4mm nozzle PLA baseline unless noted
- Cite the flow test conditions (material, temp) in notes
- `meltzone_length` is measured from the start of the melt zone to the nozzle tip

## Correcting Data

If you find an error:

1. Open an issue with the correct value and your source
2. Or submit a PR with the fix and source citation in `notes`

## Validation

Run the schema validator before submitting:

```bash
python scripts/validate.py
```

## Code of Conduct

Be respectful. We're all here to help each other build better printers.
