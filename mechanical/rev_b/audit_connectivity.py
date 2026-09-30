#!/usr/bin/python3
import sys,os,json
BASE=os.path.dirname(os.path.abspath(__file__));sys.path.extend(['/usr/lib/freecad-python3/lib',BASE])
import FreeCAD as A,socket_b_features as m
D=A.openDocument(BASE+'/CARBENTRA-P16-B-base-provisional.FCStd')
pairs=[('Blade_PE','PEBus'),('PEBus','Contact_PE'),('Blade_L','PowerCore_L_RAW'),('PowerCore_L_RAW','MainFuseCollector1'),('MainFuseCollector1','MainFuseClip1'),('MainFuseClip1','MainFuseCap1'),('MainFuseCap2','MainFuseClip2'),('MainFuseClip2','MainFuseCollector2'),('MainFuseCollector2','PowerCore_L_FUSE_THERMAL'),('PowerCore_L_FUSE_THERMAL','ThermalLead2'),('ThermalLead1','PowerCore_L_PROTECTED'),('PowerCore_L_OUTPUT','Contact_L'),('Blade_N','PowerCore_N_RAW'),('PowerCore_N_OUTPUT','Contact_N')]
rows=[]
for a,b in pairs:
 x=D.getObject(a).Shape;y=D.getObject(b).Shape;rows.append({'a':a,'b':b,'overlap_mm3':x.common(y).Volume,'surface_distance_mm':x.distToShape(y)[0]})
p=D.getObject('Blade_PE').Shape.fuse(D.getObject('PEBus').Shape).fuse(D.getObject('Contact_PE').Shape)
rep={'brand':'CARBENTRA','front_view':'Look from+Z toward origin; +Y up, +X right; L right,N left,PE top','rear_view':'Look from−Z toward origin; +Y up,−X viewer right; L left,N right,PE top','interface_world':m.S,'main_line_chain':['Blade_L','PowerCore_L_RAW','MainFuseCollector1','MainFuseClip1','F_MAIN_SHF8020.5080','MainFuseClip2','MainFuseCollector2','PowerCore_L_FUSE_THERMAL','TF1','PowerCore_L_PROTECTED','J201.1','RS201','K101','J102.1','PowerCore_L_OUTPUT','Contact_L'],'neutral_chain':['Blade_N','PowerCore_N_RAW','J201.2','PCB neutral path','J102.2','PowerCore_N_OUTPUT','Contact_N'],'PE_geometric_fused_solid_count':len(p.Solids),'PE_geometric_valid':p.isValid(),'modeled_joint_interfaces':rows,'joint_geometry_pass':all(r['surface_distance_mm']<1e-6 for r in rows),'scope':'Geometry connectivity of represented external joints only. Fuse/thermal cutoff/relay/terminal internal conduction and joint processes are component/electrical assumptions. No resistance, fault, pullout or safety approval claim.'}
json.dump(rep,open(BASE+'/polarity_connectivity_report.json','w'),indent=2);print(json.dumps(rep,indent=2))
