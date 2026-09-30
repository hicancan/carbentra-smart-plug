"""Run with Blender loading carbentra_studio.blend. Non-destructive source-derived preview batching."""
import bpy,json,struct,os
from pathlib import Path
V=Path(os.environ.get('CARBENTRA_OUTPUT_DIR',str(Path(__file__).resolve().parents[1])));ROOT=Path(os.environ.get('CARBENTRA_PROJECT_ROOT',str(V.parent)))
allparts=[o for o in bpy.data.objects if any(c.name[:2] in ['01','02','03','04','05'] for c in o.users_collection)]
source_names={o.name for o in allparts}
bpy.ops.object.select_all(action='DESELECT')
for o in allparts:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(V/'exports/carbentra_assembly.glb'),export_format='GLB',use_selection=True,export_apply=False,export_extras=True)
batches={'PCB detail / routed copper':[], 'PCB detail / pads and vias':[]}
for o in allparts:
 if o.name.startswith('Copper_'):batches['PCB detail / routed copper'].append(o)
 elif o.name.startswith(('Via_','Pad_')):batches['PCB detail / pads and vias'].append(o)
for name,items in batches.items():
 if not items:continue
 members=[o.name for o in items];bpy.ops.object.select_all(action='DESELECT')
 for o in items:o.select_set(True)
 bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;o['source_members']=json.dumps(members);o['representation']='Actual source geometry batched by material; not electrically connected by this display operation'
# Keep the real product branding; omit redundant package-reference annotation glyphs in the lightweight view.
for o in list(bpy.data.objects):
 if o.name.startswith('PCB reference / '):bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if any(c.name[:2] in ['01','02','03','04','05'] for c in o.users_collection):o.select_set(True)
p=V/'exports/carbentra_twin_light.glb'
bpy.ops.export_scene.gltf(filepath=str(p),export_format='GLB',use_selection=True,export_apply=False,export_extras=True)
def inspect(p):
 b=p.read_bytes();l,t=struct.unpack_from('<II',b,12);j=json.loads(b[20:20+l]);return {'bytes':len(b),'nodes':len(j['nodes']),'meshes':len(j['meshes']),'names':[x.get('name') for x in j['nodes']]}
a=inspect(V/'exports/carbentra_assembly.glb');b=inspect(p)
required=[x['id'] for x in json.loads((ROOT/'mechanical/parts_manifest.json').read_text())['parts']]
assert all(n in b['names'] for n in required)
report={'full':{k:v for k,v in a.items() if k!='names'},'light':{k:v for k,v in b.items() if k!='names'},'node_reduction_percent':round((1-b['nodes']/a['nodes'])*100,1),'byte_reduction_percent':round((1-b['bytes']/a['bytes'])*100,1),'all_mechanical_part_names_preserved':True,'method':'Batch actual copper and pad/via meshes by material; omit redundant ref-designator glyph annotations; no decimation and no functional geometry changes'}
(V/'exports/twin_optimization.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
