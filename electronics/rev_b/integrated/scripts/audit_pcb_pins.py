#!/usr/bin/python3
"""Read-only comparison: actual PCB pad nets vs exported schematic, main-board subset."""
import json,re,hashlib,datetime
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def parse(s):
 stack=[]
 for t in re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',s):
  if t=='(':
   a=[]
   if stack:stack[-1].append(a)
   stack.append(a)
  elif t==')':root=stack.pop()
  else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
 return root
def cs(x,k):return [v for v in x if isinstance(v,list) and v[0]==k]
def ch(x,k):return next(iter(cs(x,k)),None)
def norm(n):return None if not n or n.startswith('unconnected-') else n.lstrip('/')
manifest=json.loads((R/'electrical_manifest.json').read_text());main={c['ref']:c for c in manifest['components'] if c['board_designation']=='integrated'}
sch={}
for net in cs(ch(parse((R/'exports/integrated.net').read_text()),'nets'),'net'):
 n=norm(ch(net,'name')[1])
 for node in cs(net,'node'):
  ref=ch(node,'ref')[1]
  if ref in main:sch[ref,ch(node,'pin')[1]]=n
raw=(R/'integrated.kicad_pcb').read_bytes();board=parse(raw.decode());pads={};refs=set();dupes=[];mechanical=[]
for fp in cs(board,'footprint'):
 ref=next(v[2] for v in cs(fp,'property') if v[1]=='Reference')
 assert ref not in refs,('duplicate footprint',ref)
 if ref not in main:
  assert ref in {'H1','H2','H3','H4'} and all(p[1]=='' and p[2]=='np_thru_hole' and ch(p,'net') is None for p in cs(fp,'pad')),ref
  mechanical.append(ref);continue
 refs.add(ref)
 for pad in cs(fp,'pad'):
  pn=pad[1]
  if not pn:continue
  nn=ch(pad,'net');n=norm(nn[2]) if nn else None
  if (ref,pn) in pads and pads[ref,pn]!=n:dupes.append([ref,pn,pads[ref,pn],n])
  pads[ref,pn]=n
wanted={(ref,pn):n for ref,c in main.items() for pn,n in c['pins'].items()}
scherrs=[{'ref':k[0],'pin':k[1],'manifest':v,'schematic':sch.get(k,'MISSING')} for k,v in wanted.items() if sch.get(k,'MISSING')!=v]
errs=[{'ref':k[0],'pin':k[1],'schematic':v,'PCB':pads.get(k,'MISSING')} for k,v in sch.items() if pads.get(k,'MISSING')!=v]
extra=[{'ref':k[0],'pin':k[1],'net':v} for k,v in pads.items() if k not in sch]
report={'status':'PASS' if not any([scherrs,errs,extra,dupes,refs-set(main),set(main)-refs]) else 'FAIL','board_sha256':hashlib.sha256(raw).hexdigest(),'scope':'101 integrated main-board parts only; remote head/offboard/harness excluded','main_footprints':len(refs),'mechanical_NPTH_footprints':sorted(mechanical),'numbered_pad_keys':len(pads),'schematic_pin_keys':len(sch),'manifest_vs_schematic_errors':scherrs,'schematic_vs_PCB_errors':errs,'extra_PCB_pads':extra,'duplicate_pad_net_disagreement':dupes,'unexpected_footprints':sorted(refs-set(main)),'missing_footprints':sorted(set(main)-refs),'routing_continuity':'Not tested by pin-assignment audit; use PCB DRC separately','board_mutation':False}
(R/'validation/pcb_pin_audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));assert report['status']=='PASS'
