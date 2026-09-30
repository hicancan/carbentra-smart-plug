#!/usr/bin/python3
"""Compare actual KiCad-exported schematic netlist with manifest and PCB pads."""
import json,sys
from pathlib import Path
import pcbnew as p
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'))
from sexpr_util import parse,ch
R=Path(__file__).resolve().parents[1];circuit=json.loads((R/'circuit_manifest.json').read_text());tree=parse((R/'exports/meter.net').read_text());nets=ch(tree,'nets');actual={}
for n in nets[1:]:
 if not isinstance(n,list):continue
 name=ch(n,'name')[1].strip('"');name=name.lstrip('/')
 for node in n:
  if isinstance(node,list) and node[0]=='node':actual[(ch(node,'ref')[1].strip('"'),ch(node,'pin')[1].strip('"'))]=name
b=p.LoadBoard(str(R/'meter.kicad_pcb'));fps={f.GetReference():f for f in b.GetFootprints()};errors=[];count=0
for c in circuit:
 pins={x['number'] for x in c['pins']};fp=fps[c['ref']];pads={pd.GetNumber() for pd in fp.Pads()}
 for pin,net in c['nets'].items():
  count+=1
  if pin not in pins:errors.append(f'{c["ref"]}.{pin}: no schematic pin')
  if pin not in pads:errors.append(f'{c["ref"]}.{pin}: no physical pad')
  if actual.get((c['ref'],pin))!=net:errors.append(f'{c["ref"]}.{pin}: schematic {actual.get((c["ref"],pin))} != {net}')
  for pd in fp.Pads():
   if pd.GetNumber()==pin and pd.GetNetname()!=net:errors.append(f'{c["ref"]}.{pin}: board net differs')
report={'status':'PASS' if not errors else 'FAIL','components':len(circuit),'assigned_pins_checked':count,'errors':errors,'limitations':['Compares digital connectivity; not physical continuity or powered test','Manufacturer pin review and layout safety remain independent requirements']}
(R/'validation/net_pin_consistency.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));sys.exit(bool(errors))
