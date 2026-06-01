#!/usr/bin/env bash
# Sincronizza questo repo pubblico con i cataloghi Stimalo (fonte di verita').
# Flusso a senso unico: Stimalo -> repo pubblico. Non tocca mai i dati Stimalo.
#
# Uso:
#   scripts/sync_from_stimalo.sh [/percorso/a/stimalo/data]
# Default: ../GESTORE STAMPE 3D/data  (repo clonato come sibling del progetto Stimalo)
#
# Dopo il sync NON pusha da solo: rivedi `git status`/`git diff` e poi committa/pusha.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="${1:-$REPO_ROOT/../GESTORE STAMPE 3D/data}"

if [ ! -f "$DATA_DIR/printer_catalog.json" ]; then
  echo "[errore] catalogo non trovato: $DATA_DIR/printer_catalog.json" >&2
  echo "Passa il path della cartella data/ di Stimalo come primo argomento." >&2
  exit 1
fi

echo "Sorgente: $DATA_DIR"

# Stampanti: rigenera catalog.json + file per-stampante
python3 "$REPO_ROOT/scripts/export_from_stimalo.py" "$DATA_DIR/printer_catalog.json"

# Materiali: copia diretta (stesso schema lato Stimalo)
cp "$DATA_DIR/materials_catalog.json" "$REPO_ROOT/materials_catalog.json"

# Aggiorna i conteggi nel README
python3 - "$REPO_ROOT" <<'PY'
import json, re, sys
root = sys.argv[1]
p = json.load(open(f"{root}/catalog.json", encoding="utf-8"))
m = json.load(open(f"{root}/materials_catalog.json", encoding="utf-8"))
fdm = sum(1 for e in p if e.get("technology") == "FDM")
sla = len(p) - fdm
mfr = len({e.get("manufacturer", "").strip() for e in p if e.get("manufacturer")})
mbrands = len({e.get("brand", "").strip() for e in m if e.get("brand")})
r = open(f"{root}/README.md", encoding="utf-8").read()
r = re.sub(r"\*\*\d+ printers\*\* \(\d+ FDM \+ \d+ SLA\) from \d+\+? manufacturers",
           f"**{len(p)} printers** ({fdm} FDM + {sla} SLA) from {mfr} manufacturers", r)
r = re.sub(r"\*\*\d+ materials\*\* \(filaments \+ resins\) from \d+ brands",
           f"**{len(m)} materials** (filaments + resins) from {mbrands} brands", r)
r = re.sub(r"Download `materials_catalog\.json` — \d+ filaments and resins",
           f"Download `materials_catalog.json` — {len(m)} filaments and resins", r)
open(f"{root}/README.md", "w", encoding="utf-8").write(r)
print(f"README aggiornato: {len(p)} stampanti, {len(m)} materiali")
PY

echo ""
echo "Sync completato. Rivedi le modifiche e poi:"
echo "  git -C \"$REPO_ROOT\" add -A && git -C \"$REPO_ROOT\" commit -m 'Update catalogs' && git -C \"$REPO_ROOT\" push"
