#!/usr/bin/python3
"""Record/replay DRC-checked routing; does not rerun nondeterministic search during a rebuild."""
import json,re,sys
from pathlib import Path
import pcbnew as p
R=Path(__file__).resolve().parents[1];target=R/'thermal_controller.kicad_pcb';recipe=R/'scripts/controller_route_recipe.json'
def parse(s):
 st=[]
 for t in re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',s):
  if t=='(':
   a=[]
   if st:st[-1].append(a)
   st.append(a)
  elif t==')':root=st.pop()
  else:st[-1].append(t)
 return root
def ser(x):return '('+' '.join(map(ser,x))+')' if isinstance(x,list) else x
def xy(v):return [p.ToMM(v.x),p.ToMM(v.y)]
def vec(v):return p.VECTOR2I(p.FromMM(v[0]),p.FromMM(v[1]))
if sys.argv[1]=='record':
 assert '** Found 0 DRC violations **' in (R/'validation/controller_drc.rpt').read_text(encoding='utf-8')
 b=p.LoadBoard(str(target));items=[]
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):items.append({'type':'via','net':t.GetNetname(),'at':xy(t.GetPosition()),'diameter':p.ToMM(t.GetWidth(p.F_Cu)),'drill':p.ToMM(t.GetDrillValue())})
  else:items.append({'type':'segment','net':t.GetNetname(),'a':xy(t.GetStart()),'b':xy(t.GetEnd()),'width':p.ToMM(t.GetWidth()),'layer':int(t.GetLayer())})
 recipe.write_text(json.dumps({'status':'DRC-checked routing source; rerun DRC after replay','items':items},indent=2), encoding='utf-8', newline='\n');print('Recorded',len(items),'routing objects')
else:
 tree=parse(target.read_text(encoding='utf-8'));tree[:]=[n for n in tree if not(isinstance(n,list) and n[0] in ['segment','via'])];target.write_text(ser(tree), encoding='utf-8', newline='\n');b=p.LoadBoard(str(target))
 for d in json.loads(recipe.read_text(encoding='utf-8'))['items']:
  if d['type']=='via':
   t=p.PCB_VIA(b);t.SetPosition(vec(d['at']));t.SetWidth(p.F_Cu,p.FromMM(d['diameter']));t.SetWidth(p.B_Cu,p.FromMM(d['diameter']));t.SetDrill(p.FromMM(d['drill']));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu)
  else:
   t=p.PCB_TRACK(b);t.SetStart(vec(d['a']));t.SetEnd(vec(d['b']));t.SetWidth(p.FromMM(d['width']));t.SetLayer(d['layer'])
  t.SetNet(b.FindNet(d['net']));b.Add(t)
 p.SaveBoard(str(target),b);print('Replayed verified controller routing')
