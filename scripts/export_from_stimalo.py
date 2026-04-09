#!/usr/bin/env python3
"""
Export Stimalo's printer_catalog.json into individual JSON files
following the open-3d-printer-database schema.

Also generates the aggregated catalog.json at the repo root.

Usage:
  python3 scripts/export_from_stimalo.py /path/to/stimalo/data/printer_catalog.json
"""

import json
import os
import re
import sys
from pathlib import Path


def slugify(text):
    """Convert 'Bambu Lab X1 Carbon' to 'x1-carbon'."""
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    return text


def manufacturer_slug(name):
    """Convert 'Bambu Lab' to 'bambu-lab'."""
    return slugify(name)


def convert_entry(entry):
    """Convert a Stimalo catalog entry to open-3d-printer-database schema."""
    tech = entry.get("technology", "FDM")

    result = {
        "manufacturer": entry.get("manufacturer", "Unknown"),
        "model": entry.get("model", entry.get("full_name", "Unknown")),
        "technology": tech,
        "status": "current",
        "specs": {},
        "cost": {},
        "sources": [],
    }

    # Specs
    bv = entry.get("build_volume_mm")
    if bv and isinstance(bv, dict):
        result["specs"]["build_volume_mm"] = bv
    if entry.get("build_volume_cm3"):
        result["specs"]["build_volume_cm3"] = entry["build_volume_cm3"]
    if entry.get("nozzle_diameter_mm"):
        result["specs"]["nozzle_diameter_mm"] = entry["nozzle_diameter_mm"]
    if entry.get("max_speed_mm_s"):
        result["specs"]["max_speed_mm_s"] = entry["max_speed_mm_s"]
    if entry.get("power_w") is not None:
        result["specs"]["power_w"] = entry["power_w"]
    if entry.get("heater_power_w") is not None:
        result["specs"]["heater_power_w"] = entry["heater_power_w"]
    if entry.get("resolution_x"):
        result["specs"]["resolution_x"] = entry["resolution_x"]
        result["specs"]["resolution_y"] = entry.get("resolution_y")
        result["specs"]["pixel_size_um"] = entry.get("pixel_size_um")

    # Cost
    if entry.get("typical_price_eur") is not None:
        result["cost"]["typical_price_eur"] = entry["typical_price_eur"]
    if entry.get("maintenance_eur_year") is not None:
        result["cost"]["maintenance_eur_year"] = entry["maintenance_eur_year"]

    # Temperatures
    if entry.get("typical_bed_temp") is not None or entry.get("typical_nozzle_temp") is not None:
        result["temperatures"] = {
            "typical_bed_temp": entry.get("typical_bed_temp"),
            "typical_nozzle_temp": entry.get("typical_nozzle_temp"),
        }

    # Sources
    source = entry.get("source", "overlay")
    if source == "uvtools":
        result["sources"].append("UVtools (github.com/sn4k3/UVtools)")
    if entry.get("power_w") is not None:
        result["sources"].append("stimalo overlay (community)")

    result["contributed_by"] = "swordlab"

    return result


def main():
    repo_root = Path(__file__).parent.parent
    printers_dir = repo_root / "printers"

    # Find Stimalo catalog
    if len(sys.argv) > 1:
        catalog_path = Path(sys.argv[1])
    else:
        # Default: look in sibling Stimalo project
        catalog_path = repo_root.parent / "GESTORE STAMPE 3D" / "data" / "printer_catalog.json"

    if not catalog_path.exists():
        print(f"[error] Catalog not found: {catalog_path}")
        sys.exit(1)

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    entries = [e for e in catalog if not e.get("_metadata")]

    print(f"[info] Loaded {len(entries)} entries from {catalog_path.name}")

    # Clear existing printer files
    for tech_dir in ["fdm", "sla"]:
        d = printers_dir / tech_dir
        d.mkdir(parents=True, exist_ok=True)
        for f in d.iterdir():
            if f.suffix == ".json":
                f.unlink()

    # Export individual files
    all_entries = []
    by_manufacturer = {}

    for entry in entries:
        converted = convert_entry(entry)
        manufacturer = converted["manufacturer"]
        model = converted["model"]
        tech = converted["technology"].lower()
        if tech in ("msla", "dlp"):
            tech = "sla"

        # Create manufacturer subfolder
        mfr_slug = manufacturer_slug(manufacturer)
        mfr_dir = printers_dir / tech / mfr_slug
        mfr_dir.mkdir(parents=True, exist_ok=True)

        # Write individual file
        model_slug = slugify(model)
        filepath = mfr_dir / f"{model_slug}.json"
        filepath.write_text(json.dumps(converted, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        # Flat entry for catalog.json
        flat = {
            "full_name": entry.get("full_name", f"{manufacturer} {model}"),
            **converted,
        }
        all_entries.append(flat)

        by_manufacturer.setdefault(manufacturer, []).append(model)

    # Sort catalog
    all_entries.sort(key=lambda e: (e.get("manufacturer", ""), e.get("model", "")))

    # Write aggregated catalog.json
    catalog_out = repo_root / "catalog.json"
    catalog_out.write_text(json.dumps(all_entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Stats
    fdm = sum(1 for e in all_entries if e.get("technology") == "FDM")
    sla = len(all_entries) - fdm
    with_price = sum(1 for e in all_entries if e.get("cost", {}).get("typical_price_eur"))
    mfr_count = len(by_manufacturer)

    print(f"\n[ok] Exported {len(all_entries)} printers")
    print(f"  FDM: {fdm}  |  SLA: {sla}")
    print(f"  Manufacturers: {mfr_count}")
    print(f"  With price data: {with_price}")
    print(f"\n  Files written to: {printers_dir}")
    print(f"  Catalog: {catalog_out}")
    print(f"\n  Top manufacturers:")
    for mfr, models in sorted(by_manufacturer.items(), key=lambda x: -len(x[1]))[:10]:
        print(f"    {mfr}: {len(models)} models")


if __name__ == "__main__":
    main()
