# PSU Mounting Dimensions

**Generated** from the per-manufacturer `*.yaml` in this directory — do not hand-edit; run `python psu/gen.py`. The YAML files are the source of truth.

- **Total units:** 11
- **Confidence:** 11 high · 0 medium · 0 low
- **Aggregate for code:** `psu.json`
- **License:** data under ODbL-1.0 (database) + DbCL-1.0 (contents), © BakedBean3D. See [`DATA_LICENSE.md`](../DATA_LICENSE.md).

## Conventions

- `length_mm`/`width_mm`/`height_mm` follow the vendor's own L×W×H convention where stated; for DIN-rail units (vendor convention W×H×D) these are remapped length=D, width=W, height=H — read each record's `notes` for the exact mapping.
- Every enclosed/slim_enclosed unit carries TWO mount patterns: `bottom_mount_*` (vertical-entry hole pattern for flat/plate mounting — the one almost every printer mount design uses) and `side_mount_*` (the second documented pattern — true horizontal side-wall entry on the larger LRS-200/350/RSP-500 case family, or a second vertical top-flange pattern on the smaller LRS-50/100/150 case family). Read `notes` to know which physical face `side_mount` refers to for a given record — it is not always a horizontal entry.
- `din_rail_compatible` + `din_rail_type` describe spring-clip DIN-rail units (MDR/EDR series); these have no bolt-hole mount pattern (`bottom_mount_pattern`/`side_mount_pattern` = `none`).
- `mount_*_max_penetration_mm` is the maximum screw length Mean Well specifies before risking the internal PCB — respect it, this is a shock/short hazard, not just a mechanical fit issue.
- `mount_*_hole_dia_mm` is often inferred from the screw size (M3→3.5, M4→4.5 in this dataset) where the vendor drawing didn't explicitly dimension the bore — flagged per-record in `notes`.
- `null` = genuinely unknown; **never** assume 0.
- **Confidence:** `high` = dimensions extracted from the vendor's vector-text PDF and cross-validated (symmetric/arithmetic-checked); `medium` = case dimensions and screw/depth specs verified from the vendor mechanical drawing, but exact hole XY/pitch could not be fully resolved from the published PDF — extract from vendor 3D STEP/DXF before cutting; `low` = not authoritatively found — measure first.

## All units

| Unit | Mfr | Category | L×W×H (mm) | Weight | Watt | Voltages | Bottom mount | Side mount | Conf |
|---|---|---|---|---|---|---|---|---|---|
| LDO LCP300-24D5 | LDO Motors | enclosed | 120.0×95.0×35.0 | —g | 300W | 5/24 | 4×M3 (rectangular) | 4×M3 (rectangular) | high |
| Mean Well EDR-120 | Mean Well | din_rail | 113.5×40.0×125.2 | 600g | 120W | 12/24/48 | none | DIN TS35/7.5 or TS35/15 | high |
| Mean Well LRS-100 | Mean Well | enclosed | 129.0×97.0×30.0 | 330g | 100W | 3.3/5/12/15/24/36/48 | 2×M3 (2-hole) | 3×M3 (other) | high |
| Mean Well LRS-150 | Mean Well | enclosed | 159.0×97.0×30.0 | 420g | 150W | 12/15/24/36/48 | 2×M3 (2-hole) | 3×M3 (other) | high |
| Mean Well LRS-200 | Mean Well | enclosed | 215.0×115.0×30.0 | 660g | 200W | 3.3/4.2/5/12/15/24/36/48 | 4×M4 (rectangular) | 4×M4 (rectangular) | high |
| Mean Well LRS-350 | Mean Well | enclosed | 215.0×115.0×30.0 | 760g | 350W | 3.3/4.2/5/12/15/24/36/48 | 4×M4 (rectangular) | 4×M4 (rectangular) | high |
| Mean Well LRS-50 | Mean Well | enclosed | 99.0×82.0×30.0 | 210g | 50W | 3.3/5/12/15/24/36/48 | 2×M3 (2-hole) | 2×M3 (2-hole) | high |
| Mean Well LRS-75 | Mean Well | enclosed | 99.0×97.0×30.0 | —g | 75W | 5/12/15/24/36/48 | 2×M3 (2-hole) | 2×M3 (2-hole) | high |
| Mean Well MDR-60 | Mean Well | din_rail | 100.0×40.0×90.0 | 287g | 60W | 5/12/24/48 | none | DIN TS35/7.5 or TS35/15 | high |
| Mean Well RSP-500 | Mean Well | enclosed | 230.0×127.0×40.5 | 1300g | 500W | 3.3/4/5/12/15/24/27/48 | 5×M4 (other) | 4×M4 (rectangular) | high |
| Mean Well UHP-350 | Mean Well | slim_enclosed | 220.0×62.0×31.0 | 680g | 350W | 3.3/4.2/5/12/15/24/36/48/55 | 4×M3 (rectangular) | none | high |

## LDO Motors

### LDO LCP300-24D5  ·  `ldo_lcp300_24d5`

