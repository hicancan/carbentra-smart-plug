#!/bin/bash
set -euo pipefail
R="$(cd "$(dirname "$0")/.." && pwd)"
export XDG_CONFIG_HOME="$R/.xdg/config" XDG_CACHE_HOME="$R/.xdg/cache" XDG_DATA_HOME="$R/.xdg/data"
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME"
/usr/bin/python3 "$R/scripts/build_thermal.py"
/usr/bin/python3 "$R/scripts/build_boards.py"
/usr/bin/python3 "$R/scripts/routing_recipe.py" replay
kicad-cli sch erc "$R/thermal_interlock.kicad_sch" -o "$R/validation/erc.rpt"
kicad-cli pcb drc "$R/thermal_controller.kicad_pcb" -o "$R/validation/controller_drc.rpt"
kicad-cli pcb drc "$R/thermal_sensor.kicad_pcb" -o "$R/validation/sensor_drc.rpt"
/usr/bin/python3 "$R/scripts/verify_thermal.py" > "$R/validation/verify.log" 2>&1
kicad-cli sch export svg "$R/thermal_interlock.kicad_sch" -o "$R/exports/"
inkscape "$R/exports/thermal_interlock.svg" --export-filename="$R/exports/thermal_interlock.png" --export-width=2400
for B in thermal_controller thermal_sensor; do
 kicad-cli pcb export svg -l F.Cu,B.Cu,F.Fab,Edge.Cuts,Dwgs.User --mode-single --exclude-drawing-sheet --fit-page-to-board -o "$R/exports/$B.svg" "$R/$B.kicad_pcb"
 inkscape "$R/exports/$B.svg" --export-area-drawing --export-filename="$R/exports/$B.png" --export-width=1800
done
/usr/bin/python3 "$R/scripts/export_geometry.py" > "$R/validation/geometry_export.log" 2>&1
