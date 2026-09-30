from pathlib import Path
import json,hashlib,re,subprocess,shutil,datetime,os
R=Path(__file__).resolve().parents[1];V=R/'validation';H=V/'history';H.mkdir(exist_ok=True)
for f in V.glob('*.rpt'):
 if f.name not in ('erc.rpt','drc.rpt','final_erc.rpt','final_drc.rpt'):
  dest=H/f.name
  if dest.exists():dest=H/(f.stem+'_'+str(int(f.stat().st_mtime))+f.suffix)
  f.rename(dest)
# Preserve any previous canonical DRC snapshot before replacing it.
for name in('final_drc.rpt','final_erc.rpt'):
 f=V/name
 if f.exists():shutil.copy2(f,H/(f.stem+'_'+str(int(f.stat().st_mtime))+'.rpt'))
def run(args):subprocess.run(args,cwd=R,check=True,stdout=subprocess.DEVNULL)
run(['kicad-cli','pcb','drc',str(R/'integrated.kicad_pcb'),'-o',str(V/'final_drc.rpt')])
run(['kicad-cli','sch','erc',str(R/'integrated.kicad_sch'),'-o',str(V/'final_erc.rpt')])
for script in('verify_schematic.py','audit_pcb_pins.py','audit_isolation.py'):run(['/usr/bin/python3',str(R/'scripts'/script)])
for a,z in [('pcb_pin_audit.json','final_pin_audit.json'),('projected_isolation.json','final_isolation.json'),('independent_schematic_checks.json','final_source_graph.json')]:shutil.copyfile(V/a,V/z)
shutil.copyfile(V/'final_drc.rpt',V/'drc.rpt');shutil.copyfile(V/'final_erc.rpt',V/'erc.rpt')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();board=R/'integrated.kicad_pcb';d=(V/'final_drc.rpt').read_text();e=(V/'final_erc.rpt').read_text();counts={k:int(re.search(r'Found (\d+) '+re.escape(label),d)[1])for k,label in [('violations','DRC violations'),('unconnected','unconnected pads'),('footprint_errors','Footprint errors')]};erc=re.search(r'ERC messages: (\d+)  Errors (\d+)  Warnings (\d+)',e);iso=json.loads((V/'final_isolation.json').read_text());pin=json.loads((V/'final_pin_audit.json').read_text());native=json.loads((V/'rule_controls/result.json').read_text());negative=json.loads((V/'rule_controls/projected_negative.json').read_text())
assert not any(counts.values()) and all(int(v)==0 for v in erc.groups()) and iso['pass'] and pin['status']=='PASS' and native['pass'] and not negative['pass']
summary={'status':'DIGITAL CHECKS PASS / DEVELOPMENT HOLD','generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'board_sha256':sha(board),'rules_sha256':sha(board.with_suffix('.kicad_dru')),'schematic_files_sha256':{p.name:sha(p)for p in sorted(R.glob('*.kicad_sch'))},'main_electrical_items':101,'physical_component_bodies':99,'zero_height_test_pads':2,'mechanical_mounting_footprints':4,'main_numbered_pad_keys':pin['numbered_pad_keys'],'assembly_numbered_terminals':348,'layer_count':4,'native_DRC':counts,'ERC':{'messages':int(erc[1]),'errors':int(erc[2]),'warnings':int(erc[3])},'projected_isolation':{'minimum_mm':iso['minimum_mm'],'limiting_pair':iso['minimum_pair'],'routing_items_below_8p4_mm':len(iso['routing_margin_below_8p4']),'scope':iso['basis']},'negative_controls':{'native_supported_rule_rejects_6mm_gap':native['supported']['expected_rule_reported'],'old_unsupported_rule_did_not_reject_6mm_gap':not native['unsupported']['expected_rule_reported'],'independent_checker_rejects_shifted_hot_pad':not negative['pass']},'authoritative_reports':['final_drc.rpt','final_erc.rpt','final_pin_audit.json','final_isolation.json','final_source_graph.json'],'not_proven':['manufactured clearances/creepage and insulation','16 A continuous thermal rating or motor/inrush switching suitability','fuse total-clearing coordination and fault containment','measurement accuracy/calibration, EMC, RF, production reliability','physical thermal response and sensor/fault coverage','certification or permission to fabricate/energize']}
(V/'final_summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
