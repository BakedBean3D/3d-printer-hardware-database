#!/usr/bin/env python3
"""Import motors from CSV, dedup against existing data, output per-manufacturer YAML."""
import csv
import os
import glob
import yaml
from collections import defaultdict


class LiteralStr(str):
    pass


def literal_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(LiteralStr, literal_representer)


def load_existing_motors():
    """Load all existing motor IDs from motors/ directory."""
    existing = {}
    for filepath in glob.glob("motors/*.yaml"):
        with open(filepath) as f:
            data = yaml.safe_load(f) or []
        for entry in data:
            existing[entry["id"]] = entry
    return existing


def make_id(manufacturer, model):
    """Generate a consistent ID from manufacturer and model."""
    raw = f"{manufacturer}_{model}".lower()
    raw = raw.replace("-", "_").replace("(", "").replace(")", "")
    raw = raw.replace(" ", "_").replace("+", "_plus")
    return raw


def slug(name):
    return name.lower().replace(" ", "_").replace("'", "").replace("/", "_")


def parse_csv(filepath):
    """Parse the motor CSV. Columns:
    0: Full ID (manufacturer-model)
    1: Manufacturer
    2: Model
    3: NEMA size (frame number)
    4: Body length (mm)
    5: Step angle (degrees)
    6: Rated current (A)
    7: Holding torque (N·cm)
    8: Resistance (Ohms)
    9: Inductance (mH)
    10: Weight (g)
    11: Usage notes (e.g. "V0.1 AB")
    12: Datasheet URL
    13-15: (unused)
    """
    motors = []
    seen_ids = set()

    with open(filepath, newline="") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 11:
                continue

            manufacturer = row[1].strip()
            model = row[2].strip()
            motor_id = make_id(manufacturer, model)

            if motor_id in seen_ids:
                continue
            seen_ids.add(motor_id)

            nema = int(row[3]) if row[3].strip() else 17
            body_length = float(row[4]) if row[4].strip() else 0.0
            step_angle = float(row[5]) if row[5].strip() else 1.8
            rated_current = float(row[6]) if row[6].strip() else 0.0
            holding_torque = float(row[7]) if row[7].strip() else 0.0
            inductance = float(row[8]) if row[8].strip() else 0.0
            resistance = float(row[9]) if row[9].strip() else 0.0
            weight = int(float(row[10])) if row[10].strip() else 0
            usage = row[11].strip() if len(row) > 11 else ""
            datasheet = row[12].strip() if len(row) > 12 else ""

            # Calculate recommended run_current (50% of rated as safe starting point)
            rec_current = round(rated_current * 0.5, 2) if rated_current > 0 else 0.0

            # Build notes
            notes_parts = []
            if usage:
                notes_parts.append(f"Common use: {usage}.")
            notes_parts.append(f"Rated {rated_current}A RMS.")
            notes_parts.append(f"Run current {rec_current}A (50% rated, conservative start).")
            if datasheet:
                notes_parts.append(f"Ref: {datasheet}")
            else:
                notes_parts.append("Ref: community spreadsheet, unverified")

            notes = " ".join(notes_parts)

            frame_size = f"NEMA{nema}"

            motor = {
                "id": motor_id,
                "name": f"{manufacturer}-{model}" if not row[0].startswith(manufacturer) else row[0].strip(),
                "manufacturer": manufacturer,
                "frame_size": frame_size,
                "body_length_mm": body_length,
                "rated_current_amps": rated_current,
                "recommended_run_current": rec_current,
                "holding_torque_ncm": holding_torque,
                "inductance_mh": inductance,
                "resistance_ohms": resistance,
                "step_angle": step_angle,
                "weight": weight,
                "tooth_count": 0,
                "notes": notes,
            }

            if datasheet:
                motor["datasheet_url"] = datasheet

            motors.append(motor)

    return motors


def write_yaml(data, filepath):
    def clean(d):
        result = {}
        for k, v in d.items():
            if isinstance(v, str) and len(v) > 80:
                result[k] = LiteralStr(v)
            else:
                result[k] = v
        return result

    cleaned = [clean(d) for d in data]
    with open(filepath, "w") as f:
        yaml.dump(
            cleaned,
            f,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
            width=120,
        )


def main():
    csv_path = "/Users/mjohnson/Desktop/motor db.csv"
    print(f"Parsing CSV: {csv_path}")
    csv_motors = parse_csv(csv_path)
    print(f"  Found {len(csv_motors)} unique motors in CSV")

    existing = load_existing_motors()
    print(f"  Existing in database: {len(existing)} motors")

    # Find new motors (not already in database)
    new_motors = []
    skipped = []
    for motor in csv_motors:
        if motor["id"] in existing:
            skipped.append(motor["id"])
        else:
            new_motors.append(motor)

    print(f"  New motors to add: {len(new_motors)}")
    print(f"  Skipped (already exist): {len(skipped)}")
    if skipped:
        print(f"    {', '.join(skipped[:10])}{'...' if len(skipped) > 10 else ''}")

    # Group new motors by manufacturer
    by_mfr = defaultdict(list)
    for motor in new_motors:
        by_mfr[motor["manufacturer"]].append(motor)

    # Merge with existing files or create new ones
    for mfr, motors in sorted(by_mfr.items()):
        filepath = f"motors/{slug(mfr)}.yaml"
        if os.path.exists(filepath):
            with open(filepath) as f:
                existing_data = yaml.safe_load(f) or []
            combined = existing_data + motors
        else:
            combined = motors

        write_yaml(combined, filepath)
        print(f"  Wrote {filepath} ({len(combined)} total, +{len(motors)} new)")


if __name__ == "__main__":
    main()
