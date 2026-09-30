"""Independent nominal 3D check of rear primary terminations against all isolated PCB copper.
No surface-creepage, solid-insulation or tolerance qualification is implied.
"""
import sys,json,math,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];ROOT=R.parents[2];M=ROOT/'mechanical/rev_b'
sys.path.extend(['/usr/lib/freecad/lib',str(M)])
import FreeCAD as A,Part,pcbnew as p,power_links
V=A.Vector;b=p.LoadBoard(str(R/'integrated.kicad_pcb'));doc=A.openDocument(str(M/'CARBENTRA-P16-B-base-provisional.FCStd'))
sources=[]
for n in ['Blade_L','Blade_N']:sources.append((n,doc.getObject(n).Shape.copy()))
for n in ['L_RAW','N_RAW']:
 path=power_links.ROUTES[n];length=sum(e.Length for e in path.edges);trim=power_links.TRIMS[n][0];sources.append((n+'_bare_start',path.pipe(1,0,length-trim)))
def world(q,z):return V(p.ToMM(q.x)-50,42.5-p.ToMM(q.y),z)
def lower(a,c):
 a=a.BoundBox;c=c.BoundBox
 return math.sqrt(sum(max(0,getattr(a,k+'Min')-getattr(c,k+'Max'),getattr(c,k+'Min')-getattr(a,k+'Max'))**2 for k in 'XYZ'))
targets=[]
def add(name,s):
 if min(lower(a,s)for _,a in sources)<9:targets.append((name,s))
levels=[(p.F_Cu,13.1,.07),(p.In1_Cu,12.815,.035),(p.In2_Cu,11.75,.035),(p.B_Cu,11.43,.07)]
for f in b.GetFootprints():
 for pd in f.Pads():
  if not pd.GetNetname()or pd.GetNetname().startswith('HOT_')or pd.GetAttribute()==p.PAD_ATTRIB_NPTH:continue
  for layer,z,th in levels:
   if not pd.IsOnLayer(layer):continue
   poly=pd.GetEffectivePolygon(layer)
   for k in range(poly.OutlineCount()):
    c=poly.COutline(k);pts=[world(c.CPoint(j),z)for j in range(c.PointCount())]
    if len(pts)>2:add(f'{f.GetReference()}.{pd.GetNumber()}:{b.GetLayerName(layer)}',Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,th)))
for i,t in enumerate(b.GetTracks()):
 if t.GetNetname().startswith('HOT_'):continue
 name=f'{t.GetNetname()}:copper{i}'
 if isinstance(t,p.PCB_VIA):add(name,Part.makeCylinder(p.ToMM(t.GetWidth(p.F_Cu))/2,1.74,world(t.GetPosition(),11.43)));continue
 layer,z,th=next(a for a in levels if a[0]==t.GetLayer());a=world(t.GetStart(),z);e=world(t.GetEnd(),z);v=e-a;L=v.Length;r=p.ToMM(t.GetWidth())/2
 if L<1e-6:continue
 n=V(-v.y/L*r,v.x/L*r,0);pts=[a+n,e+n,e-n,a-n];sh=Part.Compound([Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,th)),Part.makeCylinder(r,th,a),Part.makeCylinder(r,th,e)]);add(name,sh)
# Conservative entire zone outline, including areas removed by native clearance cuts.
for zi,q in enumerate(b.Zones()):
 if q.GetIsRuleArea()or q.GetNetname().startswith('HOT_'):continue
 layer,z,th=next(a for a in levels if a[0]==q.GetLayer());o=q.Outline()
 for k in range(o.OutlineCount()):
  c=o.COutline(k);pts=[world(c.CPoint(j),z)for j in range(c.PointCount())];add(f'ZONE:{q.GetNetname()}:{zi}',Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,th)))
mins=[];bad=[]
for name,s in sources:
 best=(1e9,None,None)
 for key,t in sorted(targets,key=lambda a:lower(s,a[1])):
  if lower(s,t)>max(best[0],8.4):continue
  d,pts,_=s.distToShape(t)
  if d<best[0]:best=(d,key,[[list(a),list(c)]for a,c in pts[:1]])
  if d<8.4:bad.append({'source':name,'target':key,'mm':d})
 mins.append({'source':name,'minimum_mm':best[0],'target':best[1],'closest_points_mm':best[2]})
files=[R/'integrated.kicad_pcb',M/'CARBENTRA-P16-B-base-provisional.FCStd',M/'power_links.py']
report={'status':'nominal engineering geometry only; fabrication and insulation qualification remain held','inputs':{str(a.relative_to(ROOT)):hashlib.sha256(a.read_bytes()).hexdigest()for a in files},'pcb_bottom_z_mm':11.5,'target_mm':8.4,'minimums':mins,'pairs_below_8p4_mm':bad,'pass_nominal_margin':not bad,'limitations':['Nominal direct 3D distance, not creepage or qualified free-air clearance.','Rear blades and bare input-link starts only; complete assembly audit is separate.','Conservative whole zone-outline fill and solid full via-land column.','No fabrication/assembly tolerance, thermal motion or material qualification.']}
(R/'validation/rear_termination.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
