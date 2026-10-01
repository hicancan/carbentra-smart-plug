#!/usr/bin/env python3
"""Read-only current Rev B evidence check. A pass never releases physical hardware."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]


def verify_hashes(root, entries):
    """Return exact mismatches, refusing paths outside the checkout."""
    failures = []
    root = root.resolve()
    for name, metadata in entries.items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            failures.append(name)
            continue
        if not isinstance(metadata, (str, dict)):
            failures.append(name)
            continue
        expected = metadata if isinstance(metadata, str) else metadata.get('sha256')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            failures.append(name)
        elif isinstance(metadata, dict) and 'bytes' in metadata and path.stat().st_size != metadata['bytes']:
            failures.append(name)
    return failures


def validate(root=ROOT):
    checks = []
    def check(name, passed, detail=None):
        checks.append({'check': name, 'passed': bool(passed), 'detail': detail})
    def read(name):
        try:
            return json.loads((root / name).read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            check('read ' + name, False, str(exc))
            return {}
    def pinned(name, entries, minimum=1):
        failures = verify_hashes(root, entries)
        check(name, len(entries) >= minimum and not failures, failures)
    mechanical = read('mechanical/rev_b/freeze_manifest.json')
    rows = mechanical.get('files', [])
    check('nonempty unique mechanical freeze', len(rows) >= 193 and len({r['path'] for r in rows}) == len(rows))
    pinned('current mechanical freeze', {r['path']: r for r in rows}, 193)
    check('mechanical bounded digital pass', mechanical.get('all_defined_digital_checks_pass') is True)
    electrical = read('electronics/rev_b/integrated/HANDOFF.json')
    prefix = 'electronics/rev_b/integrated/'
    pinned('current electrical handoff', {prefix + p: m for p, m in electrical.get('files', {}).items()}, 25)
    check('electrical development hold retained', electrical.get('status') == 'DEVELOPMENT HOLD')
    summary = read(prefix + 'validation/final_summary.json')
    pinned('current native PCB and rule checks', {
        prefix + 'integrated.kicad_pcb': summary.get('board_sha256'),
        prefix + 'integrated.kicad_dru': summary.get('rules_sha256'),
    })
    pinned('all current schematic sheets', {prefix + p: m for p, m in summary.get('schematic_files_sha256', {}).items()}, 6)
    check('native DRC and ERC zero', summary.get('native_DRC') == {'violations': 0, 'unconnected': 0, 'footprint_errors': 0}
          and summary.get('ERC') == {'messages': 0, 'errors': 0, 'warnings': 0})
    controls = summary.get('negative_controls', {})
    check('native and independent negative controls', len(controls) == 3 and all(v is True for v in controls.values()))
    insulation = read('mechanical/rev_b/insulation_domain_report.json')
    pinned('full insulation audit current inputs', insulation.get('input_snapshot', {}), 9)
    check('full insulation audit rather than reused incremental result', insulation.get('incremental_scope') == 'Full source/target distance audit'
          and insulation.get('inputs_changed_during_run') == []
          and insulation.get('nominal_geometric_screen', {}).get('met_nominally') is True)
    drawing = read('mechanical/rev_b/docs/drawing_source_snapshot.json')
    pinned('drawing generated from current sources', {'mechanical/rev_b/' + p: m for p, m in drawing.get('source_files', {}).items()}, 3)
    rebuilt = read('release/hardware_geometry_rebuild.json')
    pinned('fresh geometry rebuild current inputs', rebuilt.get('input_sha256', {}), 15)
    check('fresh geometry equals retained design', rebuilt.get('passed') is True
          and len(rebuilt.get('assemblies', [])) == 4
          and all(a.get('passed') is True for a in rebuilt.get('assemblies', [])))
    recertification = read('release/hardware_recertification.json')
    pinned('recertification current evidence', recertification.get('evidence_sha256', {}), 15)
    check('physical holds retained', recertification.get('release_for_fabrication') is False
          and recertification.get('release_for_energization') is False)
    check('three retained reviewed PDFs unchanged', recertification.get('pdf_visual_review', {}).get('passed') is True
          and recertification.get('pdf_visual_review', {}).get('pages') == 11)
    return {'scope': 'Digital consistency only, not physical qualification',
            'passed': all(c['passed'] for c in checks), 'checks': checks}


if __name__ == '__main__':
    result = validate()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result['passed'] else 1)
