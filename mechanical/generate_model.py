#!/usr/bin/python3
import sys,os,json,csv
BASE=os.path.dirname(os.path.abspath(__file__))
sys.path.extend(['/usr/lib/freecad-python3/lib',BASE])
import FreeCAD as App,Part,MeshPart
from socket_features import SocketPart,P,H
os.makedirs(BASE+'/meshes',exist_ok=True);os.makedirs(BASE+'/step',exist_ok=True)
doc=App.newDocument('CARBENTRA-P16-EVT-A')
ss=doc.addObject('Spreadsheet::Sheet','Parameters')
for i,(n,v) in enumerate([('Width',88),('Height',88),('Depth',55)],1):ss.set('A'+str(i),n);ss.set('B'+str(i),str(v)+' mm');ss.setAlias('B'+str(i),n)
ss.set('A5','Development model; do not energize')
items=[('RearShell','Rear housing + PCB standoffs','PC-FR candidate',[.92,.94,.93],-25),('FrontLid','Front housing','PC-FR candidate',[.94,.96,.95],62),('SeamRing','Registration seam trim','PC candidate',[.03,.23,.24],36),('RearAccent','Rear perimeter finish layer (40um)','Decorative coating candidate',[.05,.10,.12],-24),('Carrier','Insulating socket carrier','PBT-FR candidate',[.22,.27,.28],22),('ShutterGuide','Shutter guide','PBT-FR candidate',[.28,.33,.33],37),('ShutterSlider','Coupled shutter development envelope','PBT-FR candidate',[.14,.19,.20],46),('Button','Front control plunger','PC candidate',[.08,.39,.37],64),('LightGuide','Status light guide','Optical PC candidate',[.2,.85,.63],64),('PEBus','Unswitched PE conductor route','Copper alloy candidate',[.7,.43,.16],0)]
for n in ['L','N','PE']:items.append(('Blade_'+n,n+' input blade - provisional','Copper alloy candidate',[.74,.62,.33],-40));items.append(('Contact_'+n,n+' receptacle spring envelope','Copper alloy candidate',[.76,.59,.29],25))
items.append(('AntennaFPC','Taoglas FXP73.07.0100A FPC envelope','Flexible antenna substrate',[.13,.13,.12],8))
items.append(('AntennaCoax','100mm coax routing envelope; RF endpoint provisional','Coax outer jacket',[.10,.10,.10],8))
for k,label,mat,col in [('FuseHolder','Schurter OGN0031.8201 holder envelope','PBT candidate',[.20,.21,.22]),('FuseCeramic','Littelfuse0216016.MXP ceramic5x20 fuse envelope','Ceramic',[.85,.85,.79]),('FuseCap1','Fuse endcap1','Plated metal',[.65,.67,.68]),('FuseCap2','Fuse endcap2','Plated metal',[.65,.67,.68]),('FuseLead1','Holder contact1 + lead','Copper alloy',[.7,.55,.27]),('FuseLead2','Holder contact2 + lead','Copper alloy',[.7,.55,.27]),('ThermalBody','Sensience G5 thermal cutoff body candidate','Metal can',[.60,.62,.62]),('ThermalLead1','Thermal cutoff lead1','Metal',[.63,.65,.65]),('ThermalLead2','Thermal cutoff lead2','Metal',[.63,.65,.65])]:
 items.append((k,label,mat,col,12))
for k in ['AuxFuseBody','AuxFuseCap1','AuxFuseCap2','AuxFuseLead1','AuxFuseLead2']:
 items.append((k,'0215001.MXEP auxiliary fuse '+k,'Ceramic/metal candidate',[.82,.80,.72] if k=='AuxFuseBody' else [.65,.66,.67],10))
for r in [q['id'] for q in H['routes']]:
 items.append(('WireCore_'+r,r+' conductor routing envelope','Copper candidate',[.65,.34,.12],8))
 items.append(('WireJacket_'+r,r+' insulating jacket envelope','Insulation qualification pending',[.24,.12,.06] if r.startswith(('L','AUX_L')) else [.08,.25,.60],8))
