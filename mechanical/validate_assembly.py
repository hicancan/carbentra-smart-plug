#!/usr/bin/python3
import sys,os,json
BASE=os.path.dirname(os.path.abspath(__file__))
sys.path.extend(['/usr/lib/freecad-python3/lib',BASE])
import FreeCAD as App,Part,socket_features
V=App.Vector
d=App.openDocument(BASE+'/CARBENTRA-P16-EVT-A.FCStd');d.recompute()
parts=[o for o in d.Objects if hasattr(o,'PartKind')]
# Native file regenerates; spreadsheet propagates 88->90->88 envelope edit.
d.Parameters.set('B1','90 mm');d.recompute()
edit_ok=abs(d.RearShell.Shape.BoundBox.XLength-90)<1e-6 and d.RearShell.Shape.isValid() and len(d.RearShell.Shape.Solids)==1
d.Parameters.set('B1','88 mm');d.recompute()
# Verify intentional PE union is one connected solid.
pe=d.Blade_PE.Shape.fuse(d.PEBus.Shape).fuse(d.Contact_PE.Shape).removeSplitter()
report={'fcstd_reload_valid':all(o.Shape.isValid() for o in parts),'native_parameter_edit_88_90_88':edit_ok,'pe_union_solid_count':len(pe.Solids),'pe_union_valid':pe.isValid(),'pcb_body_interferences':[],'component_envelope_interferences':[]}
pcb=Part.makeBox(72,68,1.6,V(-36,-34,8))
for x,y in socket_features.P['pcb']['mount_centers']:pcb=pcb.cut(Part.makeCylinder(1.6,2,V(x,y,7.9)))
for o in parts:
 v=pcb.common(o.Shape).Volume
 if v>1e-5:report['pcb_body_interferences'].append({'part':o.Name,'volume_mm3':v})
f=os.path.join(BASE,'../electronics/exports/component_envelopes.json')
if os.path.exists(f):
 env=json.load(open(f));report['component_envelope_count']=len(env['components'])
 for c in env['components']:
  x,y,z=c['min_xyz_mm'];w,h,dep=c['size_xyz_mm'];s=Part.makeBox(w,h,dep,V(x,y,z))
  for o in parts:
   v=s.common(o.Shape).Volume
   if v>1e-5:
    expected=(c['ref']=='J1' and o.Name in ['WireCore_L_IN_POST','WireCore_N_IN']) or (c['ref']=='J2' and o.Name in ['WireCore_L_OUT','WireCore_N_OUT']) or (c['ref']=='J5' and o.Name in ['WireCore_AUX_L_OUT','WireCore_AUX_N'])
    report['component_envelope_interferences'].append({'component':c['ref'],'part':o.Name,'volume_mm3':v,'intentional_terminal_entry':expected})
else:report['component_envelope_count']=0
report['insertion_keepout_interferences']=[]
for pin in socket_features.S:
 keep=socket_features.slot(2.0,6.8,35.5,20,pin['x'],pin['y'],pin['angle'])
 for o in parts:
  v=keep.common(o.Shape).Volume
  if v>1e-5:report['insertion_keepout_interferences'].append({'opening':pin['name'],'part':o.Name,'volume_mm3':v,'intentional_closed_shutter':o.Name=='ShutterSlider'})
report['scope']='BRep, provisional insertion keepouts and envelope fit only. No electrical, tooling or physical verification.'
json.dump(report,open(BASE+'/integration_validation.json','w'),indent=2);print(json.dumps(report,indent=2))
