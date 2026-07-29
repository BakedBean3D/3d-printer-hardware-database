# PSU Mounting Dimensions

**Generated** from the per-manufacturer `*.yaml` in this directory — do not hand-edit; run `python psu/gen.py`. The YAML files are the source of truth.

- **Total units:** 9
- **Confidence:** 5 high · 4 medium · 0 low
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
| Mean Well EDR-120 | Mean Well | din_rail | 113.5×40.0×125.2 | 600g | 120W | 12/24/48 | none | DIN TS35/7.5 or TS35/15 | high |
| Mean Well LRS-100 | Mean Well | enclosed | 129.0×97.0×30.0 | 330g | 100W | 3.3/5/12/15/24/36/48 | 3×M3 (3-hole) | 2×M3 (2-hole) | medium |
| Mean Well LRS-150 | Mean Well | enclosed | 159.0×97.0×30.0 | 420g | 150W | 12/15/24/36/48 | 3×M3 (3-hole) | 2×M3 (2-hole) | medium |
| Mean Well LRS-200 | Mean Well | enclosed | 215.0×115.0×30.0 | 660g | 200W | 3.3/4.2/5/12/15/24/36/48 | 4×M4 (rectangular) | 4×M4 (rectangular) | high |
| Mean Well LRS-350 | Mean Well | enclosed | 215.0×115.0×30.0 | 760g | 350W | 3.3/4.2/5/12/15/24/36/48 | 4×M4 (rectangular) | 4×M4 (rectangular) | high |
| Mean Well LRS-50 | Mean Well | enclosed | 99.0×82.0×30.0 | 210g | 50W | 3.3/5/12/15/24/36/48 | 2×M3 (2-hole) | 2×M3 (2-hole) | medium |
| Mean Well MDR-60 | Mean Well | din_rail | 100.0×40.0×90.0 | 287g | 60W | 5/12/24/48 | none | DIN TS35/7.5 or TS35/15 | high |
| Mean Well RSP-500 | Mean Well | enclosed | 230.0×127.0×40.5 | 1300g | 500W | 3.3/4/5/12/15/24/27/48 | 5×M4 (other) | 4×M4 (rectangular) | medium |
| Mean Well UHP-350 | Mean Well | slim_enclosed | 220.0×62.0×31.0 | 680g | 350W | 3.3/4.2/5/12/15/24/36/48/55 | 4×M3 (rectangular) | none | high |

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

- **Category:** enclosed · **Confidence:** medium · **Source file:** `meanwell.yaml`
- **Case:** 129.0 × 97.0 × 30.0 mm, 330 g, 100W
- **Output voltages:** 3.3/5/12/15/24/36/48 V
- **Bottom mount:** 3× M3 (Ø3.5), 3-hole, pitch —×— mm, max penetration 5.0 mm
- **Side mount:** 2× M3 (Ø3.5), 2-hole, pitch_x — mm, max penetration 3.0 mm
- **Terminal location:** 7-pin screw terminal block (AC/L, AC/N, FG, DC OUTPUT -V x2, DC OUTPUT +V x2), same face as the LED, SVR1 adjustment pot, and the side_mount holes
- **Connectors:** 7-position screw terminal. Pins 1-3 AC/L, AC/N, FG; pins 4-5 DC OUTPUT -V; pins 6-7 DC OUTPUT +V.
- **Notes:** Confidence medium -- Tier-1 source (Mean Well LRS-100-SPEC.PDF, Case No.238A, rev 2025-04-07, tolerance +-1mm), exact hole XY unresolved. Case 129x97x30mm and weight 330g cross-confirmed from both the spec table and the mechanical drawing. bottom_mount = base/underside view: 3x M3 (NOT 2 -- this is one more hole than LRS-50, confirmed by the explicit "3-M3 L=5" callout), dia 3.5mm labelled, 5mm max penetration. 3-hole pattern geometry (not a simple 2-point pitch) means bottom_mount_pitch_x/y_mm do not apply cleanly and are left null; raw legible offsets in the drawing include 32mm and 77mm along one axis but could not be confidently assigned to specific hole positions from the rendered PDF -- extract from vendor CAD before cutting. side_mount = top/flange view (terminal/LED/SVR1 side): 2x M3, dia 3.5mm labelled, "2-M3 L=3.0", 3mm max penetration. Source: https://www.meanwell.com/Upload/PDF/LRS-100/LRS-100-SPEC.PDF
- src: https://www.meanwell.com/Upload/PDF/LRS-100/LRS-100-SPEC.PDF

