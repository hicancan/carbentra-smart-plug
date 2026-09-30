"""CarbonMirror studio. All geometry imported from the common engineering assembly.
Usage: blender -b --python visuals/scripts/build_studio.py -- preview|stills|animation|all
Units: source mm, Blender meters. Mesh source manifests remain authority.
"""
import bpy, math, json, sys, os, subprocess, hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(os.environ.get('CM_PROJECT_ROOT',str(Path(__file__).resolve().parents[2]))); OUT=Path(os.environ.get('CM_OUTPUT_DIR',str(ROOT/'visuals'))); MODE=sys.argv[-1] if '--' in sys.argv else 'preview'
for d in ['renders','exports','animation']: (OUT/d).mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for d in bpy.data.materials: bpy.data.materials.remove(d)
scene=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0
scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=1
scene.render.engine='CYCLES';scene.cycles.samples=96;scene.cycles.use_denoising=False;scene.cycles.adaptive_threshold=.025
scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-3.5;scene.view_settings.look='AgX - Medium High Contrast'
scene.world.color=(.25,.25,.25)
scene.world.use_nodes=True; scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.23,.29,.32,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4

def mat(n,c,metal=0,rough=.32,trans=0,emit=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;p.inputs['Transmission Weight'].default_value=trans
 if emit: p.inputs['Emission Color'].default_value=(*c,1);p.inputs['Emission Strength'].default_value=emit
 return m
M={'ivory':mat('01 • Warm ivory / satin PC',(.82,.825,.765),rough=.28),'dark':mat('02 • Graphite / textured polymer',(.021,.031,.035),rough=.36),'teal':mat('03 • Jade status accent',(.006,.09,.056),rough=.25),'led':mat('04 • Mint lightguide',(.13,.8,.61),rough=.18,emit=2),'brass':mat('05 • Nickel brass contacts',(.68,.5,.2),metal=.85,rough=.23),'steel':mat('06 • Stainless hardware',(.5,.55,.58),metal=.9,rough=.24),'pcb':mat('07 • Deep green soldermask',(.014,.14,.095),rough=.32),'black':mat('08 • Component moulding',(.017,.022,.025),rough=.3),'white':mat('09 • Silkscreen',(.8,.83,.78),rough=.5),'glass':mat('10 • Diagnostic transparent shell',(.68,.9,.87),rough=.08,trans=.94),'ink':mat('11 • Pad print charcoal',(.008,.016,.018),rough=.6)}
M['trace']=mat('16 • Routed copper inspection / mask unqualified',(.015,.25,.15),metal=.2,rough=.35)
# Nonphysical diagnostic ghost treatment: see through the unchanged enclosure without refraction distortion.
g=M['glass'].node_tree;g.nodes.clear();out=g.nodes.new('ShaderNodeOutputMaterial');mix=g.nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.12;tr=g.nodes.new('ShaderNodeBsdfTransparent');tr.inputs[0].default_value=(.88,.98,.95,1);surf=g.nodes.new('ShaderNodeBsdfPrincipled');surf.inputs['Base Color'].default_value=(.4,.75,.65,1);surf.inputs['Roughness'].default_value=.35;g.links.new(tr.outputs[0],mix.inputs[1]);g.links.new(surf.outputs[0],mix.inputs[2]);g.links.new(mix.outputs[0],out.inputs[0])
M['lightpipe']=mat('15 • Optical lightpipe body',(.22,.65,.50),rough=.18,trans=.5)
M['wirebrown']=mat('13 • L conductor jacket',(.18,.05,.018),rough=.38);M['wireblue']=mat('14 • N conductor jacket',(.012,.08,.28),rough=.38)
M['ceramic']=mat('12 • Ceramic packages',(.30,.17,.075),rough=.4)
parts=[]; meta={}; electronics=[]
params=json.loads((ROOT/'mechanical/design_parameters.json').read_text()); front_z=params['enclosure']['depth']/1000
(OUT/'exports/render_context.json').write_text(json.dumps({'revision':params.get('revision','Engineering development'),'enclosure_mm':params['enclosure'],'source_root':str(ROOT),'status':'Engineering development; verification pending'},indent=2))

def assign(o,key):o.data.materials.clear();o.data.materials.append(M[key])
def material_for(n):
 n=n.lower()
 if n in ['fuseceramic','auxfusebody']:return 'ivory'
 if n.startswith(('auxfusecap','auxfuselead')):return 'steel'
 if n.startswith(('fusecap','thermal')):return 'steel'
 if n.startswith('fuselead'):return 'brass'
 if n.startswith('antenna'):return 'black'
 if n.startswith('wirecore'):return 'brass'
 if n.startswith('wirejacket'):return 'wireblue' if '_n_' in n or n.endswith('_n') else 'wirebrown'
 if any(x in n for x in ['led','light','lens']):return 'led'
 if any(x in n for x in ['seam','gasket','button']):return 'teal'
 if any(x in n for x in ['blade','bus','contact','copper','spring','terminal']):return 'brass'
 if any(x in n for x in ['screw','washer','insert']):return 'steel'
 if any(x in n for x in ['base','rearaccent','carrier','shutter','relay','module','capacitor','ic_','fuse']):return 'dark'
 if any(x in n for x in ['pcb','board']):return 'pcb'
 return 'ivory'

def import_stl(path,name):
 bpy.ops.wm.stl_import(filepath=str(path));o=bpy.context.object;o.name=name;o.scale=(.001,)*3;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35));return o
