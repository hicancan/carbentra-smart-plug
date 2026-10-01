#!/usr/bin/python3
"""Separate native PCB trial ONLY. Never saves integrated.kicad_pcb."""
from pathlib import Path
import json,hashlib,shutil,os,argparse
R=Path(__file__).resolve().parents[1]
for d in ['CONFIG','CACHE','DATA']:os.environ['XDG_'+d+'_HOME']=str(R/'.xdg'/d.lower())
import pcbnew as p
ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,default=R/'integrated.kicad_pcb');args=ap.parse_args();raw=args.source.read_bytes()
source_board=p.LoadBoard(str(args.source))
for v in source_board.GetTracks():
 if isinstance(v,p.PCB_VIA) and v.GetNetname()=='HOT_GND' and abs(p.ToMM(v.GetPosition().y)-59.65)<.001:
  raise RuntimeError('Source already contains the proposed input via row. Do not duplicate copper; use --source integrated_power_baseline.kicad_pcb to reproduce the preserved trial.')
for stem in ['integrated_power_baseline','integrated_power_candidate']:
 (R/(stem+'.kicad_pcb')).write_bytes(raw)
 for ext in ['.kicad_pro','.kicad_dru']:shutil.copyfile(R/('integrated'+ext),R/(stem+ext))
b=p.LoadBoard(str(R/'integrated_power_candidate.kicad_pcb'));changes=[]
def xy(v):return [round(p.ToMM(v.x),5),round(p.ToMM(v.y),5)]
def widen(t,w):
 changes.append({'action':'width','net':t.GetNetname(),'layer':b.GetLayerName(t.GetLayer()),'start':xy(t.GetStart()),'end':xy(t.GetEnd()),'old_width_mm':p.ToMM(t.GetWidth()),'new_width_mm':w});t.SetWidth(p.FromMM(w))
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):continue
 n=t.GetNetname();a,z=xy(t.GetStart()),xy(t.GetEnd());w=p.ToMM(t.GetWidth())
 if n=='HOT_N' and w==2.4:widen(t,4.8)
 if n=='HOT_GND' and t.GetLayer()==p.F_Cu and w==2.4 and sorted([a,z])==sorted([[28.5,62],[32.5,62]]):widen(t,4.8)
def track(n,a,z,w,layer):
 t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));t.SetEnd(p.VECTOR2I(p.FromMM(z[0]),p.FromMM(z[1])));t.SetWidth(p.FromMM(w));t.SetLayer(layer);t.SetNetCode(b.FindNet(n).GetNetCode());b.Add(t);changes.append({'action':'add_track','net':n,'layer':b.GetLayerName(layer),'start':a,'end':z,'width_mm':w})
track('HOT_LOAD',[49.2,47.5],[49.2,55],2.4,p.F_Cu)
track('HOT_SWITCHED',[44.16,47.5],[44.16,55],2.4,p.B_Cu)
for a,z in zip([[28.5,62],[32.5,62],[35,59.9]],[[32.5,62],[35,59.9],[39.15,59.9]]):track('HOT_GND',a,z,2.4,p.B_Cu)
for x in [36.8,37.5,38.2,38.9,39.6,40.3]:
 for y in [59.65]:
  v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));v.SetWidth(p.F_Cu,p.FromMM(.8));v.SetDrill(p.FromMM(.4));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(b.FindNet('HOT_GND').GetNetCode());b.Add(v);changes.append({'action':'add_via','net':'HOT_GND','at':[x,y],'diameter_mm':.8,'drill_mm':.4,'layers':['F.Cu','B.Cu']})
p.SaveBoard(str(R/'integrated_power_candidate.kicad_pcb'),b)
(R/'validation/power_candidate_patch.json').write_text(json.dumps({'source_master_sha256':hashlib.sha256(raw).hexdigest(),'scope':'Separate candidate only; no footprint moves and no removed existing paths','changes':changes},indent=2), encoding='utf-8', newline='\n');print('Candidate created, changes',len(changes))
