# CLAUDE.md

Community YAML database of 3D printer hardware specs (motors, hotends, extruders,
probes, toolheads, controller-board and PSU mounting geometry) for Klipper-based
printers. Downstream consumers use this data to configure real machines and to
generate parametric CAD mounts — **a wrong number here damages hardware or
produces an unprintable/unfastenable part**. Data quality outranks everything else.

## The one command that matters

```bash
python3 scripts/validate.py   # must print PASSED before any commit
```

## Source of truth and generated files

Per-manufacturer `*.yaml` files are the only source of truth. These files are
**generated — never hand-edit them**:

- `controller_boards/controller_boards.json`, `controller_boards/CONTROLLER_BOARDS.md`
  → regenerate with `python3 controller_boards/gen.py`
- `psu/psu.json`, `psu/PSU.md`
  → regenerate with `python3 psu/gen.py`

After editing any YAML in those two directories, rerun the matching `gen.py` and
commit the regenerated outputs together with the YAML change.

## Hard data rules (never break these)

1. **`null` means unknown; `0` means measured-as-zero.** Never substitute `0`,
   `0.0`, or a guess for a value you could not verify. A zero flows into CAD as
   a real dimension.
2. **Never invent a spec.** Every value must trace to a source cited in the
   entry's `notes` (and `sources` URLs where the schema has them). Tiers:
   manufacturer datasheet (1) > trusted retailer (2) > community tested (3).
   If you cannot find a source, use `null` and flag it in `notes`
   (`"unverified - needs research"`).
3. **Motor currents are RMS**, matching Klipper's TMC `run_current`
   (peak = RMS × 1.414). `recommended_run_current` is 40–70% of rated RMS.
4. **Units live in the field name** (`_mm`, `_g`, `_ncm`, `_mh`, `_w`, `_v`).
   Convert before entering; never store a value in the wrong unit because the
   datasheet used it.
5. **IDs**: lowercase, underscores, unique within the category (validator
   enforces this across files), e.g. `ldo_42sth48_2004mah`.
6. **Every required field present** on every entry — the per-category required
   lists are at the top of `scripts/validate.py`. New fields are a schema
   change: add them to every existing entry (as `null` where unknown), to
   `validate.py`, and to the README field table in the same commit.
7. **PSU/board geometry has physics checks** (pitch vs. face size, holes on the
   part, `bottom_mount_interface` rules). If the validator flags your entry,
   the drawing was misread — recheck the datasheet; do not weaken the check.

## Adding or correcting an entry — workflow

1. Find the vendor datasheet / mechanical drawing (or the community CAD for
   open-source designs). Read the actual numbers; don't trust retailer blurbs
   for dimensions.
2. Pick the file: brand-owned hardware goes in the manufacturer's file
   (`motors/ldo.yaml`, `hotends/phaetus.yaml`, ...); community designs go in
   the category's single file (`extruders/extruders.yaml`,
   `toolheads/toolheads.yaml`, `controller_boards/community.yaml`).
3. Copy an adjacent entry as a template so field order and style match.
4. Fill every field; cite the source (with revision/date if available) in
   `notes`; set `confidence` honestly where the schema has it.
5. `python3 scripts/validate.py` → PASSED.
6. If you touched `controller_boards/` or `psu/`, rerun that directory's
   `gen.py`.

When correcting existing data, state the old value, new value, and source in
the commit message (see `git log` for the house style: `fix(psu): ...`,
`feat(boards): ...`).

## Judgment calls

- If a datasheet and this database disagree, the datasheet wins — but check
  whether the datasheet revision changed before assuming the entry was wrong.
- If two sources disagree, record the tier-1 value and note the conflict in
  `notes` rather than averaging.
- Plausibility-check numbers against the part class before committing
  (NEMA17 body ≈ 42.3 mm square; hotend max temps ~240–500 °C; PSU wattage ≈
  max voltage × current). An implausible value is usually a unit or
  transcription error — verify, don't "fix" it silently.
- Don't add speculative fields, performance opinions, or non-hardware data;
  this repo is measured specs only.

## Licensing

Database structure: ODbL-1.0. Record contents: DbCL-1.0. Code: MIT.
Contributions inherit these terms — only add specs that are freely citable
(datasheet numbers are facts; don't paste proprietary drawings or text).
