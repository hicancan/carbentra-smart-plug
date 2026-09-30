#!/usr/bin/python3
import os,sys,json,hashlib
B=os.path.dirname(os.path.abspath(__file__));sys.path.extend(['/usr/lib/freecad-python3/lib',B]);import FreeCAD as A,Part,socket_b_features
def equivalent(a,b):
 aa=a.split();bb=b.split()
 if len(aa)!=len(bb):return False
 for x,y in zip(aa,bb):
  if x==y:continue
  try:
   if abs(float(x)-float(y))>1e-10:return False
  except ValueError:return False
 return True
D=A.openDocument(B+'/CARBENTRA-P16-B-base-provisional.FCStd');E=A.openDocument(B+'/CARBENTRA-P16-EVT-B.FCStd');rows=[]
for o in D.Objects:
 if not hasattr(o,'PartKind'):continue
 q=E.getObject(o.Name);a=o.Shape.cleaned().exportBrepToString();b=q.Shape.cleaned().exportBrepToString();rows.append({'part':o.Name,'brep_serialization_equal':a==b,'brep_geometry_numeric_equivalent_1e_10':equivalent(a,b),'volume_difference_mm3':abs(o.Shape.Volume-q.Shape.Volume)})
C=A.openDocument(B+'/CARBENTRA-P16-EVT-B_system_assembly.FCStd');cs=[o.Shape for o in C.Objects if hasattr(o,'Shape') and not o.Shape.isNull() and o.Name!='Mech_RFServiceSlackEnvelope'];st=Part.Shape();st.read(B+'/CARBENTRA-P16-EVT-B_system_assembly.step');nativev=sum(s.Volume for s in cs);stepv=sum(s.Volume for s in st.Solids)
r={'mechanical_source_to_delivery':rows,'all_mechanical_brep_equal':all(x['brep_serialization_equal'] for x in rows),'all_mechanical_geometry_numeric_equivalent':all(x['brep_geometry_numeric_equivalent_1e_10'] for x in rows),'numeric_serialization_comparison_tolerance':1e-10,'system_native_objects':len(cs),'step_roundtrip_solids':len(st.Solids),'step_roundtrip_all_valid':all(s.isValid() for s in st.Solids),'native_volume_mm3':nativev,'step_volume_mm3':stepv,'relative_volume_difference':abs(nativev-stepv)/nativev}
json.dump(r,open(B+'/export_roundtrip_report.json','w'),indent=2);print({k:v for k,v in r.items() if k!='mechanical_source_to_delivery'})
