from pathlib import Path
import sys,json,hashlib
sys.path.append('/usr/lib/freecad/lib');import FreeCAD as A,Part
R=Path(__file__).resolve().parents[1];src=R.parent/'thermal/exports/thermal_sensor_envelope.FCStd';doc=A.openDocument(str(src));solids=[];names=[]
for obj in doc.Objects:
 if not hasattr(obj,'Shape'):continue
 for shape in obj.Shape.Solids:
  t=shape.copy();t.rotate(A.Vector(0,0,0),A.Vector(1,0,0),180);t.translate(A.Vector(4.8272413,1.25,43.465));solids.append(t);names.append('HeadB_'+obj.Name)
with(R/'exports/remote_head_assembled.obj').open('w')as f:
 off=1
 for name,s in zip(names,solids):
  vs,fs=s.tessellate(.05);f.write(f'o {name}\n')
  for v in vs:f.write(f'v {v.x:.6f} {v.y:.6f} {v.z:.6f}\n')
  for face in fs:f.write('f '+' '.join(str(k+off)for k in face)+'\n')
  off+=len(vs)
bbs=[s.BoundBox for s in solids]
record={'source':str(src.relative_to(R.parents[2])),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'object_count':len(solids),'all_valid':all(s.isValid() and s.Volume>0 for s in solids),'units':'mm','already_in_assembly_world_frame':True,'board_id':'HeadB','proper_rotation_determinant':1,'matrix_local_to_world':[[1,0,0,4.8272413],[0,-1,0,1.25],[0,0,-1,43.465],[0,0,0,1]],'sensor_center_mm':[8.2272413,-4.75],'board_center_xy_mm':[10.8272413,-4.75],'board_substrate_back_z_mm':43.465,'pickup_copper_face_z_mm':43.5,'bounds_min_mm':[min(b.XMin for b in bbs),min(b.YMin for b in bbs),min(b.ZMin for b in bbs)],'bounds_max_mm':[max(b.XMax for b in bbs),max(b.YMax for b in bbs),max(b.ZMax for b in bbs)]}
(R/'exports/remote_head_assembled.json').write_text(json.dumps(record,indent=2));(R/'validation/remote_head_geometry.json').write_text(json.dumps(record,indent=2));print(json.dumps(record),flush=True)
out=A.newDocument('CARBENTRA_Remote_Head');objects=[]
for name,s in zip(names,solids):
 obj=out.addObject('Part::Feature',name);obj.Shape=s;objects.append(obj)
Part.export(objects,str(R/'exports/remote_head_assembled.step'))