mf=ROOT/'mechanical/parts_manifest.json'
raw=json.loads(mf.read_text()) if mf.exists() else {}
entries=raw.get('parts',[]) if isinstance(raw,dict) else raw
for e in entries:meta[e.get('id',e.get('name',''))]=e
if not entries:raise RuntimeError('Mechanical manifest required')
for entry in entries:
 p=ROOT/'mechanical'/entry['file']
 o=import_stl(p,entry['id']);parts.append(o);assign(o,material_for(o.name))
 if o.name=='LightGuide':
  o.data.materials.clear();o.data.materials.append(M['lightpipe']);o.data.materials.append(M['led'])
  for face in o.data.polygons:face.material_index=1 if face.center.z>front_z-.0001 else 0
 # CAD triangulation kept intact; bevel gives physical edge catches without shape redesign.
 if o.name not in ['RearAccent','SeamRing','Button','LightGuide']:
  mod=o.modifiers.new('Tooling edge highlight','BEVEL');mod.width=.00012;mod.segments=3;mod.limit_method='ANGLE';mod.angle_limit=.55
 mod=o.modifiers.new('Area weighted normals','WEIGHTED_NORMAL');mod.keep_sharp=True
for p in [ROOT/'electronics/exports/pcb_assembly.obj']:
 bpy.ops.wm.obj_import(filepath=str(p),forward_axis='Y',up_axis='Z')
 imported=[o for o in bpy.context.selected_objects if o.type=='MESH']
 for o in imported:o.scale=(.001,)*3
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for o in imported:
  parts.append(o);electronics.append(o)
  n=o.name.lower()
  key='trace' if n.startswith('copper_') else 'brass' if n.startswith(('pad_','via_')) else 'pcb' if n.startswith('pcb') else 'steel' if n.startswith('u1_') else 'teal' if n.startswith('j') else 'ceramic' if n.startswith('c') else 'led' if n.startswith('led1') else 'black'
  assign(o,key)
if not parts:raise RuntimeError('Common engineering meshes missing; no substitute geometry generated')
for o in parts:o['source']='Common CAD/ECAD engineering model';o['development_status']='Engineering development; verification pending'
validation={'units':'metres','parts':len(parts),'mechanical_source':'mechanical/parts_manifest.json','electronic_source':'electronics/exports/pcb_assembly.obj','bounds':{},'source_sha256':{'mechanical_manifest':hashlib.sha256(mf.read_bytes()).hexdigest(),'electronics_obj':hashlib.sha256((ROOT/'electronics/exports/pcb_assembly.obj').read_bytes()).hexdigest()}}
for o in parts:
 points=[o.matrix_world@Vector(c) for c in o.bound_box]
 bb=[min(v[i] for v in points) for i in range(3)]+[max(v[i] for v in points) for i in range(3)]
 validation['bounds'][o.name]=bb
 if o.name in meta:
  expected=meta[o.name]['bbox_mm'];err=max(abs(bb[i]*1000-expected[i]) for i in range(6))
  if err>.05:raise RuntimeError('Mesh transform mismatch '+o.name+': '+str(err)+'mm')
(OUT/'exports/import_validation.json').write_text(json.dumps(validation,indent=2))

