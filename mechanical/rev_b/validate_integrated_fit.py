#!/usr/bin/python3
from carbentra_tools import FREECAD_LIB, FONT_REGULAR, PYTHON, kicad_resource
import os,sys,json
BASE=os.path.dirname(os.path.abspath(__file__));sys.path.extend([FREECAD_LIB,BASE])
import FreeCAD as App,Part,socket_b_features as m
V=App.Vector
D=App.openDocument(BASE+'/CARBENTRA-P16-B-base-provisional.FCStd')
parts=[o for o in D.Objects if hasattr(o,'PartKind')]
manifest=json.load(open(BASE+'/../../electronics/rev_b/integrated/exports/component_envelopes.json'))
allow={frozenset(['PEBus','Blade_PE']),frozenset(['PEBus','Contact_PE']),frozenset(['Contact_L','ThermalSleeve']),frozenset(['MainFuseCap1','MainFuseLead1']),frozenset(['MainFuseCap2','MainFuseLead2']),frozenset(['ThermalBody','ThermalLead1']),frozenset(['ThermalBody','ThermalLead2'])}
for n,(a,b) in m.links.CONNECTIONS.items():
 if not a.startswith('J'):allow.add(frozenset(['PowerCore_'+n,a]))
 if not b.startswith('J'):allow.add(frozenset(['PowerCore_'+n,b.replace('_lug','')]))
for a,b in [('RFServiceSlackEnvelope','RFCoax'),('RFAntenna','RFCoax'),('MainFuseCap1','MainFuseClip1'),('MainFuseCap2','MainFuseClip2'),('MainFuseClip1','MainFuseCollector1'),('MainFuseClip2','MainFuseCollector2'),('PowerCore_L_FUSE_THERMAL','MainFuseClip2')]:allow.add(frozenset([a,b]))
for i in range(4):
 allow.add(frozenset(['FrontLid','Screw_'+str(i)]));allow.add(frozenset(['RearShell','FuseRetainerScrew_'+str(i)]))
for i in range(2):allow.add(frozenset(['Carrier','ThermalRetainerScrew_'+str(i)]))
E=App.openDocument(BASE+'/../../electronics/rev_b/integrated/exports/placement_assembly.FCStd')
ints=[]
for i,a in enumerate(parts):
 for b in parts[i+1:]:
  if not a.Shape.BoundBox.intersect(b.Shape.BoundBox):continue
  vol=a.Shape.common(b.Shape).Volume
  if vol>1e-5:ints.append({'a':a.Name,'b':b.Name,'volume_mm3':vol,'intentional_interface':frozenset([a.Name,b.Name]) in allow})
expected={'J201':['PowerCore_L_PROTECTED','PowerCore_N_RAW'],'J102':['PowerCore_L_OUTPUT','PowerCore_N_OUTPUT'],'U101':['RFConnectorEnvelope'],'J403':['HeadConnectorEnvelope']}
component_hits=[]
for c in manifest['components']+manifest['leads']:
 if 'min_xyz_mm' not in c:continue
 x,y,z=c['min_xyz_mm'];w,h,dd=c['size_xyz_mm']
 if min(w,h,dd)<=0:continue
 eo=E.getObject(c['object']);sh=eo.Shape.copy();sh.translate(V(0,0,m.P['pcb']['bottom_z']))
 for o in parts:
  if not o.Shape.BoundBox.intersect(sh.BoundBox):continue
  v=sh.common(o.Shape).Volume
  if v>1e-5:component_hits.append({'ref':c['ref'],'object':c.get('object'),'role':c.get('role'),'part':o.Name,'volume_mm3':v,'intentional_terminal_entry':c.get('role')=='component' and o.Name in expected.get(c['ref'],[])})
head_shape=Part.Shape();head_shape.read(BASE+'/../../electronics/rev_b/integrated/exports/remote_head_assembled.step')
head_hits=[]
for i,sh in enumerate(head_shape.Solids):
 for o in parts:
  if sh.BoundBox.intersect(o.Shape.BoundBox):
   v=sh.common(o.Shape).Volume
   if v>1e-5:head_hits.append({'head_solid':i,'part':o.Name,'volume_mm3':v})
report={'status':'PROVISIONAL fit audit against exported nominal/max envelopes, explicit terminal/fuse lead volumes; not manufacturer detailed CAD or safety approval','head_intersections':head_hits,'geometry_objects':len(parts),'physical_mechanical_parts':sum(o.Name!='RFServiceSlackEnvelope' for o in parts),'mechanical_parts':len(parts),'mechanical_all_valid':all(o.Shape.isValid() for o in parts),'mechanical_all_single_solids':all(len(o.Shape.Solids)==1 for o in parts),'mechanical_intersections':ints,'component_and_lead_intersections':component_hits}
json.dump(report,open(BASE+'/integrated_fit_report.json','w'),indent=2)
print('MECHANICAL',*[r for r in ints if not r['intentional_interface']],sep='\n')
print('COMPONENTS',*[r for r in component_hits if not r['intentional_terminal_entry']],sep='\n')

print('HEAD',*head_hits,sep='\n')
