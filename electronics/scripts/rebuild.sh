#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export XDG_CONFIG_HOME="${CARBENTRA_KICAD_CONFIG_HOME:-/tmp/carbentra-kicad/config}"
export XDG_CACHE_HOME="${CARBENTRA_KICAD_CACHE_HOME:-/tmp/carbentra-kicad/cache}"
export XDG_DATA_HOME="${CARBENTRA_KICAD_DATA_HOME:-/tmp/carbentra-kicad/data}"
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME" exports validation
/usr/bin/python3 scripts/build_electronics.py
/usr/bin/python3 scripts/rebuild_completed_lv.py carbentra.kicad_pcb carbentra.kicad_pcb
kicad-cli sch erc carbentra.kicad_sch -o validation/erc.rpt
kicad-cli pcb drc carbentra.kicad_pcb -o validation/drc.rpt
kicad-cli sch export netlist carbentra.kicad_sch -o exports/carbentra.net
/usr/bin/python3 scripts/verify_electronics.py
kicad-cli sch export pdf carbentra.kicad_sch -o exports/schematic.pdf
kicad-cli sch export svg carbentra.kicad_sch -o exports/schematic/
kicad-cli pcb export svg --layers F.Cu,F.Fab,Edge.Cuts,Dwgs.User --page-size-mode 2 --exclude-drawing-sheet --mode-single -o exports/pcb_top.svg carbentra.kicad_pcb
printf '\nRebuilt development source. Inspect the reports: 9 mains airwires remain; fabrication is on hold.\n'
