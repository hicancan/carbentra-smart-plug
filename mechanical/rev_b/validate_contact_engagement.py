#!/usr/bin/python3
from carbentra_tools import FREECAD_LIB, FONT_REGULAR, PYTHON, kicad_resource
import os,sys,json
BASE=os.path.dirname(os.path.abspath(__file__));sys.path.extend([FREECAD_LIB,BASE])
import FreeCAD as A,Part,socket_b_features as m
D=A.openDocument(BASE+'/CARBENTRA-P16-B-base-provisional.FCStd');rows=[]
for thick in [1.8,1.95]:
 for p in m.S:
  n=p['name'];z=43.58 if n=='PE' else 46.65
  pin=m.slot(thick,8.1,z,65-z,p['x'],p['y'],p['angle'])
  free=m.shape('Contact_'+n,contact_gap=1.7);inserted=m.shape('Contact_'+n,contact_gap=thick)
  hits=[]
  for o in D.Objects:
   if not hasattr(o,'PartKind') or o.Name.startswith('Contact_'):continue
   if any(t in o.Name for t in ['Shutter','Pawl']):s=m.shape(o.Name,travel=12.5,left_pawl=.8,right_pawl=.8,contact_gap=thick)
   else:s=o.Shape
   if pin.BoundBox.intersect(s.BoundBox):
    vol=pin.common(s).Volume
    if vol>1e-5:hits.append({'part':o.Name,'volume_mm3':vol})
  rows.append({'pin':n,'blade_thickness_mm':thick,'free_gap_mm':1.7,'required_leaf_displacement_each_mm':(thick-1.7)/2,'unloaded_interference_is_intended_elastic_engagement_mm3':pin.common(free).Volume,'inserted_contact_intersection_mm3':pin.common(inserted).Volume,'rigid_or_other_part_intersections':hits,'inserted_shape_valid':inserted.isValid()})
rep={'scope':'Original dual formed-leaf geometric candidate. Inserted shape is a prescribed displacement, not FEA or measured force. Stamping bend radii, copper-alloy temper/plating, contact pressure, resistance, fatigue and temperature remain qualification gates.','states':rows,'geometric_engagement_pass':all(r['unloaded_interference_is_intended_elastic_engagement_mm3']>0 and r['inserted_contact_intersection_mm3']<1e-5 and not r['rigid_or_other_part_intersections'] and r['inserted_shape_valid'] for r in rows)}
json.dump(rep,open(BASE+'/contact_engagement_report.json','w'),indent=2);print(json.dumps(rep,indent=2))
for gap,tag in [(1.8,'nominal'),(1.95,'maximum_reference')]:
 E=A.newDocument('Contacts_'+tag);objs=[]
 for n in ['L','N','PE']:
  o=E.addObject('Part::Feature','Contact_'+n);s=m.shape('Contact_'+n,contact_gap=gap);o.Shape=s;o.Placement=s.Placement;objs.append(o)
 Part.export(objs,BASE+'/contacts_inserted_'+tag+'.step')