### Mean Well LRS-150  ·  `meanwell_lrs_150`

- **Category:** enclosed · **Confidence:** medium · **Source file:** `meanwell.yaml`
- **Case:** 159.0 × 97.0 × 30.0 mm, 420 g, 150W
- **Output voltages:** 12/15/24/36/48 V
- **Bottom mount:** 3× M3 (Ø3.5), 3-hole, pitch —×— mm, max penetration 5.0 mm
- **Side mount:** 2× M3 (Ø3.5), 2-hole, pitch_x — mm, max penetration 3.0 mm
- **Terminal location:** 7-pin screw terminal block (AC/L, AC/N, FG, DC OUTPUT -V x2, DC OUTPUT +V x2), same face as the LED, SVR1 adjustment pot, and the side_mount holes
- **Connectors:** 7-position screw terminal. Pins 1-3 AC/L, AC/N, FG; pins 4-5 DC OUTPUT -V; pins 6-7 DC OUTPUT +V.
- **Notes:** Confidence medium -- Tier-1 source (Mean Well LRS-150-SPEC.PDF, Case No.241A, rev 2025-04-07, tolerance +-1mm), exact hole XY unresolved. Case 159x97x30mm and weight 420g cross-confirmed from both the spec table and the mechanical drawing. No 3.3V/5V output option on this series (spec table lists 12/15/24/36/48V only). bottom_mount = base/underside view: 3x M3 ("3-M3 L=5" explicit callout), dia 3.5mm labelled, 5mm max penetration; pitch/XY not confidently resolved from the rendered PDF, left null. side_mount = top/flange view: 2x M3, dia 3.5mm labelled, "2-M3 L=3.0", 3mm max penetration. Same case family/drawing style as LRS-100 (Case No. one increment higher), scaled in length only (width/height identical). Source: https://www.meanwell.com/Upload/PDF/LRS-150/LRS-150-SPEC.PDF
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
- **Bottom mount:** 4× M4 (Ø4.5), rectangular, pitch 150.0×50.0 mm, max penetration 3.0 mm
  - holes (x,y mm): [[32.5, 32.5], [182.5, 32.5], [32.5, 82.5], [182.5, 82.5]]
- **Side mount:** 4× M4 (Ø4.5), rectangular, pitch_x 150.0 mm, max penetration 5.0 mm
- **Terminal location:** 9-pin screw terminal block (AC/L, AC/N, FG, DC OUTPUT -V x3, DC OUTPUT +V x3), same face as the LED, +V ADJ pot, cooling fan, and the bottom_mount holes
- **Connectors:** 9-position screw terminal (same layout as LRS-200). Built-in DC fan with ON/OFF control on this face, blowing across the case (see "Air flow direction" on the drawing).
- **Notes:** Confidence high -- Tier-1 source (Mean Well LRS-350-SPEC.PDF, Case No.207A, rev 2025-09-12, tolerance +-1mm); dimension chain visually verified against the rendered mechanical drawing (page 4) during review 2026-07-24. IDENTICAL case footprint and hole pattern to LRS-200 (same Case-No. family, "A" suffix = fan-cooled variant) -- 215x115x30mm body, 150mm x 50mm bottom_mount grid ("4-M4 L=3mm") at 32.5mm insets on both axes (32.5 + 150 + 32.5 = 215 and 32.5 + 50 + 32.5 = 115, both exact), 150mm-pitch side_mount "4-M4(Both Sides) L=5mm". This 150x50 grid matches the community ground truth used by existing Voron PSU mounting plates. Only weight (760g vs 660g, extra mass of the fan) and wattage differ from LRS-200. Two additional drawing-only dimensions specific to this fan variant ("36.7" and "47.45") describe the fan cutout/position, not a mounting hole -- not modeled as mount fields. mount_hole_dia_mm (4.5mm) is INFERRED M4 clearance, not explicitly dimensioned. Source: https://www.meanwell.com/Upload/PDF/LRS-350/LRS-350-SPEC.PDF
- src: https://www.meanwell.com/Upload/PDF/LRS-350/LRS-350-SPEC.PDF

### Mean Well LRS-50  ·  `meanwell_lrs_50`

