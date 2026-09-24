# Repository instructions

Community YAML specs for Klipper printers and parametric CAD mounts. Wrong
numbers can damage hardware or produce unusable parts; data quality comes first.
This is the canonical repository policy; CLAUDE.md imports it.

## Scope and routes

Finish the requested outcome and verify it. Read only references relevant to the
task, expanding when dependencies require it. Historical notes and handoffs are
context, not assignments or proof that work shipped. Preserve unrelated changes.

| Task | Read next |
| --- | --- |
| Add or correct hardware | [CONTRIBUTING.md](CONTRIBUTING.md), an adjacent YAML entry, the actual vendor drawing/datasheet (official CAD for community designs) |
| Field or schema change | Required lists, types and enums in [scripts/validate.py](scripts/validate.py), the category's [README field table](README.md), [scripts/gen_schema.py](scripts/gen_schema.py) |
| Re-verify low-confidence entries | [.claude/commands/reverify.md](.claude/commands/reverify.md); execute its publication steps only for that requested workflow |
| Code, docs, or release checks | Relevant implementation and [.github/workflows/validate.yml](.github/workflows/validate.yml); do not claim unchecked gates passed |

## Data safeguards

1. **Unknown is `null`; zero is measured zero.** Never fill an unknown with a
   guess or `0`/`0.0`; flag it in notes as "unverified - needs research".
2. Cite every value in `notes` and `sources` URLs where supported, including
   revision/date when available. Rank manufacturer datasheet > trusted retailer >
   community tested. Read actual drawing dimensions, not retailer blurbs.
   Check revisions when sources disagree; use the tier-1 value and note the
   conflict, never average. Set required `confidence` honestly per CONTRIBUTING.
   A validator pass checks structure/plausibility, not source accuracy, URL
   reachability, or physical fit; verify those claims with their own evidence.
   **Never write "no 3D model / no solid published" from a single 404.** Vendors
   spell archive URLs inconsistently (Mean Well hides suffixed series under a
   parenthesised folder AND repeats the suffix in the filename, while the spec
   PDF beside it stays unsuffixed). Run `python3 scripts/check_vendor_solids.py
   [<id>...]` first; if it finds a solid, measure from that, because the
   artifact hierarchy is vendor 3D solid > printed dimension text > drawing-view
   geometry. One unprobed spelling is how `meanwell_uhp_350` carried a
   `bottom_mount_pitch_x_mm` wrong by 4.2 mm into shipped parts (218.2 vs a true
   214.0, corrected 2026-09-24).
3. Motor current is **RMS** (peak = RMS × 1.414); recommended run current is
   40–70% of rated RMS. Convert units to those required by the field/schema
   (`_mm`, `_g`, `_ncm`, `_mh`, `_w`, `_v`); do not rename legacy fields casually.
4. IDs are lowercase with underscores, unique within a category. Include every
   required field. New fields require updating all entries in that category
   (`null` where unknown and schema permits), validate.py, and the README field
   table together; regenerate JSON Schemas as below.
5. Recheck drawings when geometry/physics checks fail (pitch, face size, hole
   bounds, `bottom_mount_interface`). Never weaken a check to fit an entry;
   escalate a source-backed contradiction for human review. Plausibility-check
   against the part class (NEMA17 ≈ 42.3 mm square; hotends ~240–500 °C;
   PSU watts ≈ volts × amps); verify odd values rather than silently fixing them.
6. Add measured hardware specs, not speculative fields or performance opinions.
   Existing source-attributed estimates remain explicitly qualified by confidence;
   they do not authorize inventing new values.
7. Structure: ODbL-1.0; records: DbCL-1.0; code: MIT. Contributions inherit these
   terms. Use freely citable specs; never copy proprietary drawings or prose.

## Sources, generated files, and completion

Category YAML files are the data authority, including manufacturer files and
community/single files. Copy an adjacent entry's field order and style. Generated
outputs must never be hand-edited; commit them with their source changes:

| Source change | Regenerate | Outputs |
| --- | --- | --- |
| `controller_boards/*.yaml` | `python3 controller_boards/gen.py` | `controller_boards/controller_boards.json`, `controller_boards/CONTROLLER_BOARDS.md` |
| `psu/*.yaml` | `python3 psu/gen.py` | `psu/psu.json`, `psu/PSU.md` |
| Schema definitions in `scripts/validate.py` | `python3 scripts/gen_schema.py` | `schema/*.schema.json` |

Regenerate affected outputs first. **Before every commit**, run
`python3 scripts/validate.py` and require **PASSED**. For data/schema work also run
`python3 scripts/check_docs.py` and `python3 scripts/gen_schema.py --validate`;
run relevant code checks for implementation changes. Inspect the final diff for
unrelated edits and generated drift. Report evidence and remaining unknowns;
a plan alone is not completion. Data-correction commit messages must state old
value → new value → source; use existing `fix(psu):` / `feat(boards):` style.
Data changes need human review; do not push them directly to main.
