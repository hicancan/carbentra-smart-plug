#!/usr/bin/python3
"""Read-only application check: exact additive power geometry present once in live board."""
from pathlib import Path
import os,json,hashlib
R=Path(__file__).resolve().parents[1]
for d in ['CONFIG','CACHE','DATA']:os.environ['XDG_'+d+'_HOME']=str(R/'.xdg'/d.lower())
import pcbnew as p
raw=(R/'integrated.kicad_pcb').read_bytes();b=p.LoadBoard(str(R/'integrated.kicad_pcb'));changes=json.loads((R/'validation/power_candidate_patch.json').read_text(encoding='utf-8'))['changes'];tracks=list(b.GetTracks());xy=lambda x:[round(p.ToMM(x.x),5),round(p.ToMM(x.y),5)];results=[]
for c in changes:
 found=[]
 for t in tracks:
  if t.GetNetname()!=c['net']:continue
  if c['action']=='add_via':
   if isinstance(t,p.PCB_VIA) and xy(t.GetPosition())==c['at'] and abs(p.ToMM(t.GetWidth(p.F_Cu))-c['diameter_mm'])<1e-6 and abs(p.ToMM(t.GetDrillValue())-c['drill_mm'])<1e-6:found.append(t)
  elif not isinstance(t,p.PCB_VIA) and b.GetLayerName(t.GetLayer())==c['layer']:
   if sorted([xy(t.GetStart()),xy(t.GetEnd())])==sorted([c['start'],c['end']]) and abs(p.ToMM(t.GetWidth())-c.get('new_width_mm',c.get('width_mm')))<1e-6:found.append(t)
 results.append({'operation':c,'matching_objects':len(found)})
assert (R/'integrated.kicad_pcb').read_bytes()==raw,'Live PCB changed during audit; rerun after current save completes'
report={'status':'PASS' if all(v['matching_objects']==1 for v in results) else 'FAIL','expected_operations':len(results),'actual_master_sha256':hashlib.sha256(raw).hexdigest(),'operations':results,'master_modified':False}
(R/'validation/power_patch_application_audit.json').write_text(json.dumps(report,indent=2), encoding='utf-8', newline='\n');print(report['status'],len(results));assert report['status']=='PASS'
