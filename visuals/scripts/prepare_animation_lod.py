"""Render-only tessellation of native CAD, with explicit chord and angular tolerances."""
import sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];M=R/'mechanical/rev_b';O=R/'visuals/rev_b/_animation_lod';O.mkdir(parents=True,exist_ok=True)
sys.path.extend(['/usr/lib/freecad-python3/lib',str(M)])
import FreeCAD as A,MeshPart,socket_b_features
p=M/'CARBENTRA-P16-EVT-B.FCStd';d=A.openDocument(str(p));report={'source':str(p),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'linear_deflection_mm':.04,'angular_deflection_rad':.3,'purpose':'Animation-only subpixel display tessellation; studio source and selectable GLB retain full-resolution source meshes','parts':[]}
for o in d.Objects:
 if not hasattr(o,'Shape') or o.Shape.isNull():continue
 mesh=MeshPart.meshFromShape(Shape=o.Shape,LinearDeflection=.04,AngularDeflection=.3,Relative=False);mesh.write(str(O/(o.Name+'.stl')));report['parts'].append({'id':o.Name,'triangles':mesh.CountFacets})
(O/'lod_manifest.json').write_text(json.dumps(report,indent=2));print('LOD triangles',sum(p['triangles'] for p in report['parts']))
