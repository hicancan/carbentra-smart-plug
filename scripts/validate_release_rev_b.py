"""Final CARBENTRA digital-deliverable checks, never hardware certification."""
from pathlib import Path
import hashlib,json,struct,subprocess,sys
R=Path(__file__).resolve().parents[1]; checks=[]
def check(name,ok,detail=''):checks.append({'check':name,'passed':bool(ok),'detail':detail})
def read(rel):
 p=R/rel
 if not p.exists():check('required '+rel,False);return {}
 return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pinned(base,path,meta):
 p=base/path;check('frozen '+str(p.relative_to(R)),p.is_file() and p.stat().st_size==meta['bytes'] and sha(p)==meta['sha256'])
m=read('mechanical/rev_b/freeze_manifest.json')
check('mechanical defined digital checks',m.get('all_defined_digital_checks_pass'))
for f in m.get('files',[]):pinned(R,f['path'],f)
detail=read('mechanical/rev_b/detailed_export_report.json')
if detail.get('output'):pinned(R,detail['output']['path'],detail['output'])
check('detailed STEP valid roundtrip',detail.get('step_roundtrip_all_valid') and detail.get('relative_summed_volume_difference',1)<1e-6)
ebase=R/'electronics/rev_b/integrated'
e=read('electronics/rev_b/integrated/HANDOFF.json')
for path,meta in e.get('files',{}).items():pinned(ebase,path,meta)
f=read('electronics/rev_b/integrated/validation/final_summary.json')
check('canonical native DRC',f.get('native_DRC')=={'violations':0,'unconnected':0,'footprint_errors':0})
check('canonical ERC',f.get('ERC',{}).get('errors')==0 and f.get('ERC',{}).get('warnings')==0)
check('native rule and independent negative controls',f.get('negative_controls') and all(f['negative_controls'].values()))
check('board source hash',f.get('board_sha256')==sha(ebase/'integrated.kicad_pcb'))
check('project-only copper separation',f.get('projected_isolation',{}).get('minimum_mm',0)>=8-1e-6)
fit=read('mechanical/rev_b/integrated_fit_report.json')
check('valid individual geometry',fit.get('mechanical_all_valid') and fit.get('mechanical_all_single_solids'))
check('no unintended mechanical collision',all(x.get('intentional_interface',False) for x in fit.get('mechanical_intersections',[])))
check('no unintended board/lead collision',all(x.get('intentional_terminal_entry',False) for x in fit.get('component_and_lead_intersections',[])))
check('no head collision',not fit.get('head_intersections',[None]))
p=read('mechanical/rev_b/polarity_connectivity_report.json')
check('external modeled joint connectivity',p.get('joint_geometry_pass'))
check('PE one continuous geometric solid',p.get('PE_geometric_valid') and p.get('PE_geometric_fused_solid_count')==1)
interface={x['name']:x for x in p.get('interface_world',[])}
check('front polarity convention',interface.get('L',{}).get('x',0)>0 and interface.get('N',{}).get('x',0)<0)
s=read('mechanical/rev_b/shutter_kinematic_report.json');states={x['state']:x for x in s.get('states',[])}
check('shutter state coverage',len(states)==11)
for name in ['single_L_attempt','single_N_attempt']:check(name+' remains geometrically blocked',bool(states.get(name,{}).get('intersections')))
check('open insertion paths clear',states.get('open_rest') and all(x['blocked_volume_mm3']<1e-6 for x in states['open_rest']['insertion_paths']))
check('spring contact candidate engagement',read('mechanical/rev_b/contact_engagement_report.json').get('geometric_engagement_pass'))
i=read('mechanical/rev_b/insulation_domain_report.json')
check('nominal 3D project screen',i.get('nominal_geometric_screen',{}).get('met_nominally'))
check('insulation inputs stable',not i.get('inputs_changed_during_run',True))
cf=read('visuals/rev_b/exports/common_frame_validation.json')
check('visual common-frame source comparison',cf.get('all_pass') and cf.get('head_aggregate_pass'))
for n in ['01_hero_ivory','02_hero_detail','03_rear_interface','04_internal_architecture','05_transparent_inspection','06_exploded_raw','06_exploded_annotated','07_six_view_sheet','08_section_raw','08_section_annotated','09_pcb_assembly']:
 path=R/'visuals/rev_b/renders'/f'{n}.png';check('render '+n,path.is_file() and path.stat().st_size>1000)
for n in ['carbonmirror_studio.blend','carbonmirror_animation.blend']:
 path=R/'visuals/rev_b'/n;check('native scene '+n,path.is_file() and path.stat().st_size>1000)
for n in ['carbonmirror_assembly.glb','carbonmirror_twin_light.glb']:
 path=R/'visuals/rev_b/exports'/n
 if not path.exists():check('GLB '+n,False);continue
 data=path.read_bytes();header=struct.unpack('<4sII',data[:12]);check('GLB structure '+n,header==(b'glTF',2,len(data)))
 length,kind=struct.unpack('<II',data[12:20]);j=json.loads(data[20:20+length]);check('GLB nodes '+n,len(j.get('nodes',[]))>=10)
gi=read('release/light_glb_import_check.json')
check('actual Blender light GLB import',gi.get('import_pass') and gi.get('sha256')==sha(R/'visuals/rev_b/exports/carbonmirror_twin_light.glb'))
movie=R/'visuals/rev_b/animation/carbonmirror_exploded.mp4'
if movie.exists():
 r=subprocess.run(['ffprobe','-v','error','-count_frames','-show_entries','format=duration:stream=codec_name,width,height,avg_frame_rate,nb_read_frames','-of','json',str(movie)],capture_output=True,text=True)
 d=json.loads(r.stdout) if r.returncode==0 else {};v=d.get('streams',[{}])[0]
 check('actual144-frame24fps animation',r.returncode==0 and v.get('avg_frame_rate')=='24/1' and int(v.get('nb_read_frames','0'))==144 and abs(float(d.get('format',{}).get('duration',0))-6)<.1,r.stdout)
else:check('actual animation',False)
for cmd,label in [([sys.executable,'scripts/validate_firmware_evidence.py'],'firmware evidence'),([sys.executable,'-m','unittest','discover','-s','edge/tests'],'edge tests'),([sys.executable,'-m','unittest','discover','-s','tests/policy'],'policy reference tests')]:
 r=subprocess.run(cmd,cwd=R,capture_output=True,text=True);check(label,r.returncode==0,r.stdout+r.stderr)
review=R/'release/CARBENTRA_RevB_Design_Review_CN.pdf';check('final Chinese review PDF',review.is_file() and review.stat().st_size>1000)
pq=read('release/review_pdf_qa.json')
check('final PDF visual QA and hash',pq.get('passed') and pq.get('all_pages_rendered_and_contact_sheet_visually_reviewed') and pq.get('sha256')==sha(review))
out={'product':'CARBENTRA','revision':'CM-S16-EVT-B','scope':'Frozen digital consistency and software checks only; no physical/electrical certification','release_for_fabrication':False,'release_for_energization':False,'passed':all(c['passed'] for c in checks),'checks':checks}
(R/'release/digital_checks_rev_b.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'passed':out['passed'],'check_count':len(checks),'failures':[c['check'] for c in checks if not c['passed']]},ensure_ascii=False,indent=2));sys.exit(0 if out['passed'] else 1)
