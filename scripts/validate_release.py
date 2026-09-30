"""Non-destructive digital artifact checks. Not electrical safety validation."""
from pathlib import Path
import json, struct, subprocess, sys, re, hashlib
R=Path(__file__).resolve().parents[1]
checks=[]
def check(name, ok, detail=''):
 checks.append({'check':name,'passed':bool(ok),'detail':detail})
for folder,pattern in [('mechanical','*.FCStd'),('mechanical/step','*.step'),('mechanical/meshes','*.stl'),('electronics','*.kicad_sch'),('electronics','*.kicad_pcb'),('visuals','*.blend'),('visuals/exports','*.glb'),('visuals/animation','*.mp4')]:
 files=list((R/folder).glob(pattern));check(folder+'/'+pattern,bool(files) and all(p.stat().st_size>0 for p in files),str(len(files))+' files')
v=R/'mechanical/validation.json'
if v.exists():
 d=json.loads(v.read_text());check('mechanical solid validity',d.get('all_shapes_valid') and d.get('all_single_solid'),json.dumps(d,ensure_ascii=False))
 check('no unintended mechanical intersections',not any(not x.get('intentional') for x in d.get('intersections',[])))
iv=R/'mechanical/integration_validation.json'
if iv.exists():
 d=json.loads(iv.read_text()); check('native CAD reload',d.get('fcstd_reload_valid',False))
 check('CAD parameter recompute',d.get('native_parameter_edit_88_90_88',False))
 check('PCB body fit',not d.get('pcb_body_interferences',[]))
 bad=[x for x in d.get('component_envelope_interferences',[]) if not x.get('intentional_terminal_entry',False)]
 check('component envelope fit',not bad,json.dumps(bad,ensure_ascii=False))
 check('insertion corridors',not any(not x.get('intentional_closed_shutter') for x in d.get('insertion_keepout_interferences',[])))
erc=R/'electronics/validation/erc.rpt'
if erc.exists():
 t=erc.read_text(); check('KiCad ERC report',bool(re.search(r'Errors\s+0\s+Warnings\s+0',t)),t[-300:])
drc=R/'electronics/validation/drc.rpt'
if drc.exists():
 t=drc.read_text(); match=re.search(r'Found (\d+) DRC violations',t)
 check('KiCad geometric DRC',match is not None and int(match.group(1))==0,match.group(0) if match else 'not parsed')
 # Missing connections are a separately disclosed engineering hold, never a certification pass.
 summary=json.loads((R/'electronics/validation/final_summary.json').read_text())
 check('fabrication hold retained',summary.get('release_status')=='FABRICATION_HOLD','Electrical completion not inferred from geometric DRC.')
 check('low-voltage connectivity',summary.get('lv_unconnected')==0,'Mains unconnected count: '+str(summary.get('mains_unconnected')))
 check('canonical board hash',hashlib.sha256((R/'electronics/carbentra.kicad_pcb').read_bytes()).hexdigest()==summary.get('board_sha256'))
 pin=json.loads((R/'electronics/validation/net_pin_consistency.json').read_text())
 check('schematic to PCB pin-net consistency',pin.get('status')=='PASS' and not pin.get('errors'),str(pin.get('assigned_pins_checked'))+' assigned pins')
 sysfit=json.loads((R/'mechanical/system_fit_validation.json').read_text())
 check('full exported ECAD solid fit',all(x.get('intended_terminal_entry') for x in sysfit['intersections']),str(sysfit.get('electronic_solids'))+' electronic solids')
for name in ['01_hero_ivory','02_hero_detail','03_rear_interface','04_internal_architecture','05_transparent_inspection','06_exploded_raw','07_six_view_sheet','08_section_raw','09_pcb_assembly']:
 p=R/'visuals/renders'/f'{name}.png'
 check('required render '+name,p.exists() and p.stat().st_size>1000)
for p in (R/'visuals/exports').glob('*.glb'):
 data=p.read_bytes();magic,version,length=struct.unpack('<4sII',data[:12]);check('GLB header '+p.name,magic==b'glTF' and version==2 and length==len(data))
 ln,kind=struct.unpack('<II',data[12:20]);j=json.loads(data[20:20+ln]);check('GLB named meshes '+p.name,len(j.get('meshes',[]))>=54 and len(j.get('nodes',[]))>=54,str(len(j.get('meshes',[])))+' meshes')
for p in (R/'visuals/animation').glob('*.mp4'):
 r=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,width,height','-of','json',str(p)],capture_output=True,text=True)
 check('animation probe '+p.name,r.returncode==0,r.stdout)
r=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(R/'tests/policy'),'-v'],capture_output=True,text=True)
check('policy reference unit tests',r.returncode==0,r.stdout+r.stderr)
out={'scope':'Digital artifact consistency only; no physical/electrical certification','release_for_fabrication':False,'passed':all(c['passed'] for c in checks),'checks':checks}
(R/'release/digital_checks.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False,indent=2));sys.exit(0 if out['passed'] else 1)