- **Category:** enclosed · **Confidence:** high · **Source file:** `ldo.yaml`
- **Case:** 120.0 × 95.0 × 35.0 mm, — g, 300W
- **Output voltages:** 5/24 V
- **Bottom mount:** 4× M3 (Ø3.5), rectangular, pitch 115.1×82.0 mm, max penetration — mm
  - holes (x,y mm): [[2.45, 6.5], [117.55, 6.5], [2.45, 88.5], [117.55, 88.5]]
  - open ear SLOT: the xy above is the slot's CLOSED (fully-enclosed) end; the screw centre may travel 2.45 mm outward from it toward the ear's open mouth
- **Side mount:** 4× M3 (Ø2.53), rectangular, pitch_x 100.0 mm, max penetration — mm
  - holes (x,y mm): [[10.0, 5.2], [110.0, 5.2], [10.0, 20.0], [110.0, 20.0]]
- **Terminal location:** screw terminal blocks on OPPOSITE 95x35 short ends -- AC input (6-position barrier, 7.7 mm pitch, dual AC input for parallel connection) on one end, DC output (8-position, 5.08 mm pitch) on the other. A bay layout must leave wire access at BOTH ends; this unit cannot be pushed against a wall the way a single-ended case can.
- **Connectors:** AC input uses M3 barrier terminals (LDO recommends SV2-3 or equivalent fork spade terminals). DC output uses standard 5.08 mm screw terminals (LDO recommends ferrules up to size VE1508). Output allocation is 24 V x3 pairs + 5 V x1 pair across the 8 positions. Fully enclosed, no user-serviceable vent face called out in the drawing.
- **Notes:** Confidence high -- measured 2026-09-08 from the VENDOR 3D STEP (LDOPowerSupply repo, LCP300-24D5/CAD) by OCCT cylindrical-face extraction, taking each cylinder's axis_of_rotation.position (a point ON the axis) and never its face centroid -- a half-cylinder face's centroid lies on the SURFACE, offset from the axis, which splits one round hole into two arcs and reads as a slot. Every mount number below is independently confirmed by the LCP300-24D5's OWN datasheet drawing (page 4, "Drawings and Dimensions"), so the record does not rest on the STEP alone. STEP orientation: X = 120 length, Y = 35 height, Z = 95 width; bbox measures exactly 120.000 x 35.000 x 95.000 with no connector overhang, so the case IS the bbox and the datum needed no reconstruction. Record origin: x=0 at the AC-INPUT end (located in the STEP by the 6-position 7.7 mm barrier terminals), y=0 at either long side -- both mount patterns are symmetric about the case centreline, so the y choice is free and is stated only to make the coordinates reproducible. Viewed onto the mounting face. BOTTOM (the plate-mount pattern, drawing's "115" x "82" view): four OPEN-MOUTHED SLOTS 3.5 mm wide in the 1.5 mm outer skin of one 120x95 face. The recorded xy is each slot's CLOSED round end (arc centres at STEP X=+-57.55, Z=+-41.0 -> 115.1 x 82.0 pitch; the drawing rounds 115.1 to 115). Each slot runs OUTWARD from there and breaks through the 120 mm end face -- the STEP end plane at X=+-60 is interrupted between Z=39.25 and Z=42.75, which is the mouth -- giving 2.45 mm of screw-centre travel. Interface is clearance_ears, NOT threaded: the user's screw passes through the case and must find its thread in the mount, so bottom_mount_max_penetration_mm is null by definition (nothing to thread into) rather than unknown. The opposite 120x95 face carries no mount feature at all -- checked, only a corner fillet. SIDE (drawing's "4x M3" / "4-M3" views): four TAPPED M3 in EACH long 120x35 side wall -- 8 on the unit, and side_mount_hole_count records the four on one wall, matching the drawing's own per-view callout. Pilots measure 2.529 mm (thread-forming M3). Positions x = 10.0 and 110.0 (100.0 mm pitch, the drawing's "100"); side_mount_holes_xy's second coordinate is HEIGHT above the large face that carries NO slots, 5.2 and 20.0 (the drawing's "5.2" and "20"). Measured from the slot face instead those heights are 29.8 and 15.0 -- state which face a mount is referencing before cutting. side_mount_max_penetration_mm is null and must stay null: LDO publishes no depth, and the STEP shows the thread passing through a bare 1.5 mm sheet with live case interior directly behind it, so there is no vendor-sanctioned safe screw length to record. Do not infer one. weight_g null -- absent from the datasheet and from every distributor page checked. din_rail_compatible false: the unit has no clip. LDO does publish a printable "Low Profile DIN Rail Mount" accessory in the same repo, which is an add-on part and not a property of the case. Provenance caveat, recorded rather than hidden: the LCP300-24D5 and LCP300-48 CAD files in that repo are BYTE-IDENTICAL (sha1 076c4543...), so the STEP is the shared LCP300 family case rather than a per-variant model. That does not weaken this record, because every dimension above is cross-checked against the 24D5's own datasheet drawing; it does mean the STEP alone cannot tell the two variants apart, and the terminal counts do not discriminate either (the -48 also uses 8 output positions). NOT YET PHYSICALLY VALIDATED -- no printed mount has been fitted to this unit.
- src: https://github.com/MotorDynamicsLab/LDOPowerSupply/blob/master/LCP300-24D5/CAD/LCP300-24D5%20CAD.step
- src: https://github.com/MotorDynamicsLab/LDOPowerSupply/blob/master/LCP300-24D5/Media/LCP300-24D5%20Datasheet.pdf
- src: https://docs.ldomotors.com/en/PSU/LCP300-24D5

## Mean Well

### Mean Well EDR-120  ·  `meanwell_edr_120`

- **Category:** din_rail · **Confidence:** high · **Source file:** `meanwell.yaml`
- **Case:** 113.5 × 40.0 × 125.2 mm, 600 g, 120W
- **Output voltages:** 12/24/48 V
- **DIN rail:** TS35/7.5 or TS35/15
- **Terminal location:** screw terminal blocks -- TB1 (3-pin AC/DC input) at the bottom of the front face, TB2 (4-pin DC output) at the top of the front face, both accessible with the unit clipped onto the DIN rail
- **Connectors:** TB1: 1 FG, 2 AC/N or DC-, 3 AC/L or DC+ (accepts DC input directly). TB2: pins 1-2 DC OUTPUT -V, pins 3-4 DC OUTPUT +V. No DC-OK signal on this economy line (unlike MDR-60).
- **Notes:** Confidence high -- Tier-1 source (Mean Well EDR-120-SPEC.PDF, Case No.992D, rev 2026-03-31, tolerance +-1mm), extracted with pdftotext against the clean text-layer PDF. Spring-clip DIN-rail unit (40mm body width, admissible rail TS35/7.5 or TS35/15) -- no bottom or side screw-hole pattern, same reasoning as MDR-60. The drawing's side views show two small circular marks on the case body that are the internal DIN-rail spring-clip mechanism, not user-facing mounting screws -- not modeled as a mount pattern. Vendor dimension convention is W*H*D (40*125.2*113.5mm), remapped here as length_mm=D(113.5), width_mm=W(40), height_mm=H(125.2), same convention as meanwell_mdr_60. Source: https://www.meanwell.com/Upload/PDF/EDR-120/EDR-120-SPEC.PDF
- src: https://www.meanwell.com/Upload/PDF/EDR-120/EDR-120-SPEC.PDF

### Mean Well LRS-100  ·  `meanwell_lrs_100`

- **Category:** enclosed · **Confidence:** high · **Source file:** `meanwell.yaml`
- **Case:** 129.0 × 97.0 × 30.0 mm, 330 g, 100W
- **Output voltages:** 3.3/5/12/15/24/36/48 V
- **Bottom mount:** 2× M3 (Ø2.6), 2-hole, pitch —×33.0 mm, max penetration 3.0 mm
  - holes (x,y mm): [[78.0, 34.0], [78.0, 67.0]]
- **Side mount:** 3× M3 (Ø2.6), other, pitch_x 77.0 mm, max penetration 5.0 mm
- **Terminal location:** 7-pin screw terminal block (AC/L, AC/N, FG, DC OUTPUT -V x2, DC OUTPUT +V x2), same face as the LED, SVR1 adjustment pot, and the side_mount holes
- **Connectors:** 7-position screw terminal. Pins 1-3 AC/L, AC/N, FG; pins 4-5 DC OUTPUT -V; pins 6-7 DC OUTPUT +V.
- **Notes:** Confidence high -- CORRECTED 2026-07-29 against the vendor 3D STEP (LRS-100(N2)-3D.stp); the previous record swapped the two hole groups between faces. Measured 2026-07-29 from the VENDOR 3D STEP (linked under the spec-PDF path, https://www.meanwell.com/Upload/PDF/<series>/<series>-3D.zip) via OCCT cylindrical-face extraction: every mount hole appears as an M-thread-forming punched pilot (dia 2.64mm for M3 family / 3.1mm for M4 family) with a 4.3mm extrusion collar, so positions are exact solid-model coordinates, not drawing estimates. Origin convention: x=0 at the terminal-block end, y=0 at the front (terminal-screw) long face, viewed from above -- verified against the STEP by locating the terminal features at the x-min end / y-min face. REAL bottom pattern: 2x M3 (callout "2-M3 L=3.0" in the top view, drawing dims 33/34) in a single column at (78.0, 34.0) and (78.0, 67.0) -- x=78 from the terminal end, 33mm apart across the width; max penetration 3.0mm, NOT the previously recorded 5mm (that depth belongs to the side wall -- safety-relevant swap). The "3-M3 L=5" callout the old record assigned to the bottom is the front SIDE-WALL trio: x=32 (mid-height ~15mm) and x=109 at two heights (~6mm and ~24mm) -- side_mount_pitch_x_mm 77 = the 32->109 span (drawing chain 32/77); heights informative only. Sources: LRS-100-SPEC.PDF + LRS-100-3D.zip.
- src: https://www.meanwell.com/Upload/PDF/LRS-100/LRS-100-SPEC.PDF

### Mean Well LRS-150  ·  `meanwell_lrs_150`

- **Category:** enclosed · **Confidence:** high · **Source file:** `meanwell.yaml`
- **Case:** 159.0 × 97.0 × 30.0 mm, 420 g, 150W
- **Output voltages:** 12/15/24/36/48 V
- **Bottom mount:** 2× M3 (Ø2.6), 2-hole, pitch 78.0×— mm, max penetration 3.0 mm
  - holes (x,y mm): [[24.0, 32.0], [102.0, 32.0]]
- **Side mount:** 3× M3 (Ø2.6), other, pitch_x 117.0 mm, max penetration 5.0 mm
- **Terminal location:** 7-pin screw terminal block (AC/L, AC/N, FG, DC OUTPUT -V x2, DC OUTPUT +V x2), same face as the LED, SVR1 adjustment pot, and the side_mount holes
- **Connectors:** 7-position screw terminal. Pins 1-3 AC/L, AC/N, FG; pins 4-5 DC OUTPUT -V; pins 6-7 DC OUTPUT +V.
- **Notes:** Confidence high -- CORRECTED 2026-07-29 against the vendor 3D STEP (LRS-150(230808).stp); same face-swap as LRS-100. Measured 2026-07-29 from the VENDOR 3D STEP (linked under the spec-PDF path, https://www.meanwell.com/Upload/PDF/<series>/<series>-3D.zip) via OCCT cylindrical-face extraction: every mount hole appears as an M-thread-forming punched pilot (dia 2.64mm for M3 family / 3.1mm for M4 family) with a 4.3mm extrusion collar, so positions are exact solid-model coordinates, not drawing estimates. Origin convention: x=0 at the terminal-block end, y=0 at the front (terminal-screw) long face, viewed from above -- verified against the STEP by locating the terminal features at the x-min end / y-min face. REAL bottom pattern: 2x M3 (callout "2-M3 L=3.0" in the top view) at (24.0, 32.0) and (102.0, 32.0) -- 78mm pitch on the y=32 line; max penetration 3.0mm, NOT the previously recorded 5mm (side-wall depth -- safety-relevant swap). "3-M3 L=5" is the front SIDE-WALL trio: x=22 (mid-height ~15mm) and x=139 at two heights (~6mm and ~24mm); side_mount_pitch_x_mm 117 = the 22->139 span; heights informative only. Sources: LRS-150-SPEC.PDF + LRS-150-3D.zip.
- src: https://www.meanwell.com/Upload/PDF/LRS-150/LRS-150-SPEC.PDF

### Mean Well LRS-200  ·  `meanwell_lrs_200`

- **Category:** enclosed · **Confidence:** high · **Source file:** `meanwell.yaml`
- **Case:** 215.0 × 115.0 × 30.0 mm, 660 g, 200W
- **Output voltages:** 3.3/4.2/5/12/15/24/36/48 V
- **Bottom mount:** 4× M4 (Ø4.5), rectangular, pitch 150.0×50.0 mm, max penetration 3.0 mm
  - holes (x,y mm): [[32.5, 32.5], [182.5, 32.5], [32.5, 82.5], [182.5, 82.5]]
- **Side mount:** 4× M4 (Ø4.5), rectangular, pitch_x 150.0 mm, max penetration 5.0 mm
- **Terminal location:** 9-pin screw terminal block (AC/L, AC/N, FG, DC OUTPUT -V x3, DC OUTPUT +V x3), same face as the LED, +V ADJ pot, and the bottom_mount holes
- **Connectors:** 9-position screw terminal. Pins 1-3 AC/L, AC/N, FG; pins 4-6 DC OUTPUT -V; pins 7-9 DC OUTPUT +V.
- **Notes:** Confidence high -- Tier-1 source (Mean Well LRS-200-SPEC.PDF, Case No.207, rev 2025-09-12, tolerance +-1mm); dimension chain visually verified against the rendered mechanical drawing (page 4) during review 2026-07-24. Case body 215x115x30mm and weight 660g cross-confirmed from both the spec table and the drawing. bottom_mount ("4-M4 L=3mm", vertical entry into the base): X pitch 150mm with 32.5mm inset each side (32.5 + 150 + 32.5 = 215, exact); Y pitch 50mm with 32.5mm inset each side (32.5 + 50 + 32.5 = 115, exact) -- the drawing's right-hand chain reads 115 overall / 50 between rows / 32.5 to the edge. This 150x50 grid also matches the community ground truth used by existing Voron PSU mounting plates. The drawing's 135mm figure is the overall top-view envelope including the terminal-block strip, NOT a mounting dimension -- do not derive hole positions from it. mount_holes_xy given from the case body's bottom-left corner. mount_hole_dia_mm (4.5mm) is INFERRED M4 clearance, not explicitly dimensioned on this drawing. side_mount is Mean Well's own "4-M4(Both Sides) L=5mm" label -- true horizontal entry through the two long side walls (NOT the top/bottom face), 2 holes per side, reusing the SAME 150mm X pitch as bottom_mount (confirmed: "32.5"/"150" reappear verbatim in the side-view dimension chain; the side view shows the hole row at 12.5mm above the case bottom, but that single Z figure was not cross-validated, so side holes_xy stays null). Source: https://www.meanwell.com/Upload/PDF/LRS-200/LRS-200-SPEC.PDF
- src: https://www.meanwell.com/Upload/PDF/LRS-200/LRS-200-SPEC.PDF

### Mean Well LRS-350  ·  `meanwell_lrs_350`

- **Category:** enclosed · **Confidence:** high · **Source file:** `meanwell.yaml`
- **Case:** 215.0 × 115.0 × 30.0 mm, 760 g, 350W
- **Output voltages:** 3.3/4.2/5/12/15/24/36/48 V
- **Bottom mount:** 4× M4 (Ø3.1), rectangular, pitch 150.0×50.0 mm, max penetration 3.0 mm
  - holes (x,y mm): [[32.5, 32.5], [182.5, 32.5], [32.5, 82.5], [182.5, 82.5]]
- **Side mount:** 4× M4 (Ø4.5), rectangular, pitch_x 150.0 mm, max penetration 5.0 mm
- **Terminal location:** 9-pin screw terminal block (AC/L, AC/N, FG, DC OUTPUT -V x3, DC OUTPUT +V x3), same face as the LED, +V ADJ pot, cooling fan, and the bottom_mount holes
- **Connectors:** 9-position screw terminal (same layout as LRS-200). Built-in DC fan with ON/OFF control on this face, blowing across the case (see "Air flow direction" on the drawing).
- **Notes:** Confidence high -- Tier-1 source (Mean Well LRS-350-SPEC.PDF, Case No.207A, rev 2025-09-12, tolerance +-1mm); dimension chain visually verified against the rendered mechanical drawing (page 4) during review 2026-07-24. IDENTICAL case footprint and hole pattern to LRS-200 (same Case-No. family, "A" suffix = fan-cooled variant) -- 215x115x30mm body, 150mm x 50mm bottom_mount grid ("4-M4 L=3mm") at 32.5mm insets on both axes (32.5 + 150 + 32.5 = 215 and 32.5 + 50 + 32.5 = 115, both exact), 150mm-pitch side_mount "4-M4(Both Sides) L=5mm". This 150x50 grid matches the community ground truth used by existing Voron PSU mounting plates. Only weight (760g vs 660g, extra mass of the fan) and wattage differ from LRS-200. Two additional drawing-only dimensions specific to this fan variant ("36.7" and "47.45") describe the fan cutout/position, not a mounting hole -- not modeled as mount fields. mount_hole_dia_mm (4.5mm) is INFERRED M4 clearance, not explicitly dimensioned. Source: https://www.meanwell.com/Upload/PDF/LRS-350/LRS-350-SPEC.PDF STEP-VERIFIED 2026-07-29 (LRS-350(N2).stp, OCCT face extraction): bottom grid measures exactly (32.5, 32.5)/(32.5, 82.5)/(182.5, 32.5)/(182.5, 82.5) and the side pitch 150 at ~13.4mm height -- record confirmed against the vendor solid. Mount pilots measure 3.1mm (thread-forming M4); hole_dia updated from the 4.5 inferred clearance to the measured case hole.
- src: https://www.meanwell.com/Upload/PDF/LRS-350/LRS-350-SPEC.PDF

### Mean Well LRS-50  ·  `meanwell_lrs_50`

- **Category:** enclosed · **Confidence:** high · **Source file:** `meanwell.yaml`
- **Case:** 99.0 × 82.0 × 30.0 mm, 210 g, 50W
- **Output voltages:** 3.3/5/12/15/24/36/48 V
- **Bottom mount:** 2× M3 (Ø2.6), 2-hole, pitch 55.0×— mm, max penetration 3.0 mm
  - holes (x,y mm): [[20.5, 40.5], [75.5, 40.5]]
- **Side mount:** 2× M3 (Ø2.6), 2-hole, pitch_x 74.0 mm, max penetration 5.0 mm
- **Terminal location:** 5-pin screw terminal block (AC/L, AC/N, FG, DC OUTPUT -V, DC OUTPUT +V), on the same face as the LED and the flange (side_mount) holes
- **Connectors:** 5-position screw terminal. Pin 1 AC/L, 2 AC/N, 3 FG, 4 DC OUTPUT -V, 5 DC OUTPUT +V.
- **Notes:** Confidence high -- CORRECTED 2026-07-29 against the vendor 3D STEP (LRS-50.stp); the previous record mis-assigned the drawing views AND swapped the L= depths. Measured 2026-07-29 from the VENDOR 3D STEP (linked under the spec-PDF path, https://www.meanwell.com/Upload/PDF/<series>/<series>-3D.zip) via OCCT cylindrical-face extraction: every mount hole appears as an M-thread-forming punched pilot (dia 2.64mm for M3 family / 3.1mm for M4 family) with a 4.3mm extrusion collar, so positions are exact solid-model coordinates, not drawing estimates. Origin convention: x=0 at the terminal-block end, y=0 at the front (terminal-screw) long face, viewed from above -- verified against the STEP by locating the terminal features at the x-min end / y-min face. REAL bottom pattern: 2x M3 at (20.5, 40.5) and (75.5, 40.5) -- 55mm pitch on the y=40.5 line (the top view's 20.5/55 chain + 40.5 dim, callout "2-M3 L=3.0") -- NOT the previously recorded 64mm from "10/74": those dims belong to the SIDE-WALL holes. bottom_mount_max_penetration_mm is 3.0 ("L=3.0"), not 5 -- the old record's 5mm was the side wall's depth: a screw sized to 5mm engagement into the bottom can reach 2mm past Mean Well's limit. side_mount = the front side-wall pair (callout "2-M3 L=5"): x = 10.0 and 84.0 (74mm pitch), ~15-16mm above the case bottom (height informative only, not a modeled field). The top-flange holes the old record called side_mount carry no vendor callout in the drawing and are excluded. psi3.5 labels in the drawing belong to other (cover/ground) holes, not the mount pattern -- mount pilots measure 2.64mm (thread-forming M3). Sources: LRS-50-SPEC.PDF + LRS-50-3D.zip.
- src: https://www.meanwell.com/Upload/PDF/LRS-50/LRS-50-SPEC.PDF

### Mean Well LRS-75  ·  `meanwell_lrs_75`

- **Category:** enclosed · **Confidence:** high · **Source file:** `meanwell.yaml`
- **Case:** 99.0 × 97.0 × 30.0 mm, — g, 75W
- **Output voltages:** 5/12/15/24/36/48 V
- **Bottom mount:** 2× M3 (Ø2.65), 2-hole, pitch 55.0×— mm, max penetration 3.0 mm
  - holes (x,y mm): [[20.62, 45.5], [75.64, 45.5]]
- **Side mount:** 2× M3 (Ø2.65), 2-hole, pitch_x 74.0 mm, max penetration 5.0 mm
- **Terminal location:** 5-pin screw terminal block (AC/L, AC/N, FG, DC OUTPUT -V, DC OUTPUT +V), on the same face as the LED and the flange (side_mount) holes
- **Connectors:** 5-position screw terminal. Pin 1 AC/L, 2 AC/N, 3 FG, 4 DC OUTPUT -V, 5 DC OUTPUT +V.
- **Notes:** Confidence high -- NEW RECORD 2026-09-08, measured from the VENDOR 3D STEP (LRS-75-3D.stp, from LRS-75-3D.zip beside the spec PDF) via OCCT cylindrical-face extraction, with every value cross-checked against the printed dimension text in LRS-75-SPEC.PDF (Case No.240A, tolerance +/-1). Case measures 99.00 x 97.00 x 30.00 at the STEP bounding box, matching the drawing 99/97/30 exactly. Origin convention: x=0 at the terminal-block end, y=0 at the front (terminal-screw) long face, viewed from above -- verified against the STEP, not assumed: the five 6mm terminal pins sit at x=3.6 and x=9.6 on 9.5mm centres (drawing "9.5") at the x-min end, and the two side-wall pilots lie on the y-min face. Hole axes were taken from each cylindrical face's AXIS, never its centroid: a half-cylinder face centroid lies on the surface, which reads one round hole as two offset arcs and would have recorded these holes as 8.5mm slots. Both mount holes are round M3 thread-forming pilots (measured dia 2.65) with a concentric 4.27 collar. BOTTOM: 2x M3 at (20.62, 45.50) and (75.64, 45.50) -- 55.02 measured pitch on the y=45.50 line; the drawing chain 20.5 + 55 = 75.5 and the printed 45.5 agree to within 0.15mm (the STEP value is recorded, per the measured-artifact hierarchy). SIDE: 2x M3 on the y=0 long face at x=10.00 and x=84.00 (74.00 pitch, drawing "10"/"74"), 15.00 above the case bottom (drawing "15"; height is informative, not a modelled field). L= depths were assigned by LOCATING THE CALLOUTS IN THE DRAWING, not transferred from a sibling record: "2-M3 L=3.0" sits in the view that also carries 99/97/20.5/55/45.5 (the bottom view) and "2-M3 L=5" sits in the view carrying 30/15/10/74 (the side view), so bottom max penetration is 3.0 and side is 5.0. Swapping those two is a safety error -- it has happened in this file before (LRS-50, LRS-100). Cross-check: LRS-75 shares the LRS-50 case length and hole X positions (20.5/75.5 bottom, 10/84 side) and differs only in width (97 vs 82), which moves the bottom hole line from y=40.5 to y=45.5 -- consistent with one case family in two widths. weight_g is null (unknown): the spec PDF stores its packing table as positioned text that does not extract in reading order, and null means unknown here, never zero. output_voltages_v from the model-variant list on spec page 2 -- LRS-75 has NO 3.3V variant (LRS-75-5/12/15/24/36/48 only), unlike LRS-50 and LRS-100. NOT YET PHYSICALLY VALIDATED: no print has threaded onto a real LRS-75.
- src: https://www.meanwell.com/Upload/PDF/LRS-75/LRS-75-SPEC.PDF
- src: https://www.meanwell.com/Upload/PDF/LRS-75/LRS-75-3D.zip

### Mean Well MDR-60  ·  `meanwell_mdr_60`

- **Category:** din_rail · **Confidence:** high · **Source file:** `meanwell.yaml`
- **Case:** 100.0 × 40.0 × 90.0 mm, 287 g, 60W
- **Output voltages:** 5/12/24/48 V
- **DIN rail:** TS35/7.5 or TS35/15
- **Terminal location:** screw terminal strip (+V, +V, -V, -V, DC OK) on the top face, AC input (N, L) on the bottom face, both accessible with the unit clipped onto the DIN rail
- **Connectors:** DC OK is a dry relay contact (30V/1A resistive max), not a signal level -- contact closed = PSU on/DC OK, open = PSU off/DC fail.
- **Notes:** Confidence high -- Tier-1 source (Mean Well MDR-60-SPEC.PDF, Case No.962A, rev 2025-07-25, tolerance +-1mm), extracted with pdftotext against the clean text-layer PDF (no raster estimation needed). This is a spring-clip DIN-rail unit, not a screw-mounted one -- there is no bottom or side screw-hole pattern to record (both left null/none rather than guessed); the mount interface for a parametric generator is the DIN-rail clip geometry itself (rail width 35mm, admissible rail profile TS35/7.5 or TS35/15 per the drawing's "Install DIN rail TS35/7.5 or TS35/15" callout), not a bolt pattern. Vendor dimension convention on this drawing is W*H*D (40*90*100mm) rather than L*W*H -- remapped here to this schema's length/width/height as length_mm=D(100, how far the unit projects off the rail), width_mm=W(40, body width along the rail), height_mm=H(90, vertical extent when rail-mounted). Source: https://www.meanwell.com/upload/pdf/MDR-60/MDR-60-SPEC.PDF
- src: https://www.meanwell.com/upload/pdf/MDR-60/MDR-60-SPEC.PDF

### Mean Well RSP-500  ·  `meanwell_rsp_500`

- **Category:** enclosed · **Confidence:** high · **Source file:** `meanwell.yaml`
- **Case:** 230.0 × 127.0 × 40.5 mm, 1300 g, 500W
- **Output voltages:** 3.3/4/5/12/15/24/27/48 V
- **Bottom mount:** 5× M4 (Ø3.1), other, pitch —×— mm, max penetration 4.0 mm
  - holes (x,y mm): [[39.4, 19.0], [39.4, 108.0], [88.1, 69.0], [198.9, 19.0], [198.9, 108.0]]
- **Side mount:** 4× M4 (Ø3.1), rectangular, pitch_x 170.0 mm, max penetration 5.0 mm
- **Terminal location:** screw terminal blocks (TB1 3-pin AC input, TB2 6-pin DC output) plus a 4-pin CN100 connector (remote ON/OFF + remote sense), on the face opposite the built-in cooling fan
- **Connectors:** TB1 (AC input): 1 AC/L, 2 AC/N, 3 FG. TB2 (DC output): pins 1-3 DC OUTPUT -V, pins 4-6 DC OUTPUT +V. CN100 (HRS DF11-04DP-2DS or equivalent): 1 -S, 2 +S, 3 RC-, 4 RC+ (remote sense / remote on-off). Built-in DC fan for forced-air cooling.
- **Notes:** Confidence high -- COMPLETED 2026-07-29 against the vendor 3D STEP (rsp-500.stp). Measured 2026-07-29 from the VENDOR 3D STEP (linked under the spec-PDF path, https://www.meanwell.com/Upload/PDF/<series>/<series>-3D.zip) via OCCT cylindrical-face extraction: every mount hole appears as an M-thread-forming punched pilot (dia 2.64mm for M3 family / 3.1mm for M4 family) with a 4.3mm extrusion collar, so positions are exact solid-model coordinates, not drawing estimates. Origin convention: x=0 at the terminal-block end, y=0 at the front (terminal-screw) long face, viewed from above -- verified against the STEP by locating the terminal features at the x-min end / y-min face. Bottom pattern "5-M4 L=4mm": all five holes resolved -- (39.4, 19.0), (39.4, 108.0), (88.1, 69.0), (198.9, 19.0), (198.9, 108.0); the old record's unassigned raw dims 39.3/159.7/88 all land (39.4, 39.4+159.5=198.9, 88.1). The 5th hole is a genuine mid-case structural point at (88.1, 69.0), not a chassis-ground as previously hypothesised. side_mount "4-M4(Both Sides) L=5mm": x = 40.1 and 210.1 (170mm pitch, the drawing's raw 40/170), at two heights per position (~12.5mm and ~30.5mm from the case bottom; heights informative only). Mount pilots measure 3.1mm (thread-forming M4); the previous 4.5mm was an inferred clearance, not the case hole. Sources: RSP-500-SPEC.PDF + RSP-500-3D.zip.
- src: https://www.meanwell.com/Upload/PDF/RSP-500/RSP-500-SPEC.PDF

### Mean Well UHP-350  ·  `meanwell_uhp_350`

- **Category:** slim_enclosed · **Confidence:** high · **Source file:** `meanwell.yaml`
- **Case:** 220.0 × 62.0 × 31.0 mm, 680 g, 350W
- **Output voltages:** 3.3/4.2/5/12/15/24/36/48/55 V
- **Bottom mount:** 4× M3 (Ø3.3), rectangular, pitch 218.2×46.4 mm, max penetration — mm
  - holes (x,y mm): [[0.9, 7.8], [219.1, 7.8], [0.9, 54.2], [219.1, 54.2]]
  - open ear SLOT: the xy above is the slot's CLOSED (fully-enclosed) end; the screw centre may travel 2.0 mm outward from it toward the ear's open mouth
- **Terminal location:** screw terminal blocks -- TB1 (2-pin AC input) on one short end, TB2/TB3 (4-pin DC output, high-current) plus CN10 (2-pin DC-OK signal) on the opposite short end
- **Connectors:** TB1 (DEGSON DG28C-B-03P or equiv.): 1 AC/L, 2 AC/N, 3 FG; max mounting torque 5Kgf-cm. TB2/TB3 (Mean Well TB-HTP-200-40A or equiv.): pins 1-2 -V, pins 3-4 +V; max mounting torque 8Kgf-cm. CN10 (JST B2B-PH-K-S or equiv.): 1 DC COM, 2 DC OK +V. Fanless -- MUST be mounted to a thermally-conductive aluminum plate (or equivalent chassis) at least 450x450x3mm per Mean Well's installation guidance for the unit to meet its rated derating curve; this is a thermal requirement, not just a mechanical one.
- **Notes:** Confidence high -- Tier-1 source (Mean Well UHP-350-SPEC.PDF, Case No.232C, rev 2024-11-23, tolerance +-1mm; "R" suffix variant adds a DC-OK signal + redundant-operation function, same mechanicals). Case 220x62x31mm and weight 680g cross-confirmed from both the spec table and the drawing. VECTOR-PDF EXTRACTION 2026-07-28 (least-squares circle fits on the drawing's own bezier geometry; supersedes the earlier raster reading): the "4-ψ3.3" callout's leader line terminates at an END-PLATE EAR -- the mounting interface is 4 outward-opening 3.3mm slots on the corner ears of the two 3mm end plates, at the case bottom plane. The 4 small circles ON the case face at ~10.1mm end insets are case-assembly screws, NOT mounting holes -- do not mount to them. ACROSS WIDTH (Y): the drawing's own chain closes exactly (7.8 + 46.4 + 7.8 = 62) and the fitted ear centres measure 7.79/46.39/7.82 against it -- pitch_y 46.4 with 7.8 insets. ALONG LENGTH (X): slot centres vector-measure 0.9mm inside each end face (pitch_x 218.2, closing the 220 envelope exactly); this value is measured from the drawing geometry, not carried by a printed dimension -- and because the slots open OUTWARD through the end faces, any screw spacing from ~218.2 up to the 220 envelope engages the ears. FAMILY CROSS-CHECK: UHP-200 (Case 249B, 55mm-wide case) shows the identical construct, 6.5 + 42 + 6.5 = 55. SLOT GEOMETRY 2026-09-02 (same vector method, re-run on UHP-350-SPEC.PDF page 5 after a field report that a printed plate left part of each ear feature unengaged): the ear feature is a SLOT, not a round hole, and the record's xy is its CLOSED end. Bottom-view frame is anisotropically scaled -- calibrate per axis: 358.13 pt / 220 mm = 1.6279 pt/mm in X, 109.58 pt / 62 mm = 1.7674 pt/mm in Y (the Y scale closes the printed chain 7.8 + 46.4 + 7.8 = 62 exactly and independently reproduces the 3.3 mm slot WIDTH from its two parallel edges, 5.83 pt apart -- two confirmations, so the anisotropy is real and not a fitting artifact). Per corner the path is: two straight edges 3.3 mm apart, a semicircular closed end whose least-squares centre is 0.995 mm INBOARD of the case end face, and an open mouth through the ear edge, which itself stands 1.0 mm OUTBOARD of that face -- so the screw centre can travel 2.0 mm outward from the recorded position, and c-c spacing ranges 218.2 (closed end) to 222.0 (mouth). The recorded 218.2 is therefore the MINIMUM and the fully-enclosed position, which is the one to build: moving outward trades captured material for nothing, and a bare M3 head already overhangs the ear edge by ~0.85 mm on diameter at the closed end (use a washer). CORRECTION of the previous record: pitch_x 110 was a misread -- the drawing's "110"/"15.5" dimension the tc (max case temperature) measurement point on the finned side elevation, not any mounting feature. bottom_mount_interface clearance_ears: no thread in the case; the screw clamps the ear and threads into the mounting plate below (Mean Well install guidance: "M3*4" into a thermally-conductive aluminum plate >= 450x450x3mm for the full derating curve -- a THERMAL requirement, not just mechanical), and the screw path lies outside the case wall, so bottom_mount_max_penetration_mm is null (not applicable) rather than a safety depth. Source: https://www.meanwell.com/Upload/PDF/UHP-350(R)/UHP-350-SPEC.PDF (mechanical dims on page 5; installation/aluminum-plate requirement on page 6).
- src: https://www.meanwell.com/Upload/PDF/UHP-350(R)/UHP-350-SPEC.PDF
