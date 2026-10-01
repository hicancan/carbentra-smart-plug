from carbentra_tools import FREECAD_LIB, FONT_REGULAR, PYTHON, kicad_resource
import sys,json,math
from pathlib import Path
sys.path.append(FREECAD_LIB)
import FreeCAD as A,Part
import pcbnew as p
R=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(R/'meter.kicad_pcb'));cs={c['ref']:c for c in json.loads((R/'circuit_manifest.json').read_text(encoding='utf-8'))}
doc=A.newDocument('CARBENTRA_Meter_Rev_B');objects=[];manifest=[]
def obj(name,shape):
 o=doc.addObject('Part::Feature','MeterB_'+name);o.Label=o.Name;o.Shape=shape;objects.append(o);return o
board=Part.makeBox(75,45,1.6,A.Vector(-37.5,-22.5,0))
for x in(-34.5,34.5):
 for y in(-19.5,19.5):board=board.cut(Part.makeCylinder(1.1,1.6,A.Vector(x,y,0)))
obj('Board_FR4',board)
for fp in b.GetFootprints():
 ref=fp.GetReference()
 if ref not in cs:continue
 c=cs[ref];x,y,a=c['pos'];w,h=c['body'];w,h=(h,w) if round(a)%180==90 else (w,h);x-=w/2;y-=h/2
 if ref in ('J1','J2'):
  bounds=[]
  for g in fp.GraphicalItems():
   if g.GetLayer()==p.F_Fab and isinstance(g,p.PCB_SHAPE):
    bb=g.GetBoundingBox();bounds.append([p.ToMM(bb.GetLeft()),p.ToMM(bb.GetTop()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())])
  x=min(v[0] for v in bounds);y=min(v[1] for v in bounds);w=max(v[2] for v in bounds)-x;h=max(v[3] for v in bounds)-y
 elif ref=='J3':x,y,w,h=68.73,9.73,2.54,20.32
 gx=x-37.5;gy=22.5-y-h;obj(ref,Part.makeBox(w,h,c['height'],A.Vector(gx,gy,1.6)))
 manifest.append({'ref':ref,'board_id':'MeterB','label':c['value'],'min_xyz_mm':[gx,gy,1.6],'size_xyz_mm':[w,h,c['height']],'representation':'candidate nominal package envelope, no detailed lead geometry','pcb_origin_mm':c['pos'][:2]})
for fp in b.GetFootprints():
 for i,pad in enumerate(fp.Pads()):
  if not pad.GetNumber():continue
  bb=pad.GetBoundingBox();x=p.ToMM(bb.GetLeft())-37.5;y=22.5-p.ToMM(bb.GetBottom());w=p.ToMM(bb.GetWidth());h=p.ToMM(bb.GetHeight());obj('Pad_'+fp.GetReference()+'_'+str(i),Part.makeBox(w,h,.07,A.Vector(x,y,1.6)))
for i,t in enumerate(b.GetTracks()):
 if isinstance(t,p.PCB_VIA):
  x=p.ToMM(t.GetPosition().x)-37.5;y=22.5-p.ToMM(t.GetPosition().y);r=p.ToMM(t.GetWidth(p.F_Cu))/2;hole=p.ToMM(t.GetDrillValue())/2
  obj('Via_'+str(i),Part.makeCylinder(r,.07,A.Vector(x,y,1.67)).cut(Part.makeCylinder(hole,.07,A.Vector(x,y,1.67))));continue
 aa=t.GetStart();zz=t.GetEnd();x=p.ToMM(aa.x)-37.5;y=22.5-p.ToMM(aa.y);dx=p.ToMM(zz.x-aa.x);dy=-p.ToMM(zz.y-aa.y);l=math.hypot(dx,dy);w=p.ToMM(t.GetWidth())
 if l<.001:continue
 z=1.67 if t.GetLayer()==p.F_Cu else -.07;sh=Part.makeBox(l,w,.07,A.Vector(x,y-w/2,z));sh.rotate(A.Vector(x,y,z),A.Vector(0,0,1),math.degrees(math.atan2(dy,dx)));obj('Copper_'+str(i),sh)
doc.recompute();doc.saveAs(str(R/'exports/meter_assembly.FCStd'));Part.export(objects,str(R/'exports/meter_assembly.step'))
with (R/'exports/meter_assembly.obj').open('w') as f:
 off=1
 for o in objects:
  vs,fs=o.Shape.tessellate(.1);f.write('o '+o.Name+'\n')
  for v in vs:f.write(f'v {v.x:.5f} {v.y:.5f} {v.z:.5f}\n')
  for tri in fs:f.write('f '+' '.join(str(k+off) for k in tri)+'\n')
  off+=len(vs)
(R/'exports/component_envelopes.json').write_text(json.dumps({'board_id':'MeterB','coordinate_system':'mm, standalone board center XY origin, bottom z0; PCBx mapsx-37.5, PCBy maps22.5-y','board_size_mm':[75,45,1.6],'mount_holes_mm':[[-34.5,-19.5,2.2],[-34.5,19.5,2.2],[34.5,-19.5,2.2],[34.5,19.5,2.2]],'underside_terminal_lead_projection_mm':3.4,'status':'REV B DEVELOPMENT; assembly location not yet allocated','components':manifest},indent=2), encoding='utf-8', newline='\n')
(R/'validation/geometry.json').write_text(json.dumps({'objects':len(objects),'valid':all(o.Shape.isValid() and o.Shape.Volume>0 for o in objects),'component_envelopes':len(manifest),'limitations':['Package envelopes only; lead and paste geometry not vendor detailed','Pads shown as conservative rectangular bounds','Native PCB drawing authoritative for copper zones; OBJ traces are inspection overlay']},indent=2), encoding='utf-8', newline='\n');print('Exported',len(objects),'objects;',len(manifest),'bodies')
