#!/usr/bin/python3
import os,sys,json
B=os.path.dirname(os.path.abspath(__file__));sys.path.extend(['/usr/lib/freecad-python3/lib',B])
import FreeCAD as App,Part,socket_b_features as m
V=App.Vector
d=App.openDocument(B+'/CARBENTRA-P16-B-base-provisional.FCStd')
a=[o for o in d.Objects if hasattr(o,'PartKind')]
pcb=m.rr(100,85,10,11,1.6)
for x,y in m.F:pcb=pcb.cut(Part.makeCylinder(1.6,2,V(x,y,10.9)))
for n in m.P['pcb']['edge_notches_provisional']:
 x1,y1,x2,y2=n['bounds_xy'];pcb=pcb.cut(m.box(x2-x1+.2,y2-y1,2,x1-.1,y1,10.9))
allowed={frozenset(['PEBus','Blade_PE']),frozenset(['PEBus','Contact_PE'])}
ints=[]
for i,x in enumerate(a):
 for y in a[i+1:]:
  v=x.Shape.common(y.Shape).Volume
  if v>1e-5:ints.append({'a':x.Name,'b':y.Name,'volume':v,'intentional':frozenset([x.Name,y.Name]) in allowed})
pints=[]
for o in a:
 v=o.Shape.common(pcb).Volume
 if v>1e-5:pints.append({'part':o.Name,'volume':v})
kin={}
for travel in [0,12]:
 ss=m.shape('ShutterSlider',108,93,65,travel);others=[o for o in a if o.Name!='ShutterSlider'];hits=[]
 for o in others:
  v=ss.common(o.Shape).Volume
  if v>1e-5:hits.append({'part':o.Name,'volume':v})
 passage=[]
 for p in m.S:
  keep=m.slot(2,6.8,45.5,20,p['x'],p['y'],p['angle']);v=ss.common(keep).Volume
  passage.append({'pin':p['name'],'blocked_volume':v})
 kin[str(travel)]={'solid_interferences':hits,'insertion_paths':passage}
r={'status':'Base study only; electronics/components/wires not yet present','intersections':ints,'pcb_intersections':pints,'shutter_travel_study':kin}
json.dump(r,open(B+'/base_fit_report.json','w'),indent=2);print(json.dumps(r,indent=2))
