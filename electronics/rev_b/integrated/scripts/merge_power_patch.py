from pathlib import Path
import json,pcbnew as p
R=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(R/'integrated.kicad_pcb'));changes=json.loads((R/'validation/power_candidate_patch.json').read_text())['changes'];ls={'F.Cu':p.F_Cu,'B.Cu':p.B_Cu}
def vec(a):return p.VECTOR2I(*[p.FromMM(v)for v in a])
for c in changes:
 if c['action']=='width':
  found=[t for t in b.GetTracks()if not isinstance(t,p.PCB_VIA)and t.GetNetname()==c['net']and t.GetLayer()==ls[c['layer']]and t.GetStart()==vec(c['start'])and t.GetEnd()==vec(c['end'])];assert len(found)==1,(c,len(found));found[0].SetWidth(p.FromMM(c['new_width_mm']))
 elif c['action']=='add_track':
  t=p.PCB_TRACK(b);t.SetStart(vec(c['start']));t.SetEnd(vec(c['end']));t.SetWidth(p.FromMM(c['width_mm']));t.SetLayer(ls[c['layer']]);t.SetNetCode(b.FindNet(c['net']).GetNetCode());b.Add(t)
 else:
  v=p.PCB_VIA(b);v.SetPosition(vec(c['at']));v.SetWidth(p.F_Cu,p.FromMM(c['diameter_mm']));v.SetDrill(p.FromMM(c['drill_mm']));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(b.FindNet(c['net']).GetNetCode());b.Add(v)
for f in b.GetFootprints():
 if f.GetReference()=='PS101':
  f.SetFPID(p.LIB_ID('Integrated','IRM10_Controller_Candidate'));p.PCB_IO_KICAD_SEXPR().FootprintSave(str(R/'Integrated.pretty'),f)
p.SaveBoard(str(R/'integrated.kicad_pcb'),b)
