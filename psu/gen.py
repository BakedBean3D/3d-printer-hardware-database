#!/usr/bin/env python3
"""Aggregate the per-manufacturer psu/*.yaml into:
  - psu.json   (single array, for code / parametric CAD import)
  - PSU.md     (human-readable summary table + per-unit detail)

The per-manufacturer YAML files are the source of truth. Re-run after editing:
    python psu/gen.py
"""
import yaml, json, os, glob
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_GLOB = os.path.join(HERE, "*.yaml")


def load():
    units = []
    for f in sorted(glob.glob(SOURCE_GLOB)):
        data = yaml.safe_load(open(f)) or []
        for u in data:
            u = dict(u)
            u["_source_file"] = os.path.basename(f)
            units.append(u)
    return units


def fmt(v):
    return "—" if v is None else v


def md_table(units):
    rows = ["| Unit | Mfr | Category | L×W×H (mm) | Weight | Watt | Voltages | Bottom mount | Side mount | Conf |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for u in units:
        L, W, H = u.get("length_mm"), u.get("width_mm"), u.get("height_mm")
        lwh = f"{fmt(L)}×{fmt(W)}×{fmt(H)}" if (L or W or H) else "—"
        volts = "/".join(str(v) for v in (u.get("output_voltages_v") or [])) or "—"
        bm = u.get("bottom_mount_pattern") or "—"
        if u.get("bottom_mount_hole_count"):
            bm = f"{u['bottom_mount_hole_count']}×{fmt(u.get('bottom_mount_screw'))} ({bm})"
        sm = u.get("side_mount_pattern") or "—"
        if u.get("side_mount_hole_count"):
            sm = f"{u['side_mount_hole_count']}×{fmt(u.get('side_mount_screw'))} ({sm})"
        elif u.get("din_rail_compatible"):
            sm = f"DIN {fmt(u.get('din_rail_type'))}"
        rows.append("| {name} | {mfr} | {cat} | {lwh} | {wt} | {watt}W | {volts} | {bm} | {sm} | {conf} |".format(
            name=u.get("name"), mfr=u.get("manufacturer"), cat=u.get("category"), lwh=lwh,
            wt=f"{fmt(u.get('weight_g'))}g", watt=fmt(u.get("wattage_w")), volts=volts,
            bm=bm, sm=sm, conf=u.get("confidence")))
    return "\n".join(rows)


def write_json(units):
    out = os.path.join(HERE, "psu.json")
    json.dump(units, open(out, "w"), indent=2)
    return out


def write_md(units):
    out = os.path.join(HERE, "PSU.md")
    conf = Counter(u.get("confidence") for u in units)
    by_mfr = defaultdict(list)
    for u in units:
        by_mfr[u.get("manufacturer", "?")].append(u)

    L = []
    L.append("# PSU Mounting Dimensions")
    L.append("")
    L.append("**Generated** from the per-manufacturer `*.yaml` in this directory — do not hand-edit; "
             "run `python psu/gen.py`. The YAML files are the source of truth.")
    L.append("")
    L.append(f"- **Total units:** {len(units)}")
    L.append(f"- **Confidence:** {conf.get('high',0)} high · {conf.get('medium',0)} medium · {conf.get('low',0)} low")
    L.append("- **Aggregate for code:** `psu.json`")
    L.append("- **License:** data under ODbL-1.0 (database) + DbCL-1.0 (contents), © BakedBean3D. "
             "See [`DATA_LICENSE.md`](../DATA_LICENSE.md).")
    L.append("")
    L.append("## Conventions")
    L.append("")
    L.append("- `length_mm`/`width_mm`/`height_mm` follow the vendor's own L×W×H convention where stated; "
             "for DIN-rail units (vendor convention W×H×D) these are remapped length=D, width=W, height=H — "
             "read each record's `notes` for the exact mapping.")
    L.append("- Every enclosed/slim_enclosed unit carries TWO mount patterns: `bottom_mount_*` (vertical-entry "
             "hole pattern for flat/plate mounting — the one almost every printer mount design uses) and "
             "`side_mount_*` (the second documented pattern — true horizontal side-wall entry on the larger "
             "LRS-200/350/RSP-500 case family, or a second vertical top-flange pattern on the smaller "
             "LRS-50/100/150 case family). Read `notes` to know which physical face `side_mount` refers to "
             "for a given record — it is not always a horizontal entry.")
    L.append("- `din_rail_compatible` + `din_rail_type` describe spring-clip DIN-rail units (MDR/EDR series); "
             "these have no bolt-hole mount pattern (`bottom_mount_pattern`/`side_mount_pattern` = `none`).")
    L.append("- `mount_*_max_penetration_mm` is the maximum screw length Mean Well specifies before risking "
             "the internal PCB — respect it, this is a shock/short hazard, not just a mechanical fit issue.")
    L.append("- `mount_*_hole_dia_mm` is often inferred from the screw size (M3→3.5, M4→4.5 in this dataset) "
             "where the vendor drawing didn't explicitly dimension the bore — flagged per-record in `notes`.")
    L.append("- `null` = genuinely unknown; **never** assume 0.")
    L.append("- **Confidence:** `high` = dimensions extracted from the vendor's vector-text PDF and "
             "cross-validated (symmetric/arithmetic-checked); `medium` = case dimensions and screw/depth specs "
             "verified from the vendor mechanical drawing, but exact hole XY/pitch could not be fully resolved "
             "from the published PDF — extract from vendor 3D STEP/DXF before cutting; `low` = not "
             "authoritatively found — measure first.")
    L.append("")
    L.append("## All units")
    L.append("")
    L.append(md_table(sorted(units, key=lambda u: (u.get("manufacturer",""), u.get("series",""), u.get("name","")))))
    L.append("")
    for mfr in sorted(by_mfr):
        L.append(f"## {mfr}")
        L.append("")
        for u in sorted(by_mfr[mfr], key=lambda u: u.get("name","")):
            L.append(f"### {u.get('name')}  ·  `{u.get('id')}`")
            L.append("")
            L.append(f"- **Category:** {u.get('category')} · **Confidence:** {u.get('confidence')} · **Source file:** `{u.get('_source_file')}`")
            L.append(f"- **Case:** {fmt(u.get('length_mm'))} × {fmt(u.get('width_mm'))} × {fmt(u.get('height_mm'))} mm, "
                     f"{fmt(u.get('weight_g'))} g, {fmt(u.get('wattage_w'))}W")
            volts = "/".join(str(v) for v in (u.get("output_voltages_v") or []))
            L.append(f"- **Output voltages:** {volts or '—'} V")
            if u.get("bottom_mount_hole_count"):
                L.append(f"- **Bottom mount:** {u['bottom_mount_hole_count']}× {fmt(u.get('bottom_mount_screw'))} "
                         f"(Ø{fmt(u.get('bottom_mount_hole_dia_mm'))}), {fmt(u.get('bottom_mount_pattern'))}, "
                         f"pitch {fmt(u.get('bottom_mount_pitch_x_mm'))}×{fmt(u.get('bottom_mount_pitch_y_mm'))} mm, "
                         f"max penetration {fmt(u.get('bottom_mount_max_penetration_mm'))} mm")
                if u.get("bottom_mount_holes_xy"):
                    L.append(f"  - holes (x,y mm): {u['bottom_mount_holes_xy']}")
            if u.get("side_mount_hole_count"):
                L.append(f"- **Side mount:** {u['side_mount_hole_count']}× {fmt(u.get('side_mount_screw'))} "
                         f"(Ø{fmt(u.get('side_mount_hole_dia_mm'))}), {fmt(u.get('side_mount_pattern'))}, "
                         f"pitch_x {fmt(u.get('side_mount_pitch_x_mm'))} mm, "
                         f"max penetration {fmt(u.get('side_mount_max_penetration_mm'))} mm")
                if u.get("side_mount_holes_xy"):
                    L.append(f"  - holes (x,y mm): {u['side_mount_holes_xy']}")
            if u.get("din_rail_compatible"):
                L.append(f"- **DIN rail:** {fmt(u.get('din_rail_type'))}")
            if u.get("terminal_location"):
                L.append(f"- **Terminal location:** {u['terminal_location']}")
            if u.get("connector_notes"):
                L.append(f"- **Connectors:** {u['connector_notes']}")
            if u.get("notes"):
                L.append(f"- **Notes:** {u['notes']}")
            for s in (u.get("sources") or []):
                L.append(f"- src: {s}")
            L.append("")
    open(out, "w").write("\n".join(L))
    return out


if __name__ == "__main__":
    units = load()
    j = write_json(units)
    m = write_md(units)
    print(f"{len(units)} units -> {os.path.basename(j)}, {os.path.basename(m)}")
