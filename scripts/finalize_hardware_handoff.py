#!/usr/bin/env python3
"""Bind actual current electrical reports after digital recertification; never release hardware."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'electronics/rev_b/integrated'

def read(name):
    return json.loads((BASE / name).read_text(encoding='utf-8'))

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

summary = read('validation/final_summary.json')
assert summary['board_sha256'] == sha(BASE / 'integrated.kicad_pcb')
assert summary['rules_sha256'] == sha(BASE / 'integrated.kicad_dru')
assert summary['native_DRC'] == {'violations': 0, 'unconnected': 0, 'footprint_errors': 0}
assert summary['ERC'] == {'messages': 0, 'errors': 0, 'warnings': 0}
assert len(summary['negative_controls']) == 3 and all(summary['negative_controls'].values())
for name, expected in summary['schematic_files_sha256'].items():
    assert sha(BASE / name) == expected, name
for name, expected in read('validation/electrical_source_hashes.json').items():
    assert sha(BASE / name) == expected, name
assert read('validation/rear_termination.json')['pass_nominal_margin']
assert read('validation/geometry.json')['board_sha256'] == sha(BASE / 'integrated.kicad_pcb')
rebuilt = json.loads((ROOT / 'release/hardware_geometry_rebuild.json').read_text(encoding='utf-8'))
assert rebuilt['passed']
for name, expected in rebuilt['input_sha256'].items():
    assert sha(ROOT / name) == expected, name
handoff = read('HANDOFF.json')
names = set(handoff['files']) | set(summary['schematic_files_sha256']) | {
    'integrated.kicad_dru', 'validation/electrical_source_hashes.json',
    'validation/final_source_graph.json', 'validation/rule_controls/result.json',
    'validation/rule_controls/projected_negative.json', 'scripts/finalize_validation.py',
    'scripts/test_native_rules.py', 'scripts/test_projected_isolation.py',
    'scripts/audit_isolation.py', 'scripts/audit_pcb_pins.py',
    'scripts/verify_schematic.py', 'scripts/export_geometry.py', 'scripts/plot_review.py',
}
names.update('validation/' + name for name in summary['authoritative_reports'])
handoff['files'] = {name: {'sha256': sha(BASE / name), 'bytes': (BASE / name).stat().st_size}
                    for name in sorted(names)}
handoff['status'] = 'DEVELOPMENT HOLD'
handoff['evidence'] = 'release/hardware_recertification.json'
(BASE / 'HANDOFF.json').write_text(json.dumps(handoff, indent=2) + '\n', encoding='utf-8', newline='\n')
print(f'Bound {len(names)} current electrical files; manufacturing and energization HOLD')
