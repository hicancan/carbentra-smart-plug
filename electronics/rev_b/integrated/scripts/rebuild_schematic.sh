#!/bin/bash
set -euo pipefail
R="$(cd "$(dirname "$0")/.." && pwd)"
export XDG_CONFIG_HOME="$R/.xdg/config" XDG_CACHE_HOME="$R/.xdg/cache" XDG_DATA_HOME="$R/.xdg/data"
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME"
python "$R/scripts/build_manifest.py"
python "$R/scripts/build_assembly.py"
python "$R/scripts/build_schematic.py"
kicad-cli sch erc "$R/integrated.kicad_sch" -o "$R/validation/erc.rpt"
python "$R/scripts/verify_schematic.py" > "$R/validation/verify.log" 2>&1
kicad-cli sch export svg "$R/integrated.kicad_sch" -o "$R/exports/"
for S in "$R/exports/"*.svg; do inkscape "$S" --export-filename="${S%.svg}.png" --export-width=2200; done
# This script intentionally does not alter the integrated PCB or its project/footprint setup.

python "$R/scripts/hash_electrical_sources.py"