font=bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
cn=bpy.data.fonts.load('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
def text(body,name,size,loc,material='ink',fontob=font):
 c=bpy.data.curves.new(name,'FONT');c.body=body;c.align_x='CENTER';c.size=size;c.extrude=.000008;c.font=fontob;o=bpy.data.objects.new(name,c);scene.collection.objects.link(o);o.location=loc;assign(o,material);return o
branding=[text('CARBONMIRROR','Brand / front pad print',.0034,(0,-.020,front_z+.00004)),text('碳镜校园','Brand / Chinese',.0034,(0,-.025,front_z+.00004),fontob=cn)]
parts+=branding
# Actual source reference designators, drawn as inspection annotations on large package envelopes.
board_labels=[]
for o in list(electronics):
 n=o.name
 if n.startswith(('Pad_','PCB_','Copper_','Via_')):continue
 points=[o.matrix_world@Vector(c) for c in o.bound_box];lo=[min(v[i] for v in points) for i in range(3)];hi=[max(v[i] for v in points) for i in range(3)]
 if hi[0]-lo[0]<.008 or hi[1]-lo[1]<.006:continue
 ref=n.split('_')[0];label=text(ref,'PCB reference / '+ref,.00165,((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,hi[2]+.000035),'white');label['representation']='Visual inspection reference designator';board_labels.append(label)
electronics+=board_labels;parts+=board_labels
basepos={o.name:o.location.copy() for o in parts}
# Human-readable model organization; names persist in GLB nodes.
collections={}
for name in ['01 Enclosure and controls','02 Receptacle mechanism','03 Conductors and protection','04 PCB and packages','05 Brand markings']:
 c=bpy.data.collections.new(name);scene.collection.children.link(c);collections[name]=c
for o in parts:
 if o in electronics:key='04 PCB and packages'
 elif o in branding:key='05 Brand markings'
 elif any(x in o.name.lower() for x in ['wire','bus','blade','fuse','thermal']):key='03 Conductors and protection'
 elif any(x in o.name.lower() for x in ['carrier','shutter','contact']):key='02 Receptacle mechanism'
 else:key='01 Enclosure and controls'
 for c in list(o.users_collection):c.objects.unlink(o)
 collections[key].objects.link(o)

# Plane and studio rig
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.0205));floor=bpy.context.object;floor.name='Studio cyclorama';floor.data.materials.append(mat('Studio warm grey',(.54,.59,.58),rough=.44))
def area(name,pos,power,size,color):
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.data.color=color;o.rotation_euler=(Vector((0,0,.025))-o.location).to_track_quat('-Z','Y').to_euler();return o
area('Key / large softbox',(.09,-.12,.23),12,.2,(1,.94,.85));area('Rim / cool strip',(-.14,.08,.13),5,.14,(.72,.9,1));area('Fill / overhead',(.02,.13,.24),3,.18,(1,1,1))
rear_light=area('Rear / inspection softbox',(.04,.06,-.16),7,.15,(.9,.95,1));rear_light.hide_render=True
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Camera / studio';scene.camera=cam;cam.data.lens=58;cam.data.clip_start=.01;cam.data.clip_end=1.0
if bpy.data.collections.get('Collection'):bpy.data.collections['Collection'].name='90 Studio rig'

def camera(pos,target=(0,0,.02),ortho=None):
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO' if ortho else 'PERSP'
 if ortho:cam.data.ortho_scale=ortho

def workbench():
 scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.4;scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.display.shading.cavity_type='SCREEN';scene.display.shading.curvature_ridge_factor=1.25;scene.display.shading.curvature_valley_factor=1.15;scene.display.shading.background_type='WORLD';scene.world.color=(.78,.82,.8);scene.display.render_aa='8';scene.display.shading.shadow_intensity=.35;scene.display.shading.studio_light='paint.sl';scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0

def reset():
 for o in parts:o.location=basepos[o.name].copy();o.hide_render=False
 floor.hide_render=False

