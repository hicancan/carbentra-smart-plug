"""Run with Blender loading carbentra_studio.blend. Non-destructive source-derived preview batching."""
import bpy,json,struct,os,math
from pathlib import Path
V=Path(os.environ.get('CARBENTRA_OUTPUT_DIR',str(Path(__file__).resolve().parents[1])));ROOT=Path(os.environ.get('CARBENTRA_PROJECT_ROOT',str(V.parent)))
allparts=[o for o in bpy.data.objects if any(c.name[:2] in ['01','02','03','04','05'] for c in o.users_collection)]
source_names={o.name for o in allparts}
bpy.ops.object.select_all(action='DESELECT')
for o in allparts:o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(V/'exports/carbentra_assembly.glb'),export_format='GLB',use_selection=True,export_apply=False,export_extras=True)
lod_parts=[]
if os.environ.get('CARBENTRA_TWIN_LOD_DIR'):
 lod=Path(os.environ['CARBENTRA_TWIN_LOD_DIR'])
 keep_full={'RearShell','FrontLid','RearFinish','SeamRing','LocalButton','RearmButton','StatusLightGuide','Blade_L','Blade_N','Blade_PE','BladeSleeve_L','BladeSleeve_N'}
 for o in allparts:
  p=lod/(o.name+'.stl')
  if o.name not in keep_full and p.exists():
   mats=list(o.data.materials);bpy.ops.wm.stl_import(filepath=str(p));temp=bpy.context.object;temp.scale=(.001,)*3;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
   o.data=temp.data.copy();bpy.data.objects.remove(temp,do_unlink=True);o.data.materials.clear()
   for m in mats:o.data.materials.append(m)
   o['display_tessellation_chord_mm']=.04;lod_parts.append(o.name)
(V/'exports/twin_tessellation.json').write_text(json.dumps({'native_cad_retessellated_parts':lod_parts,'chord_tolerance_mm':.04 if lod_parts else None,'angular_tolerance_rad':.3 if lod_parts else None,'external_surfaces_preserved_full_resolution':True,'statement':'Display approximation of the same native CAD surfaces; not geometry-identical to full-resolution mesh' if lod_parts else 'No retessellation'},indent=2), encoding='utf-8', newline='\n')
batches={'PCB detail / routed copper':[], 'PCB detail / pads and vias':[]}
for o in allparts:
 if o.name.removeprefix('MainB_').removeprefix('HeadB_').startswith('Copper_'):batches['PCB detail / routed copper'].append(o)
 elif o.name.removeprefix('MainB_').removeprefix('HeadB_').startswith(('Via_','Pad_')):batches['PCB detail / pads and vias'].append(o)
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
required=[x['id'] for x in json.loads(Path(os.environ.get('CARBENTRA_MECHANICAL_DIR',str(ROOT/'mechanical')),'parts_manifest.json').read_text(encoding='utf-8'))['parts'] if x.get('render_default',True) is not False and x.get('geometry_role')!='clearance_envelope']
assert all(n in b['names'] for n in required)
report={'full':{k:v for k,v in a.items() if k!='names'},'light':{k:v for k,v in b.items() if k!='names'},'node_reduction_percent':round((1-b['nodes']/a['nodes'])*100,1),'byte_reduction_percent':round((1-b['bytes']/a['bytes'])*100,1),'all_mechanical_part_names_preserved':True,'method':'Batch actual copper and pad/via meshes by material; omit redundant ref-designator glyph annotations; '+('internal native-CAD display tessellation at 0.04 mm chord / 0.3 rad angular tolerance; full-resolution exterior preserved' if lod_parts else 'no retessellation')}
(V/'exports/twin_optimization.json').write_text(json.dumps(report,indent=2), encoding='utf-8', newline='\n');print(json.dumps(report,indent=2))
