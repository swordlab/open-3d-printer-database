# Open 3D Printer Database

A community-driven, open-source database of 3D printer specifications with **cost data** for calculating print pricing and amortization.

Unlike slicer-only databases (OrcaSlicer, UVtools), this database includes **economic data**: purchase price, power consumption, maintenance costs — everything you need to calculate the real cost of a 3D print.

## What's included

| Data | FDM | SLA/MSLA/DLP |
|------|-----|--------------|
| Manufacturer & Model | ✅ | ✅ |
| Build volume | ✅ | ✅ |
| Resolution / Pixel size | — | ✅ |
| Nozzle diameter | ✅ | — |
| Max print speed | ✅ | — |
| **Power consumption (W)** | ✅ | ✅ |
| **Typical price (EUR/USD)** | ✅ | ✅ |
| **Maintenance cost/year** | ✅ | ✅ |
| **Heater power (W)** | ✅ | — |
| **Typical temperatures** | ✅ | — |

## Quick start

### Use the aggregated catalog

Download the latest `catalog.json` (single file, all printers):

```bash
curl -sL https://raw.githubusercontent.com/swordlab/open-3d-printer-database/main/catalog.json -o printers.json
```

### Use in your project

```python
import json, urllib.request

url = "https://raw.githubusercontent.com/swordlab/open-3d-printer-database/main/catalog.json"
catalog = json.loads(urllib.request.urlopen(url).read())

# Find a printer
for p in catalog:
    if "bambu" in p.get("full_name", "").lower() and "x1" in p.get("model", "").lower():
        print(f"{p['full_name']}: {p['typical_price_eur']}€, {p['power_w']}W")
```

### Use in JavaScript

```javascript
const res = await fetch('https://raw.githubusercontent.com/swordlab/open-3d-printer-database/main/catalog.json');
const catalog = await res.json();
const bambu = catalog.filter(p => p.full_name?.includes('Bambu'));
```

## Data sources

| Source | What it provides | License |
|--------|-----------------|---------|
| **Community contributions** | Prices, power, maintenance (the unique part) | CC-BY-4.0 |
| [UVtools](https://github.com/sn4k3/UVtools) | SLA resolution, build volume (152 printers) | AGPL-3.0 |
| [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) | FDM build volume, nozzle, speed | AGPL-3.0 |

## How to contribute

### Add a new printer

1. Fork this repo
2. Create a JSON file in `printers/fdm/` or `printers/sla/` following the schema:

```json
{
  "manufacturer": "Bambu Lab",
  "model": "X1 Carbon",
  "technology": "FDM",
  "released": "2023",
  "status": "current",
  "specs": {
    "build_volume_mm": { "x": 256, "y": 256, "z": 256 },
    "nozzle_diameter_mm": 0.4,
    "max_speed_mm_s": 500,
    "power_w": 1000,
    "heater_power_w": 350
  },
  "cost": {
    "typical_price_eur": 1199,
    "typical_price_usd": 1299,
    "maintenance_eur_year": 100
  },
  "contributed_by": "your-github-username"
}
```

3. Open a Pull Request

### Update an existing printer (price drop, correction)

Edit the relevant JSON file and submit a PR with a note explaining the change.

### Validate your contribution

```bash
python3 scripts/validate.py printers/fdm/bambu-lab/x1-carbon.json
```

## Used by

- [Stimalo](https://stimalo.com) — Free 3D printing cost calculator

## Stats

- **357 printers** (163 FDM + 194 SLA) from 59 manufacturers
- **517 materials** (filaments + resins) from 57 brands
- Updated regularly by the community

## Materials catalog (NEW)

Download `materials_catalog.json` — 517 filaments and resins with density, price, and temperature data:

```bash
curl -sL https://raw.githubusercontent.com/swordlab/open-3d-printer-database/main/materials_catalog.json -o materials.json
```

Brands included: 3DJake, Amazon Basics, Anycubic, AzureFilm, Bambu Lab, COEX 3D, Creality, Deeple, Elegoo, Eolas Prints, Eryone, eSUN, FDplast, FlashForge, ICE Filaments, Inslogic, JAYO, Overture, Polymaker, Prusa, Rat Rig, RBD, Recreus, Siraya Tech, Smartfil, Sting3D, Sunlu, Tianse, Tinmorry, Yxpolyer, and more.

## License

- **Data files** (`printers/`, `catalog.json`): [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/) — free to use, share, and adapt with attribution.
- **Scripts** (`scripts/`): MIT License

## Credits

- Data enrichment from [UVtools](https://github.com/sn4k3/UVtools) by sn4k3 (AGPL-3.0)
- FDM data from [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) community profiles
- Created and maintained by [@swordlab](https://github.com/swordlab)