def render(name,size=(2400,2000),samples=256):
 if MODE=='technical_preview':
  name='00_'+name;size=(1000,round(1000*size[1]/size[0]));samples=24
 scene.render.resolution_x=size[0];scene.render.resolution_y=size[1];scene.cycles.samples=samples;scene.render.filepath=str(OUT/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
 anchors={}
 for o in parts:
  if o.type=='MESH':
   center=sum((o.matrix_world @ Vector(c) for c in o.bound_box),Vector())/8
   q=world_to_camera_view(scene,cam,center);anchors[o.name]=[q.x*size[0],(1-q.y)*size[1]]
 (OUT/'renders'/f'{name}_anchors.json').write_text(json.dumps(anchors,indent=2))

# Explicit presentation layers are derived from the mechanical grouping. Offsets do not alter assembled geometry.
spacing={-40:-40,-35:-35,-25:-25,-24:-24,0:0,8:8,10:10,12:12,22:40,25:45,36:68,37:55,46:62,62:80,64:80}
def explosion_mm(o):
 if o in electronics:return 20
 if o in branding:return 80
 return meta.get(o.name,{}).get('presentation_explode_mm',spacing.get(meta.get(o.name,{}).get('explode',[0,0,0])[2],meta.get(o.name,{}).get('explode',[0,0,0])[2]))
def explode(factor=1):
 for o in parts:o.location=basepos[o.name]+Vector((0,0,explosion_mm(o)/1000*factor))
(OUT/'exports/visual_explosion_offsets.json').write_text(json.dumps({'status':'Display-only inspection layout; not a manufacturing assembly procedure','offsets_mm':{o.name:explosion_mm(o) for o in parts}},indent=2))

def save_export():
 reset();scene.render.film_transparent=False;scene.render.engine='CYCLES';scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-3.5;camera((.145,-.185,.215));
 bpy.ops.object.select_all(action='DESELECT')
 for o in parts:o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(OUT/'exports/carbonmirror_assembly.glb'),export_format='GLB',use_selection=True,export_apply=False,export_extras=True)
 scene.render.resolution_x=2400;scene.render.resolution_y=2000;scene.cycles.samples=256;scene.render.filepath=str(OUT/'renders/01_hero_ivory.png');bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'carbonmirror_studio.blend'),compress=True)

save_export()
if MODE=='views':
 if MODE=='technical_preview':sys.exit(0)
 reset();floor.hide_render=True;scene.render.film_transparent=True;scene.render.engine='CYCLES'
 for name,pos in [('front',(0,0,.3)),('rear',(0,0,-.3)),('left',(-.3,0,.0175)),('right',(.3,0,.0175)),('top',(0,.3,.0175)),('bottom',(0,-.3,.0175))]:
  camera(pos,(0,0,.0175),.13);rear_light.hide_render=name=='front';render('view_'+name,(1400,1400),96);rear_light.hide_render=True
 save_export()
if MODE=='view_preview':
 floor.hide_render=True;scene.render.film_transparent=True;camera((-.3,0,.0175),(0,0,.0175),.13);render('00_side_preview',(1000,1000),32)
 camera((0,0,.3),(0,0,.0175),.13);render('00_front_preview',(1000,1000),32)
if MODE=='rear_preview':
 floor.hide_render=True;rear_light.hide_render=False;camera((.14,.145,-.17),(0,0,.02));render('00_rear_preview',(1000,850),32)
if MODE=='preview':render('00_preview',(1000,850),32)
if MODE=='workbench_preview':
 floor.hide_render=True;workbench();render('00_workbench_preview',(1000,850),32)
if MODE=='eevee_preview':
 scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=128;render('00_eevee_preview',(1000,850),32)
