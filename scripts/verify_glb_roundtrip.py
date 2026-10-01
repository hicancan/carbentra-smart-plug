"""Run with Blender in background; imports one GLB and records basic real-reader QA."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];source=Path(args[0]).resolve();dest=Path(args[1]).resolve()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
lo=[min(p[a] for p in points) for a in range(3)];hi=[max(p[a] for p in points) for a in range(3)];dims=[hi[a]-lo[a] for a in range(3)]
out={'scope':'Actual Blender GLB import and world bounding-box check; not a manufacturing check','file':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'imported_meshes':len(meshes),'vertices':sum(len(o.data.vertices) for o in meshes),'faces':sum(len(o.data.polygons) for o in meshes),'world_bounds_m':[lo,hi],'dimensions_m':dims,'import_pass':len(meshes)>0,'expected_product_scale_pass':all(abs(a-b)<.003 for a,b in zip(sorted(dims),sorted([.108,.093,.086])))}
out['passed']=out['import_pass'] and out['expected_product_scale_pass'];dest.write_text(json.dumps(out,indent=2)+'\n', encoding='utf-8', newline='\n');print(json.dumps(out));assert out['passed']