- **Category:** enclosed · **Confidence:** medium · **Source file:** `meanwell.yaml`
- **Case:** 99.0 × 82.0 × 30.0 mm, 210 g, 50W
- **Output voltages:** 3.3/5/12/15/24/36/48 V
- **Bottom mount:** 2× M3 (Ø3.5), 2-hole, pitch 64.0×— mm, max penetration 5.0 mm
- **Side mount:** 2× M3 (Ø3.5), 2-hole, pitch_x — mm, max penetration 3.0 mm
- **Terminal location:** 5-pin screw terminal block (AC/L, AC/N, FG, DC OUTPUT -V, DC OUTPUT +V), on the same face as the LED and the flange (side_mount) holes
- **Connectors:** 5-position screw terminal. Pin 1 AC/L, 2 AC/N, 3 FG, 4 DC OUTPUT -V, 5 DC OUTPUT +V.
- **Notes:** Confidence medium -- Tier-1 source (Mean Well LRS-50-SPEC.PDF, Case No.239A, rev 2025-04-07, mechanical page dimensioned tolerance +-1mm), but exact hole XY unresolved. Case 99x82x30mm and weight 210g cross-confirmed from BOTH the spec table (DIMENSION line) and the mechanical drawing -- high confidence on those. Two distinct hole patterns, both VERTICAL entry (no horizontal side-wall option on this case size): bottom_mount = base/underside view (ventilated bottom face), 2x M3, dia 3.5mm labelled, "2-M3 L=5" (5mm max screw penetration before risking the internal PCB). Base-view dimension chain shows hole X offsets of ~10mm and ~74mm from the left edge within a ~90mm reference span (64mm pitch, used here as bottom_mount_pitch_x_mm); the Y offset along the 82mm depth could not be confidently resolved from the rendered PDF and is left null -- extract from LRS-50-3D.zip (linked from the product page) before cutting. side_mount = the top/flange view (same face as terminals, LED): 2x M3, dia 3.5mm labelled, "2-M3 L=3.0" (3mm max penetration -- shallower boss, use shorter screws here or the OK the LED/adjustment pot area). Flange hole is ~4.5mm in from the left edge near the top corner per the drawing; exact XY for both holes not confidently resolved -- treat as informative only, verify before cutting. Source: https://www.meanwell.com/Upload/PDF/LRS-50/LRS-50-SPEC.PDF
- src: https://www.meanwell.com/Upload/PDF/LRS-50/LRS-50-SPEC.PDF

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

- **Category:** enclosed · **Confidence:** medium · **Source file:** `meanwell.yaml`
- **Case:** 230.0 × 127.0 × 40.5 mm, 1300 g, 500W
- **Output voltages:** 3.3/4/5/12/15/24/27/48 V
- **Bottom mount:** 5× M4 (Ø4.5), other, pitch —×— mm, max penetration 4.0 mm
- **Side mount:** 4× M4 (Ø4.5), rectangular, pitch_x — mm, max penetration 5.0 mm
- **Terminal location:** screw terminal blocks (TB1 3-pin AC input, TB2 6-pin DC output) plus a 4-pin CN100 connector (remote ON/OFF + remote sense), on the face opposite the built-in cooling fan
- **Connectors:** TB1 (AC input): 1 AC/L, 2 AC/N, 3 FG. TB2 (DC output): pins 1-3 DC OUTPUT -V, pins 4-6 DC OUTPUT +V. CN100 (HRS DF11-04DP-2DS or equivalent): 1 -S, 2 +S, 3 RC-, 4 RC+ (remote sense / remote on-off). Built-in DC fan for forced-air cooling.
- **Notes:** Confidence medium -- Tier-1 source (Mean Well RSP-500-SPEC.PDF, Case No.226A, rev 2025-09-26, tolerance +-1mm; also cross-listed as "USP-22530 series" on the mechanical page). Case 230x127x40.5mm (1U) and weight 1.3kg cross-confirmed from both the spec table and the drawing. bottom_mount = the corner/base view: Mean Well labels this "5-M4 L=4mm" -- 5 holes (not the clean 4-corner rectangle seen on LRS-200/350), 4mm max penetration; the 5th hole is very likely a supplementary chassis-ground point near the built-in fan rather than a true 5th structural mounting point, but this could not be confirmed from the rendered PDF, so pattern is recorded as "other" and pitch/XY are left null rather than assumed rectangular. Legible-but-unassigned raw dimensions from this view include 39.3mm, 159.7mm, and 88mm -- a future contributor with the vector PDF or 3D STEP should re-derive exact XY from these. side_mount = "4-M4(Both Sides) L=5mm", true horizontal side-wall entry (same convention as LRS-200/350), 2 holes per side; X pitch not confidently resolved (raw dims 40mm, 170mm, 2.5mm visible in that view but not cleanly assignable). mount_hole_dia_mm (4.5mm) is INFERRED M4 clearance, not explicitly dimensioned. Source: https://www.meanwell.com/Upload/PDF/RSP-500/RSP-500-SPEC.PDF
- src: https://www.meanwell.com/Upload/PDF/RSP-500/RSP-500-SPEC.PDF

