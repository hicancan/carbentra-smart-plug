#!/usr/bin/python3
from carbentra_tools import FREECAD_LIB, FONT_REGULAR, PYTHON, kicad_resource
"""Reproducible engineering-development export; no fabrication-release implication."""
import os,sys,json,hashlib
BASE=os.path.dirname(os.path.abspath(__file__));sys.path.extend([FREECAD_LIB,BASE])
import FreeCAD as A,Part,MeshPart,socket_b_features as m
D=A.openDocument(BASE+'/CARBENTRA-P16-B-base-provisional.FCStd');objs=[o for o in D.Objects if hasattr(o,'PartKind')]
for sub in ['meshes','parts']:os.makedirs(BASE+'/'+sub,exist_ok=True)
def bbox(s):b=s.BoundBox;return [b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax]
def meshbox(s):
 vv=s.tessellate(.005)[0];return [min(getattr(v,k) for v in vv) for k in ['x','y','z']]+[max(getattr(v,k) for v in vv) for k in ['x','y','z']]
def style(n):
 color=[.84,.86,.85];mat='PC-FR insulating resin candidate';group='contact_carrier';explode=[0,0,25]
 if n in ['RearShell','RearFinish','Blade_L','Blade_N','Blade_PE','BladeSleeve_L','BladeSleeve_N','AuxFuseCradle','AuxFuseRetainer']:group='rear';explode=[0,0,-22]
 if n in ['FrontLid','SeamRing','LocalButton','RearmButton','StatusLightGuide']:group='front';explode=[0,0,65];color=[.94,.96,.95]
 if n=='RearFinish':color=[.035,.045,.045]
 if any(t in n for t in ['Blade_','Contact_','PowerCore','PEBus','Collector','Clip','Cap','ThermalLead']):mat='Conductive metal candidate';color=[.64,.37,.18]
 if 'Spring' in n or 'Screw' in n:mat='Spring/fastener metal candidate';color=[.42,.46,.48]
 if n.startswith('Power'):group='supported_power_links';explode=[0,0,15]
 if n.startswith('PowerCarrier'):color=[.26,.10,.045] if '_L_' in n or '_L_RAW' in n or '_L_OUTPUT' in n or '_L_PROTECTED' in n or '_L_FUSE' in n else [.025,.18,.42]
 if n.startswith('MainFuse') or n.startswith('FuseRetainer'):group='main_fuse';explode=[-18,0,25]
 if n.startswith('Thermal') or n.startswith('Head'):group='thermal';explode=[18,0,25]
 if any(t in n for t in ['Shutter','Pawl']):group='shutter';explode=[0,0,43]
 if n.startswith('RF'):group='rf';explode=[0,10,15];color=[.06,.065,.07]
 if n=='StatusLightGuide':mat='Optical PC candidate';color=[.10,.72,.50]
 return color,mat,group,explode
manifest={'brand':'CARBENTRA','revision':'CARBENTRA-P16-EVT-B','status':'Engineering development geometry; qualification and certification pending','units':'mm','front_axis':'+Z','origin':'rear housing center','parts':[]}
for o in objs:
 n=o.Name;s=o.Shape;color,mat,group,exp=style(n)
 mesh=MeshPart.meshFromShape(Shape=s,LinearDeflection=.003 if 'Spring' in n else .005,AngularDeflection=.08,Relative=False);mesh.write(BASE+'/meshes/'+n+'.stl')
 Part.export([o],BASE+'/parts/'+n+'.step')
 manifest['parts'].append({'id':n,'name':n,'geometry_role':'clearance_envelope' if n=='RFServiceSlackEnvelope' else 'physical_part','render_default':n!='RFServiceSlackEnvelope','file':'meshes/'+n+'.stl','material':mat,'color':color,'group':group,'explode':exp,'volume_mm3':s.Volume,'solids':len(s.Solids),'bbox_mm':meshbox(s),'brep_bbox_mm':bbox(s),'valid':s.isValid()})
D.saveAs(BASE+'/CARBENTRA-P16-EVT-B.FCStd');Part.export([o for o in objs if o.Name!='RFServiceSlackEnvelope'],BASE+'/CARBENTRA-P16-EVT-B_mechanical.step')
from artifacts_metadata import decorate
manifest=decorate(manifest)
json.dump(manifest,open(BASE+'/parts_manifest.json','w'),indent=2)
json.dump(m.links.manifest(),open(BASE+'/power_link_manifest.json','w'),indent=2)
E=A.openDocument(BASE+'/../../electronics/rev_b/integrated/exports/placement_assembly.FCStd')
C=A.newDocument('CARBENTRA_P16_EVT_B_System');bounds={'units':'mm','main_translation_mm':[0,0,11.5],'mechanical':{},'MainB':{},'HeadB':{}}
for o in objs:
 q=C.addObject('Part::Feature','Mech_'+o.Name);q.Label=o.Label;q.Shape=o.Shape;bounds['mechanical'][o.Name]=meshbox(q.Shape)
for o in E.Objects:
 if not hasattr(o,'Shape') or o.Shape.isNull():continue
 sh=o.Shape.copy();sh.translate(A.Vector(0,0,11.5));q=C.addObject('Part::Feature',o.Name);q.Shape=sh;q.Placement=sh.Placement;bounds['MainB'][o.Name]=meshbox(q.Shape)
hs=Part.Shape();hs.read(BASE+'/../../electronics/rev_b/integrated/exports/remote_head_assembled.step')
for i,sh in enumerate(hs.Solids):
 n='HeadB_'+str(i);q=C.addObject('Part::Feature',n);q.Shape=sh;q.Placement=sh.Placement;bounds['HeadB'][n]=meshbox(q.Shape)
C.recompute();C.saveAs(BASE+'/CARBENTRA-P16-EVT-B_system_assembly.FCStd');Part.export([o for o in C.Objects if hasattr(o,'Shape') and o.Name!='Mech_RFServiceSlackEnvelope'],BASE+'/CARBENTRA-P16-EVT-B_system_assembly.step')
for group in ['MainB','HeadB']:
 vals=list(bounds[group].values());bounds[group+'_aggregate']=[min(v[i] for v in vals) for i in range(3)]+[max(v[i] for v in vals) for i in range(3,6)]
json.dump(bounds,open(BASE+'/assembly_world_bounds.json','w'),indent=2)
json.dump({'physical_mechanical_parts':sum(o.Name!='RFServiceSlackEnvelope' for o in objs),'nonphysical_routing_reservations':1,'mechanical_parts':len(objs),'main_placement_objects':len(bounds['MainB']),'head_solids':len(bounds['HeadB']),'all_valid':all(o.Shape.isValid() for o in C.Objects if hasattr(o,'Shape')),'scope':'Mechanical BRep with nominal/max PCB body envelopes and explicit lead reservations; detailed PCB copper available separately in electronics exports'},open(BASE+'/system_export_report.json','w'),indent=2)
print('EXPORTED',len(objs),'mechanical parts',len(bounds['MainB']),'MainB',len(bounds['HeadB']),'HeadB')
