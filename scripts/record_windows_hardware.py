"""Bind checked Windows-native evidence while preserving physical release holds."""
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(name):
    return json.loads((ROOT/name).read_text(encoding='utf-8'))

def sha(name):
    return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()

prior = read('release/hardware_recertification.json')
rebuilt = read('release/hardware_geometry_rebuild.json')
assert rebuilt['passed'] and all(x['passed'] for x in rebuilt['assemblies'])
assert all(sha(name) == digest for name, digest in rebuilt['input_sha256'].items())
insulation = read('mechanical/rev_b/insulation_domain_report.json')
assert insulation['inputs_changed_during_run'] == []
assert insulation['incremental_scope'] == 'Full source/target distance audit'
assert insulation['nominal_geometric_screen']['met_nominally']
assert all(sha(name) == item['sha256'] for name, item in insulation['input_snapshot'].items())
summary = read('electronics/rev_b/integrated/validation/final_summary.json')
assert not any(summary['native_DRC'].values()) and not any(summary['ERC'].values())
assert all(summary['negative_controls'].values())
# Existing PDF visual QA remains applicable only to identical reviewed bytes.
pdfs = {name: digest for name, digest in prior['evidence_sha256'].items() if name.endswith('.pdf')}
assert len(pdfs) == 3 and all(sha(name) == digest for name, digest in pdfs.items())
names = set(prior['evidence_sha256']) | set(pdfs) | {
    'scripts/record_windows_hardware.py', 'scripts/cad_equivalence.py',
    'scripts/carbentra_pcb.py', 'scripts/carbentra_tools.py',
    'scripts/engineering.ps1', 'scripts/run_engineering.py',
    'release/windows-native-scene.json',
    'electronics/rev_b/integrated/validation/final_drc.json',
    'electronics/rev_b/integrated/validation/final_erc.json',
}
record = {
    'revision': 'CARBENTRA-P16-EVT-B',
    'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'Windows native digital validation; retained design, no physical qualification',
    'release_for_fabrication': False, 'release_for_energization': False,
    'native_tools': {'KiCad': read('electronics/rev_b/integrated/validation/final_drc.json')['kicad_version'],
                     'FreeCAD': '.'.join(rebuilt['tool_versions']['FreeCAD'][:3]),
                     'Blender': read('release/windows-native-scene.json')['blender']},
    'geometry_objects_compared': sum(x['object_count'] for x in rebuilt['assemblies']),
    'pcb_rebuild_comparison': rebuilt['pcb_rebuild_comparison'],
    'full_insulation_audit': True,
    'pdf_visual_review': {**prior['pdf_visual_review'],
                         'retained_review_basis': 'All three reviewed PDFs are byte-identical to prior reviewed delivery; no new visual inspection is claimed.'},
    'evidence_sha256': {name: sha(name) for name in sorted(names)},
}
(ROOT/'release/hardware_recertification.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8', newline='\n')
print('Bound current Windows hardware evidence; physical HOLD retained')