### Mean Well UHP-350  ·  `meanwell_uhp_350`

- **Category:** slim_enclosed · **Confidence:** high · **Source file:** `meanwell.yaml`
- **Case:** 220.0 × 62.0 × 31.0 mm, 680 g, 350W
- **Output voltages:** 3.3/4.2/5/12/15/24/36/48/55 V
- **Bottom mount:** 4× M3 (Ø3.3), rectangular, pitch 218.2×46.4 mm, max penetration — mm
  - holes (x,y mm): [[0.9, 7.8], [219.1, 7.8], [0.9, 54.2], [219.1, 54.2]]
- **Terminal location:** screw terminal blocks -- TB1 (2-pin AC input) on one short end, TB2/TB3 (4-pin DC output, high-current) plus CN10 (2-pin DC-OK signal) on the opposite short end
- **Connectors:** TB1 (DEGSON DG28C-B-03P or equiv.): 1 AC/L, 2 AC/N, 3 FG; max mounting torque 5Kgf-cm. TB2/TB3 (Mean Well TB-HTP-200-40A or equiv.): pins 1-2 -V, pins 3-4 +V; max mounting torque 8Kgf-cm. CN10 (JST B2B-PH-K-S or equiv.): 1 DC COM, 2 DC OK +V. Fanless -- MUST be mounted to a thermally-conductive aluminum plate (or equivalent chassis) at least 450x450x3mm per Mean Well's installation guidance for the unit to meet its rated derating curve; this is a thermal requirement, not just a mechanical one.
- **Notes:** Confidence high -- Tier-1 source (Mean Well UHP-350-SPEC.PDF, Case No.232C, rev 2024-11-23, tolerance +-1mm; "R" suffix variant adds a DC-OK signal + redundant-operation function, same mechanicals). Case 220x62x31mm and weight 680g cross-confirmed from both the spec table and the drawing. VECTOR-PDF EXTRACTION 2026-07-28 (least-squares circle fits on the drawing's own bezier geometry; supersedes the earlier raster reading): the "4-ψ3.3" callout's leader line terminates at an END-PLATE EAR -- the mounting interface is 4 outward-opening 3.3mm slots on the corner ears of the two 3mm end plates, at the case bottom plane. The 4 small circles ON the case face at ~10.1mm end insets are case-assembly screws, NOT mounting holes -- do not mount to them. ACROSS WIDTH (Y): the drawing's own chain closes exactly (7.8 + 46.4 + 7.8 = 62) and the fitted ear centres measure 7.79/46.39/7.82 against it -- pitch_y 46.4 with 7.8 insets. ALONG LENGTH (X): slot centres vector-measure 0.9mm inside each end face (pitch_x 218.2, closing the 220 envelope exactly); this value is measured from the drawing geometry, not carried by a printed dimension -- and because the slots open OUTWARD through the end faces, any screw spacing from ~218.2 up to the 220 envelope engages the ears. FAMILY CROSS-CHECK: UHP-200 (Case 249B, 55mm-wide case) shows the identical construct, 6.5 + 42 + 6.5 = 55. CORRECTION of the previous record: pitch_x 110 was a misread -- the drawing's "110"/"15.5" dimension the tc (max case temperature) measurement point on the finned side elevation, not any mounting feature. bottom_mount_interface clearance_ears: no thread in the case; the screw clamps the ear and threads into the mounting plate below (Mean Well install guidance: "M3*4" into a thermally-conductive aluminum plate >= 450x450x3mm for the full derating curve -- a THERMAL requirement, not just mechanical), and the screw path lies outside the case wall, so bottom_mount_max_penetration_mm is null (not applicable) rather than a safety depth. Source: https://www.meanwell.com/Upload/PDF/UHP-350(R)/UHP-350-SPEC.PDF (mechanical dims on page 5; installation/aluminum-plate requirement on page 6).
- src: https://www.meanwell.com/Upload/PDF/UHP-350(R)/UHP-350-SPEC.PDF
