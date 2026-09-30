#!/usr/bin/python3
"""Optional export-only supplement: detailed PCB, no frozen geometry modification."""
import os,sys,json,hashlib,datetime
B=os.path.dirname(os.path.abspath(__file__));R=os.path.abspath(B+'/../..');sys.path.extend(['/usr/lib/freecad-python3/lib',B])
import FreeCAD as A,Part,socket_b_features
import datetime as _dtmod
sources={'mechanical':B+'/CARBENTRA-P16-EVT-B.FCStd','main':R+'/electronics/rev_b/integrated/exports/integrated_assembly.FCStd','head':R+'/electronics/rev_b/integrated/exports/remote_head_assembled.step'}
D=A.openDocument(sources['mechanical']);E=A.openDocument(sources['main']);C=A.newDocument('CARBENTRA_P16_EVT_B_Detailed')
counts={};valid={};allobjs=[]
for group,doc,offset in [('mechanical',D,0),('main',E,11.5)]:
 objs=[o for o in doc.Objects if hasattr(o,'Shape') and not o.Shape.isNull() and o.Shape.Volume>0 and len(o.Shape.Solids)>0 and o.Name!='RFServiceSlackEnvelope']
 counts[group]={'objects':len(objs),'solids':sum(len(o.Shape.Solids) for o in objs)};valid[group]=all(s.isValid() for o in objs for s in o.Shape.Solids)
 for o in objs:
  sh=o.Shape.copy();sh.translate(A.Vector(0,0,offset));q=C.addObject('Part::Feature',group+'_'+o.Name);q.Label=o.Label;q.Shape=sh;q.Placement=sh.Placement;allobjs.append(q)
 print(group,counts[group],valid[group],flush=True)
h=Part.Shape();h.read(sources['head']);counts['head']={'objects':len(h.Solids),'solids':len(h.Solids)};valid['head']=all(s.isValid() for s in h.Solids)
for i,sh in enumerate(h.Solids):
 q=C.addObject('Part::Feature','HeadB_'+str(i));q.Shape=sh;q.Placement=sh.Placement;allobjs.append(q)
C.recompute();out=B+'/CARBENTRA-P16-EVT-B_system_detailed.step';
if '--verify-existing' not in sys.argv:Part.export(allobjs,out)
print('STEP bytes',os.path.getsize(out),flush=True)
back=Part.Shape();back.read(out);native_volume=sum(o.Shape.Volume for o in allobjs);step_volume=sum(s.Volume for s in back.Solids)
report={'brand':'CARBENTRA','revision':'CARBENTRA-P16-EVT-B','created_utc':_dtmod.datetime.now(_dtmod.timezone.utc).isoformat(),'scope':'Export-only supplement to the frozen digital review snapshot. Detailed PCB copper/lead/package geometry, not new physical qualification or vendor-internal CAD. RF slack reservation deliberately excluded as non-physical.','source_sha256':{k:{'path':os.path.relpath(p,R),'sha256':hashlib.sha256(open(p,'rb').read()).hexdigest()}for k,p in sources.items()},'frame':'World mm; MainB translated+11.5Z once; HeadB already assembled','counts':counts,'all_input_solids_valid':all(valid.values()),'input_valid_by_group':valid,'native_object_count':len(allobjs),'native_solid_count':sum(x['solids'] for x in counts.values()),'step_roundtrip_solid_count':len(back.Solids),'step_roundtrip_all_valid':all(s.isValid() for s in back.Solids),'native_summed_volume_mm3':native_volume,'step_summed_volume_mm3':step_volume,'relative_summed_volume_difference':abs(native_volume-step_volume)/native_volume,'output':{'path':os.path.relpath(out,R),'bytes':os.path.getsize(out),'sha256':hashlib.sha256(open(out,'rb').read()).hexdigest()}}
assert report['all_input_solids_valid'] and report['step_roundtrip_all_valid'];assert report['native_solid_count']==report['step_roundtrip_solid_count'];assert report['relative_summed_volume_difference']<1e-6
json.dump(report,open(B+'/detailed_export_report.json','w'),indent=2);print(json.dumps(report,indent=2))
