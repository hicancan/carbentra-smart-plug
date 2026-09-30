#!/usr/bin/python3
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[1]
files=[R/'electrical_manifest.json',R/'electrical_bom.csv',R/'ELECTRICAL_SOURCE.md',R/'RAIL_BUDGET.md',R/'POWER_CURRENT_REVIEW.md',R/'sym-lib-table']+list(R.glob('integrated*.kicad_sch'))+list(R.glob('Integrated*.kicad_sym'))
files +=[R/'scripts'/f for f in ['build_manifest.py','build_assembly.py','build_schematic.py','verify_schematic.py','audit_pcb_pins.py','patch_schematic_paths.py','calculate_rail_budget.py','rebuild_schematic.sh','hash_electrical_sources.py','build_power_candidate.py','review_power_paths.py','audit_power_candidate_isolation.py','audit_power_patch_applied.py']]
(R/'validation/electrical_source_hashes.json').write_text(json.dumps({str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2))
