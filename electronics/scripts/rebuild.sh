#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export XDG_CONFIG_HOME="${CM_KICAD_CONFIG_HOME:-/tmp/carbonmirror-kicad/config}"
export XDG_CACHE_HOME="${CM_KICAD_CACHE_HOME:-/tmp/carbonmirror-kicad/cache}"
export XDG_DATA_HOME="${CM_KICAD_DATA_HOME:-/tmp/carbonmirror-kicad/data}"
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME" exports validation
/usr/bin/python3 scripts/build_electronics.py
/usr/bin/python3 scripts/rebuild_completed_lv.py carbonmirror.kicad_pcb carbonmirror.kicad_pcb
kicad-cli sch erc carbonmirror.kicad_sch -o validation/erc.rpt
kicad-cli pcb drc carbonmirror.kicad_pcb -o validation/drc.rpt
kicad-cli sch export netlist carbonmirror.kicad_sch -o exports/carbonmirror.net
/usr/bin/python3 scripts/verify_electronics.py
kicad-cli sch export pdf carbonmirror.kicad_sch -o exports/schematic.pdf
kicad-cli sch export svg carbonmirror.kicad_sch -o exports/schematic/
kicad-cli pcb export svg --layers F.Cu,F.Fab,Edge.Cuts,Dwgs.User --page-size-mode 2 --exclude-drawing-sheet --mode-single -o exports/pcb_top.svg carbonmirror.kicad_pcb
printf '\nRebuilt development source. Inspect the reports: 9 mains airwires remain; fabrication is on hold.\n'
