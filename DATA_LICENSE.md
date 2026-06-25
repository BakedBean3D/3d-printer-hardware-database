# Data licensing

This repository is an **open database**. It is licensed so that anyone — including
commercial tools and freemium services — can use the hardware specifications, while
keeping the database itself open and attributed.

## TL;DR

| What | License | File |
|---|---|---|
| **The database** (structure, selection, arrangement of records) | **ODbL-1.0** (Open Database License) | [`LICENSE`](LICENSE) |
| **The contents** (the individual records / factual specs) | **DbCL-1.0** (Database Contents License) | [`LICENSE-DbCL`](LICENSE-DbCL) |
| **The code** (`gen.py`, `convert_data.py`, scripts) | **MIT** | [`LICENSE-CODE`](LICENSE-CODE) |

> SPDX: data is `ODbL-1.0` over `DbCL-1.0`; code is `MIT`.

This is the same dual-license model used by OpenStreetMap and most serious open
databases. It is the deliberate, canonical choice for the open-data + freemium-tool
strategy: the data stays open and share-alike, downstream tools (free or paid) may
build on it, and the database must stay attributed and open.

## What you can do

- **Use it commercially.** Yes — including in paid/freemium products (e.g. an
  electronics-bay designer, a parametric CAD generator). The DbCL explicitly permits
  commercial use of the contents with no field-of-endeavour restriction.
- **Produce works from it.** STL/STEP/3MF mounts, layouts, BOMs, visualisations, apps
  — these are *Produced Works* under the ODbL and may be licensed however you like.
  You do **not** have to open-source your app or your generated models.

## What you must do (ODbL obligations)

1. **Attribute.** Wherever you make the data or a Produced Work publicly available,
   include the attribution notice below and keep any existing notices intact.
2. **Keep the database open (share-alike).** If you publicly use a *modified version
   of the database itself* (added/changed/removed records, or a derived database),
   you must offer that modified database under ODbL-1.0 as well. This share-alike
   applies to the **database**, not to your app or to individual generated parts.
3. **No DRM** on a public ODbL copy of the database that restricts these freedoms.

> Note the boundary: building an app that *queries* this data and generates parts is
> a Produced Work (no share-alike on your app). Publishing a *changed copy of the
> database* triggers share-alike on that database. Most tool builders only do the
> former.

## Attribution notice (copy this)

```
Contains data from the 3D Printer Hardware Database
(https://github.com/BakedBean3D/3d-printer-hardware-database),
© BakedBean3D, licensed under ODbL-1.0 (database) and DbCL-1.0 (contents).
```

A shorter in-app form (e.g. a footer or "Data sources" page):

```
Hardware data © BakedBean3D · ODbL-1.0 — github.com/BakedBean3D/3d-printer-hardware-database
```

## Per-record provenance

Most records also carry their own `sources` and a `confidence` tier in the data. That
provenance is part of the Contents and should be preserved when records are
redistributed — it is what makes the data trustworthy for CAD use (and remember:
`null` means *unknown*, never `0`).

## Contributing

By contributing data (a pull request, a new record, a correction) you agree to
license your contribution under the **same terms**: ODbL-1.0 for the database and
DbCL-1.0 for the contents (code contributions under MIT). Only contribute
specifications you have the right to share — prefer vendor datasheets, official
mechanical drawings, and measured parts, and cite the source in the record.
