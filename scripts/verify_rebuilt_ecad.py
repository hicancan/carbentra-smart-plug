"""Run native ERC/DRC and net/pad checks against the separate KiCad rebuild."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

parser=argparse.ArgumentParser()
parser.add_argument('--rebuilt-root',type=Path,required=True)
args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[1]
base=args.rebuilt_root/'electronics/rev_b/integrated'
for script in ['verify_schematic.py','audit_pcb_pins.py']:
    subprocess.run([sys.executable,str(base/'scripts'/script)],check=True)
report=base/'validation/rebuilt-drc.json'
subprocess.run(['kicad-cli','pcb','drc',str(base/'integrated.kicad_pcb'),'--format','json','-o',str(report)],check=True)
drc=json.loads(report.read_text(encoding='utf-8'))
counts={'violations':len(drc['violations']),'unconnected':len(drc['unconnected_items']),'footprint_errors':len(drc['schematic_parity'])}
assert not any(counts.values()),counts
schematic=json.loads((base/'validation/independent_schematic_checks.json').read_text(encoding='utf-8'))
pads=json.loads((base/'validation/pcb_pin_audit.json').read_text(encoding='utf-8'))
assert schematic['status']=='PASS' and pads['status']=='PASS'
comparison=json.loads((ROOT/'release/hardware_geometry_rebuild.json').read_text(encoding='utf-8'))
assert comparison['passed']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result={'status':'PASS','method':'Windows KiCad native rebuilt schematic ERC, numbered net/pad checks and DRC; separate retained/rebuilt physical signature comparison',
        'kicad_version':drc['kicad_version'],'native_DRC':counts,'ERC':{'messages':0,**schematic['ERC']},
        'main_numbered_pad_keys':pads['numbered_pad_keys'],
        'recipe_sha256':sha(base/'routing_recipe.json'),
        'rebuild_output_board_sha256':sha(base/'integrated.kicad_pcb'),
        'retained_board_sha256':sha(ROOT/'electronics/rev_b/integrated/integrated.kicad_pcb'),
        'physical_signature_comparison':comparison['pcb_rebuild_comparison'],
        'fabrication_release':'HOLD','energization_release':'HOLD'}
(ROOT/'electronics/rev_b/integrated/validation/rebuild_check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(result,indent=2))
