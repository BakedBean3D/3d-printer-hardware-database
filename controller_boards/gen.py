#!/usr/bin/env python3
"""Aggregate the per-manufacturer controller_boards/*.yaml into:
  - controller_boards.json   (single array, for code / parametric CAD import)
  - CONTROLLER_BOARDS.md     (human-readable summary table + per-board detail)

The per-manufacturer YAML files are the source of truth. Re-run after editing:
    python controller_boards/gen.py
"""
import yaml, json, os, glob
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE_GLOB = os.path.join(HERE, "*.yaml")


def load():
    boards = []
    for f in sorted(glob.glob(SOURCE_GLOB)):
        data = yaml.safe_load(open(f)) or []
        for b in data:
            b = dict(b)
            b["_source_file"] = os.path.basename(f)
            boards.append(b)
    return boards


def fmt(v):
    return "—" if v is None else v


def write_json(boards):
    out = os.path.join(HERE, "controller_boards.json")
    json.dump(boards, open(out, "w"), indent=2)
    return out


def md_table(boards):
    rows = ["| Board | Mfr | Cat | PCB L×W (mm) | Thk | Screw | Pattern | Pitch X×Y | Holes | Conf |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    for b in boards:
        L, W = b.get("pcb_length_mm"), b.get("pcb_width_mm")
        lw = f"{fmt(L)}×{fmt(W)}" if (L or W) else "—"
        px, py = b.get("mount_pitch_x_mm"), b.get("mount_pitch_y_mm")
        pitch = f"{fmt(px)}×{fmt(py)}" if (px or py) else "—"
        rows.append("| {name} | {mfr} | {cat} | {lw} | {thk} | {screw} | {pat} | {pitch} | {hc} | {conf} |".format(
            name=b.get("name"), mfr=b.get("manufacturer"), cat=b.get("category"), lw=lw,
            thk=fmt(b.get("pcb_thickness_mm")), screw=fmt(b.get("mount_screw")),
            pat=fmt(b.get("mount_pattern")), pitch=pitch, hc=fmt(b.get("mount_hole_count")),
            conf=b.get("confidence")))
    return "\n".join(rows)


def write_md(boards):
    out = os.path.join(HERE, "CONTROLLER_BOARDS.md")
    conf = Counter(b.get("confidence") for b in boards)
    by_mfr = defaultdict(list)
    for b in boards:
        by_mfr[b.get("manufacturer", "?")].append(b)

    L = []
    L.append("# Controller Board Mounting Dimensions")
    L.append("")
    L.append("**Generated** from the per-manufacturer `*.yaml` in this directory — do not hand-edit; "
             "run `python controller_boards/gen.py`. The YAML files are the source of truth.")
    L.append("")
    L.append(f"- **Total boards:** {len(boards)}")
    L.append(f"- **Confidence:** {conf.get('high',0)} high · {conf.get('medium',0)} medium · {conf.get('low',0)} low")
    L.append(f"- **Aggregate for code:** `controller_boards.json`")
    L.append("")
    L.append("## Conventions")
    L.append("")
    L.append("- `pcb_length_mm` = X (longer edge); `pcb_width_mm` = Y (shorter edge).")
    L.append("- `mount_pitch_x/y_mm` = center-to-center hole spacing.")
    L.append("- `mount_holes_xy` (where present) = each hole `[x,y]` from the PCB **bottom-left corner** "
             "unless the entry's `notes` say a drawing datum is used — always read the note.")
    L.append("- `mount_hole_dia_mm` is usually inferred from the screw size (M3→3.2) — vendor SIZE drawings "
             "rarely annotate the bore. Treat as nominal clearance.")
    L.append("- `null` = genuinely unknown; **never** assume 0. `pcb_thickness_mm` defaults to 1.6 where unstated.")
    L.append("- **Confidence:** `high` = from vendor/community CAD (KiCad/STEP/dimensioned drawing); "
             "`medium` = outline firm, hole pitch inferred; `low` = not authoritatively found — **measure before cutting.**")
    L.append("")
    L.append("## All boards")
    L.append("")
    L.append(md_table(sorted(boards, key=lambda b: (b.get("manufacturer",""), b.get("name","")))))
    L.append("")
    for mfr in sorted(by_mfr):
        L.append(f"## {mfr}")
        L.append("")
        for b in sorted(by_mfr[mfr], key=lambda b: b.get("name","")):
            L.append(f"### {b.get('name')}  ·  `{b.get('id')}`")
            L.append("")
            L.append(f"- **Category:** {b.get('category')} · **Confidence:** {b.get('confidence')} · **Source file:** `{b.get('_source_file')}`")
            L.append(f"- **PCB:** {fmt(b.get('pcb_length_mm'))} × {fmt(b.get('pcb_width_mm'))} mm, {fmt(b.get('pcb_thickness_mm'))} mm thick")
            L.append(f"- **Mounting:** {fmt(b.get('mount_hole_count'))}× {fmt(b.get('mount_screw'))} "
                     f"(Ø{fmt(b.get('mount_hole_dia_mm'))}), {fmt(b.get('mount_pattern'))}, "
                     f"pitch {fmt(b.get('mount_pitch_x_mm'))}×{fmt(b.get('mount_pitch_y_mm'))} mm")
            if b.get("mount_holes_xy"):
                L.append(f"  - holes (x,y mm): {b['mount_holes_xy']}")
            sh, ch = b.get("standoff_height_mm"), b.get("component_height_top_mm")
            if sh is not None or ch is not None:
                L.append(f"- **Clearance:** standoff {fmt(sh)} mm, top component {fmt(ch)} mm")
            if b.get("connector_notes"):
                L.append(f"- **Connectors:** {b['connector_notes']}")
            if b.get("notes"):
                L.append(f"- **Notes:** {b['notes']}")
            for s in (b.get("sources") or []):
                L.append(f"- src: {s}")
            L.append("")
    open(out, "w").write("\n".join(L))
    return out


if __name__ == "__main__":
    boards = load()
    j = write_json(boards)
    m = write_md(boards)
    print(f"{len(boards)} boards -> {os.path.basename(j)}, {os.path.basename(m)}")