if MODE in ('stills','all','hero','hero_detail','technical','technical_preview'):
 if MODE not in ('technical','technical_preview','hero_detail'):render('01_hero_ivory')
 if MODE not in ('technical','technical_preview'):
  camera((-.135,-.13,.25));render('02_hero_detail')
 if MODE in ('hero','hero_detail'):sys.exit(0)
 reset();floor.hide_render=True;camera((.14,.145,-.17),(0,0,.02));rear_light.hide_render=False;render('03_rear_interface',samples=128);rear_light.hide_render=True
 reset()
 for o in parts:
  if o not in electronics:o.hide_render=True
 camera((.09,-.12,.17),(0,0,.014),.12);render('09_pcb_assembly',samples=128)
 reset()
 for o in parts:
  if o.name in ['FrontLid','RearShell','RearAccent','SeamRing','Button','LightGuide'] or o in branding:o.hide_render=True
 camera((.11,-.15,.21),target=(0,0,.015));render('04_internal_architecture',samples=128)
 reset()
 for o in parts:
  if o.name in ['RearShell','FrontLid']:assign(o,'glass')
 camera((.14,-.16,.22));render('05_transparent_inspection',samples=128)
 for o in parts:
  if o.name in ['RearShell','FrontLid']:assign(o,material_for(o.name))
 reset();floor.hide_render=True;scene.render.film_transparent=True
 # Display-only longitudinal section. Native imported engineering meshes remain untouched.
 bpy.ops.mesh.primitive_cube_add(size=1,location=(.5,0,0));cutter=bpy.context.object;cutter.name='Display-only section halfspace';cutter.scale=(1,2,2);cutter.hide_render=True
 section=[]
 for o in parts:
  o.hide_render=True
  if o.type!='MESH':continue
  dup=o.copy();dup.data=o.data.copy();scene.collection.objects.link(dup);dup.hide_render=False;dup.name='Section / '+o.name
  m=dup.modifiers.new('Display-only half-section','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter;section.append(dup)
 camera((.19,-.15,.2),(0,0,.024),.16);render('08_section_raw',samples=128)
 for o in section+[cutter]:bpy.data.objects.remove(o,do_unlink=True)
 reset();explode();floor.hide_render=True;scene.render.film_transparent=True;camera((.17,-.27,.2),(0,0,.04),.28);render('06_exploded_raw',(2400,2600),128)
 if MODE=='technical_preview':sys.exit(0)
 reset();floor.hide_render=True;scene.render.film_transparent=True;scene.render.engine='CYCLES'
 for name,pos in [('front',(0,0,.3)),('rear',(0,0,-.3)),('left',(-.3,0,.0175)),('right',(.3,0,.0175)),('top',(0,.3,.0175)),('bottom',(0,-.3,.0175))]:
  camera(pos,(0,0,.0175),.13);rear_light.hide_render=name=='front';render('view_'+name,(1400,1400),96);rear_light.hide_render=True
 save_export()
if MODE in ('animation','all'):
 reset()
 # Render-only rigid-layer batching keeps identical geometry and improves CPU viewport throughput.
 # Main .blend and GLB remain individually selectable. The animation source records every member.
 layers={}
 for o in parts:
  z=explosion_mm(o)
  layers.setdefault(z,[]).append(o)
 animated=[]
 for z,items in sorted(layers.items()):
  names=[o.name for o in items];bpy.ops.object.select_all(action='DESELECT')
  for o in items:o.select_set(True)
  bpy.context.view_layer.objects.active=items[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();o=bpy.context.object;o.name='Rigid layer / '+str(z)+' mm';o['source_members']=json.dumps(names);meta[o.name]={'presentation_explode_mm':z};animated.append(o)
 parts=animated;electronics=[];branding=[];basepos={o.name:o.location.copy() for o in parts}
 floor.hide_render=True;workbench();scene.render.resolution_x=1280;scene.render.resolution_y=1280
 scene.render.fps=24;scene.frame_start=1;scene.frame_end=192
 for frame,f in [(1,0),(36,0),(90,1),(120,1),(174,0),(192,0)]:
  explode(f)
  for o in parts:o.keyframe_insert(data_path='location',frame=frame)
  ang=math.radians(-50+(frame-1)*.45);camera((.22*math.cos(ang),.22*math.sin(ang),.23),(0,0,.022+.0155*f),.28)
  cam.keyframe_insert(data_path='location',frame=frame);cam.keyframe_insert(data_path='rotation_euler',frame=frame)
 framing={}
 for frame in [1,36,60,90,120,150,174,192]:
  scene.frame_set(frame);qs=[world_to_camera_view(scene,cam,o.matrix_world@Vector(c)) for o in parts for c in o.bound_box]
  framing[str(frame)]={'min_xy':[min(q[i] for q in qs) for i in range(2)],'max_xy':[max(q[i] for q in qs) for i in range(2)]}
 (OUT/'animation/framing_validation.json').write_text(json.dumps(framing,indent=2))
 if any(min(v['min_xy'])<.025 or max(v['max_xy'])>.975 for v in framing.values()):raise RuntimeError('Animation framing guard: part would approach edge')
 frames=OUT/'animation/frames';frames.mkdir(parents=True,exist_ok=True)
 scene.render.image_settings.file_format='PNG';scene.render.filepath=str(frames/'frame_')
 scene.frame_set(1);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'carbonmirror_animation.blend'),compress=True);bpy.ops.render.render(animation=True)
 subprocess.run(['ffmpeg','-y','-framerate','24','-i',str(frames/'frame_%04d.png'),'-vf',"drawtext=fontfile=/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc:text='碳镜校园  /  ASSEMBLY STUDY':fontsize=32:fontcolor=0x173c40:x=55:y=45,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='ENGINEERING DEVELOPMENT  •  VERIFICATION PENDING':fontsize=19:fontcolor=0x526d6e:x=55:y=1220",'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'animation/carbonmirror_exploded.mp4')],check=True)

print('STUDIO COMPLETE',MODE)
