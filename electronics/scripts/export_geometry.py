#!/usr/bin/python3
from carbentra_tools import FREECAD_LIB, FONT_REGULAR, PYTHON, kicad_resource
import sys,json
from pathlib import Path
sys.path.append(FREECAD_LIB)
import FreeCAD as A,Part,Mesh
import pcbnew as p
R=Path(__file__).resolve().parents[1]; b=p.LoadBoard(str(R/'carbentra.kicad_pcb')); cs={c['ref']:c for c in json.loads((R/'circuit_manifest.json').read_text(encoding='utf-8'))}
doc=A.newDocument('CARBENTRA_PCB_DEV_A'); objects=[];manifest=[]
def obj(name,shape,color):
 o=doc.addObject('Part::Feature',name);o.Label=name;o.Shape=shape;objects.append(o);return o
board=Part.makeBox(72,68,1.6,A.Vector(-36,-34,8))
for x in(-31,31):
 for y in(-29,29):board=board.cut(Part.makeCylinder(1.6,1.6,A.Vector(x,y,8)))
obj('PCB_FR4_72x68_DEVELOPMENT',board,(.02,.15,.12))
for fp in b.GetFootprints():
 ref=fp.GetReference()
 if ref not in cs:continue
 c=cs[ref];bounds=[]
 for g in fp.GraphicalItems():
  if g.GetLayer()==p.F_Fab and isinstance(g,p.PCB_SHAPE):
   bb=g.GetBoundingBox();bounds.append((p.ToMM(bb.GetX()),p.ToMM(bb.GetY()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())))
 if not bounds:continue
 x=min(a[0] for a in bounds);y=min(a[1] for a in bounds);w=max(a[2] for a in bounds)-x;h=max(a[3] for a in bounds)-y
 # exact major package bodies in nominal footprint frame
 if ref=='PS1':x,y,w,h=6.74,12.11,37,24
 z=9.6;gx=x-36;gy=34-y-h
 shape=Part.makeBox(w,h,c['height'],A.Vector(gx,gy,z));obj(ref+'_'+c['value'].replace(' ','_').replace('/','_'),shape,(.12,.13,.15))
 manifest.append({'ref':ref,'label':c['value'],'min_xyz_mm':[gx,gy,z],'size_xyz_mm':[w,h,c['height']],'representation':'simplified package body from footprint F.Fab and candidate height; not vendor detailed solid'})
# mesh actual footprint copper pad shapes with thin elevated metal surfaces
for fp in b.GetFootprints():
 for i,pad in enumerate(fp.Pads()):
  if pad.GetNumber()=='':continue
  ps=pad.GetPosition();sz=pad.GetSize();w=p.ToMM(sz.x);h=p.ToMM(sz.y);x=p.ToMM(ps.x)-36;y=34-p.ToMM(ps.y)
  if w>0 and h>0:obj('Pad_'+fp.GetReference()+'_'+str(i),Part.makeBox(w,h,.04,A.Vector(x-w/2,y-h/2,9.6)),(.7,.65,.4))
# Physical trace/via meshes reflect the final KiCad board. No unrouted airwire is drawn as copper.
import math
for idx,t in enumerate(b.GetTracks()):
 if isinstance(t,p.PCB_VIA):
  x=p.ToMM(t.GetPosition().x)-36;y=34-p.ToMM(t.GetPosition().y);radius=p.ToMM(t.GetWidth(p.F_Cu))/2
  if radius<=0:continue
  sh=Part.makeCylinder(radius,.035,A.Vector(x,y,9.64)).cut(Part.makeCylinder(p.ToMM(t.GetDrillValue())/2,.035,A.Vector(x,y,9.64)))
  obj('Via_'+str(idx),sh,(.7,.55,.24));continue
 a=t.GetStart();z=t.GetEnd();x=p.ToMM(a.x)-36;y=34-p.ToMM(a.y);dx=p.ToMM(z.x-a.x);dy=-p.ToMM(z.y-a.y);length=math.hypot(dx,dy);width=p.ToMM(t.GetWidth())
 if length<.001:continue
 height=9.64 if t.GetLayer()==p.F_Cu else 7.965
 sh=Part.makeBox(length,width,.035,A.Vector(x,y-width/2,height));sh.rotate(A.Vector(x,y,height),A.Vector(0,0,1),math.degrees(math.atan2(dy,dx)));obj('Copper_'+str(idx),sh,(.7,.55,.24))
doc.recompute();doc.saveAs(str(R/'exports/pcb_assembly.FCStd'));Part.export(objects,str(R/'exports/pcb_assembly.step'))
# OBJ triangulated B-rep meshes; keep names for visual materials
with (R/'exports/pcb_assembly.obj').open('w') as f:
 offset=1
 for o in objects:
  vertices,faces=o.Shape.tessellate(.1);f.write('o '+o.Name+'\n')
  for v in vertices:f.write(f'v {v.x:.5f} {v.y:.5f} {v.z:.5f}\n')
  for tri in faces:f.write('f '+' '.join(str(i+offset) for i in tri)+'\n')
  offset+=len(vertices)
(R/'exports/component_envelopes.json').write_text(json.dumps({'coordinate_system':'millimetres; common mechanics frame; PCB lower-left(-36,-34,8), top9.6; y positive up','status':'DEV-A / FABRICATION HOLD','components':manifest},indent=2), encoding='utf-8', newline='\n')
print('Exported',len(objects),'solids,',len(manifest),'package envelopes')
