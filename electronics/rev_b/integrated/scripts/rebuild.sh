#!/bin/bash
set -euo pipefail
R="$(cd "$(dirname "$0")/.." && pwd)"
export KICAD_CONFIG_HOME="${TMPDIR:-/tmp}/cm-kicad-rebuild" XDG_CONFIG_HOME="${TMPDIR:-/tmp}/cm-xdg-config" XDG_CACHE_HOME="${TMPDIR:-/tmp}/cm-xdg-cache" XDG_DATA_HOME="${TMPDIR:-/tmp}/cm-xdg-data"
mkdir -p "$KICAD_CONFIG_HOME" "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME"
bash "$R/scripts/rebuild_schematic.sh"
/usr/bin/python3 "$R/scripts/build_pcb.py"
/usr/bin/python3 "$R/../scripts/replay_routing.py" "$R/integrated.kicad_pcb"
/usr/bin/python3 "$R/scripts/patch_schematic_paths.py" --apply
/usr/bin/python3 "$R/scripts/test_native_rules.py"
/usr/bin/python3 "$R/scripts/test_projected_isolation.py"
/usr/bin/python3 "$R/scripts/finalize_validation.py"
kicad-cli sch export pdf "$R/integrated.kicad_sch" -o "$R/exports/schematic.pdf"
python "$R/scripts/plot_review.py"
if [[ "${1:-}" != "--no-geometry" ]]; then
 /usr/bin/python3 "$R/scripts/export_geometry.py" --bodies-only
 /usr/bin/python3 "$R/scripts/export_geometry.py"
fi
