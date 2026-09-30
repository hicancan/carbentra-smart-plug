#!/bin/bash
set -euo pipefail
R="$(cd "$(dirname "$0")/.." && pwd)"
export XDG_CONFIG_HOME="$R/.xdg/config" XDG_CACHE_HOME="$R/.xdg/cache" XDG_DATA_HOME="$R/.xdg/data"
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME"
/usr/bin/python3 "$R/scripts/build_feedback.py"
kicad-cli sch erc "$R/output_feedback.kicad_sch" -o "$R/validation/erc.rpt"
kicad-cli pcb drc "$R/output_feedback.kicad_pcb" -o "$R/validation/drc.rpt"
/usr/bin/python3 "$R/scripts/verify_feedback.py" > "$R/validation/verify.log" 2>&1
kicad-cli sch export svg "$R/output_feedback.kicad_sch" -o "$R/exports/"
inkscape "$R/exports/output_feedback.svg" --export-filename="$R/exports/output_feedback.png" --export-width=1800
kicad-cli pcb export svg -l F.Cu,B.Cu,F.Fab,Edge.Cuts,Dwgs.User --mode-single --exclude-drawing-sheet --fit-page-to-board -o "$R/exports/board_review.svg" "$R/output_feedback.kicad_pcb"
inkscape "$R/exports/board_review.svg" --export-area-drawing --export-filename="$R/exports/board_review.png" --export-width=1600