for i in range(4):items.append(('Screw_'+str(i),'Rear housing screw '+str(i+1),'Steel candidate',[.4,.43,.44],-35))
manifest=[];objs=[]
for k,label,mat,col,explode in items:
 obj=doc.addObject('Part::FeaturePython',k);SocketPart(obj,k);obj.Label=label
 for n in ['Width','Height','Depth']:obj.setExpression(n,'Parameters.'+n)
 obj.addProperty('App::PropertyString','MaterialCandidate').MaterialCandidate=mat
 obj.addProperty('App::PropertyString','ReleaseStatus').ReleaseStatus='DEVELOPMENT / FABRICATION HOLD'
 doc.recompute();shape=obj.Shape
 if shape.isNull() or not shape.isValid():raise RuntimeError('Invalid geometry '+k)
 shape.exportStep(BASE+'/step/'+k+'.step')
 mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=.005 if k in ['RearShell','FrontLid','RearAccent','Button','LightGuide'] else .04,AngularDeflection=.08 if k in ['RearShell','FrontLid','RearAccent','Button','LightGuide'] else .16,Relative=False);mesh.write(BASE+'/meshes/'+k+'.stl')
 b=shape.BoundBox
 manifest.append({'id':k,'name':label,'file':'meshes/'+k+'.stl','material':mat,'color':col,'explode':[0,0,explode],'volume_mm3':shape.Volume,'solids':len(shape.Solids),'bbox_mm':[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],'valid':shape.isValid()})
 objs.append(obj)
doc.recompute();doc.saveAs(BASE+'/CARBENTRA-P16-EVT-A.FCStd')
Part.export(objs,BASE+'/CARBENTRA-P16-EVT-A.step')
json.dump({'units':'mm','front_axis':'+Z','origin':'rear plane center','parts':manifest},open(BASE+'/parts_manifest.json','w'),indent=2)
# Measure exact BRep intersections. Intentional connected conductors are listed separately.
intentional={frozenset(['PEBus','Blade_PE']),frozenset(['PEBus','Contact_PE'])}
for r in [q['id'] for q in H['routes']]:
 route=next(q for q in H['routes'] if q['id']==r)
 if route['from'].startswith(('Blade_','Contact_','FuseLead','ThermalLead','AuxFuseLead','WireCore_')):intentional.add(frozenset(['WireCore_'+r,route['from']]))
 if route['to'].startswith(('FuseLead','ThermalLead','AuxFuseLead')):intentional.add(frozenset(['WireCore_'+r,route['to']]))
for a,b in [('FuseLead1','FuseCap1'),('FuseLead2','FuseCap2'),('ThermalBody','ThermalLead1'),('ThermalBody','ThermalLead2')]:intentional.add(frozenset([a,b]))
intentional.add(frozenset(['AntennaFPC','AntennaCoax']))
for a,b in [('AuxFuseLead1','AuxFuseCap1'),('AuxFuseLead2','AuxFuseCap2'),('WireJacket_AUX_L_IN','WireJacket_L_IN_POST'),('WireJacket_AUX_N','WireJacket_N_IN')]:intentional.add(frozenset([a,b]))
intersections=[]
for i,a in enumerate(objs):
 for b in objs[i+1:]:
  vol=a.Shape.common(b.Shape).Volume
  if vol>1e-5:intersections.append({'a':a.Name,'b':b.Name,'volume_mm3':vol,'intentional':frozenset([a.Name,b.Name]) in intentional})
report={'engine':'FreeCAD '+'.'.join(App.Version()[:3]),'parts':len(objs),'all_shapes_valid':all(o.Shape.isValid() for o in objs),'all_single_solid':all(len(o.Shape.Solids)==1 for o in objs),'intersections':intersections,'note':'Interference audit is geometric only. Electrical safety, creepage, contact force, shutter operation, tolerances, standards and certification are NOT validated.'}
json.dump(report,open(BASE+'/validation.json','w'),indent=2)
print(json.dumps(report,indent=2))
