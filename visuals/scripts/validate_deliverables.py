"""Validate final studio deliverables and write machine-readable release inventory."""
from pathlib import Path
from PIL import Image
import hashlib,json,struct,subprocess,os
V=Path(os.environ.get('CM_OUTPUT_DIR',str(Path(__file__).resolve().parents[1])));R=Path(os.environ.get('CM_PROJECT_ROOT',str(V.parent)))
names=['carbonmirror_studio.blend','carbonmirror_animation.blend','exports/carbonmirror_assembly.glb','exports/carbonmirror_twin_light.glb','animation/carbonmirror_exploded.mp4','renders/01_hero_ivory.png','renders/02_hero_detail.png','renders/03_rear_interface.png','renders/04_internal_architecture.png','renders/05_transparent_inspection.png','renders/06_exploded_annotated.png','renders/07_six_view_sheet.png','renders/08_section_annotated.png','renders/09_pcb_annotated.png']
entries=[]
for n in names:
 p=V/n;assert p.exists() and p.stat().st_size>0,n
 item={'file':n,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 if p.suffix=='.png':
  with Image.open(p) as im:item['pixels']=list(im.size);im.verify()
  assert min(item['pixels'])>=2000,n
 entries.append(item)
b=(V/'exports/carbonmirror_assembly.glb').read_bytes();magic,ver,total=struct.unpack_from('<III',b);assert magic==0x46546c67 and ver==2 and total==len(b)
l,t=struct.unpack_from('<II',b,12);g=json.loads(b[20:20+l]);nodes={o.get('name') for o in g['nodes']};mech=json.loads(Path(os.environ.get('CM_MECHANICAL_DIR',str(R/'mechanical')),'parts_manifest.json').read_text());assert all(o['id'] in nodes for o in mech['parts'] if o.get('render_default',True) is not False and o.get('geometry_role')!='clearance_envelope')
report={'status':'Engineering development; verification pending','deliverables':entries,'glb_nodes':len(g['nodes']),'glb_meshes':len(g['meshes']),'all_mechanical_source_ids_present':True,'video':json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height,r_frame_rate,nb_frames:format=duration','-of','json',str(V/'animation/carbonmirror_exploded.mp4')]))}
stream=report['video']['streams'][0];assert stream['width']>=1080 and stream['height']>=1080 and stream['r_frame_rate']=='24/1';assert int(stream['nb_frames'])==int(os.environ.get('CM_ANIMATION_FRAMES','144'))
iv=json.loads((V/'exports/import_validation.json').read_text());assert iv['source_sha256']['mechanical_manifest']==hashlib.sha256(Path(iv['mechanical_source']).read_bytes()).hexdigest();assert iv['source_sha256']['electronics_obj']==hashlib.sha256(Path(iv['electronic_source']).read_bytes()).hexdigest()
for item in iv.get('electronic_inputs',[]):assert item['sha256']==hashlib.sha256(Path(item['file']).read_bytes()).hexdigest()
report['current_source_hashes_match']=True
report['nonphysical_envelopes_excluded']=iv.get('excluded_nonphysical_envelopes',[])
report['light_model_validation']=json.loads((V/'exports/light_glb_ready.json').read_text())
(V/'exports/deliverables_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='deliverables'},ensure_ascii=False,indent=2))
