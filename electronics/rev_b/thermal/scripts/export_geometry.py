#!/usr/bin/python3
from carbentra_tools import FREECAD_LIB, FONT_REGULAR, PYTHON, kicad_resource
"""Simplified PCB/package envelopes for integration; not vendor detailed solids."""
import json,sys,math
from pathlib import Path
import pcbnew as p
sys.path.append(FREECAD_LIB)
import FreeCAD as A,Part
R=Path(__file__).resolve().parents[1];cases=[(R,'thermal_controller',45,35),(R,'thermal_sensor',12,12),(R.parent/'feedback','output_feedback',35,25)]
for folder,stem,W,H in cases:
 mf=json.loads((folder/'pin_net_manifest.json').read_text(encoding='utf-8'));components={c['ref']:c for c in mf['components']};b=p.LoadBoard(str(folder/(stem+'.kicad_pcb')));doc=A.newDocument(stem);objects=[];data=[]
 def add(name,shape):
  o=doc.addObject('Part::Feature',name);o.Label=name;o.Shape=shape;objects.append(o);return o
 shape=Part.makeBox(W,H,1.6,A.Vector(0,0,0))
 for fp in b.GetFootprints():
  for pad in fp.Pads():
   if pad.GetAttribute() in (p.PAD_ATTRIB_PTH,p.PAD_ATTRIB_NPTH):
    xy=pad.GetPosition();dr=pad.GetDrillSize();radius=p.ToMM(dr.x)/2
    if radius>0:shape=shape.cut(Part.makeCylinder(radius,1.6,A.Vector(p.ToMM(xy.x),H-p.ToMM(xy.y),0)))
 if stem=='output_feedback':shape=shape.cut(Part.makeBox(1,21,1.6,A.Vector(24.1,2,0)))
 add(stem+'_FR4',shape)
 if stem=='thermal_sensor':add('GND_HEAD_thermal_island_B_Cu',Part.makeBox(3.3,2.6,.035,A.Vector(1.2,H-6.9,-.035)))
 for fp in b.GetFootprints():
  ref=fp.GetReference();c=components[ref];bounds=[]
  for g in fp.GraphicalItems():
   if g.GetLayer()==p.F_Fab and isinstance(g,p.PCB_SHAPE):
    bb=g.GetBoundingBox();bounds.append((p.ToMM(bb.GetLeft()),p.ToMM(bb.GetTop()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())))
  if bounds and c['height_mm']>0:
   x=min(v[0] for v in bounds);y=min(v[1] for v in bounds);w=max(v[2] for v in bounds)-x;h=max(v[3] for v in bounds)-y
   add(ref+'_'+c['mpn'].split('/')[0].replace(' ','_').replace(',','_'),Part.makeBox(w,h,c['height_mm'],A.Vector(x,H-y-h,1.6)))
   data.append({'ref':ref,'mpn':c['mpn'],'min_xyz_mm':[x,H-y-h,1.6],'size_xyz_mm':[w,h,c['height_mm']],'representation':'F.Fab-based envelope + declared component height, not detailed manufacturer solid'})
  for idx,pad in enumerate(fp.Pads()):
   xy=pad.GetPosition();sz=pad.GetSize();w=p.ToMM(sz.x);h=p.ToMM(sz.y)
   if w and h:add('Pad_'+ref+'_'+str(idx),Part.makeBox(w,h,.035,A.Vector(p.ToMM(xy.x)-w/2,H-p.ToMM(xy.y)-h/2,1.6)))
 # Trace geometry intentionally omitted: routing is in KiCad, not represented by fake lines.
 doc.recompute();Part.export(objects,str(folder/'exports'/(stem+'_envelope.step')));doc.saveAs(str(folder/'exports'/(stem+'_envelope.FCStd')))
 out={'status':'DEVELOPMENT / HOLD','coordinate_system':'Local mm, board lower-left=(0,0,0), top copper z=1.6, +y upward (mirrored KiCad y)','board_mm':[W,H,1.6],'height_reservation_above_PCB_mm':2 if stem=='thermal_sensor' else 9,'height_reservation_below_PCB_mm':.1 if stem=='thermal_sensor' else 3,'mating_harness_actuator_and_insulation_not_included':True,'components':data}
 (folder/'exports'/(stem+'_envelopes.json')).write_text(json.dumps(out,indent=2), encoding='utf-8', newline='\n');A.closeDocument(doc.Name);print(stem,len(data),'component envelopes')
