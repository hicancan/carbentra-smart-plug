#!/usr/bin/python3
"""Independent integrated KiCad-exported netlist vs manifest check (no PCB access)."""
from pathlib import Path
import re,json,subprocess,os,collections
R=Path(__file__).resolve().parents[1]
def parse(s):
 st=[]
 for t in re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',s):
  if t=='(':
   a=[]
   if st:st[-1].append(a)
   st.append(a)
  elif t==')':root=st.pop()
  else:st[-1].append(json.loads(t) if t.startswith('"') else t)
 return root
def ch(x,k):return next((v for v in x if isinstance(v,list)and v[0]==k),None)
def cs(x,k):return [v for v in x if isinstance(v,list)and v[0]==k]
subprocess.run(['kicad-cli','sch','erc',str(R/'integrated.kicad_sch'),'--format','json','-o',str(R/'validation/erc.json')],check=True)
erc=json.loads((R/'validation/erc.json').read_text(encoding='utf-8'))
assert not [v for sheet in erc['sheets'] for v in sheet['violations']],erc
subprocess.run(['kicad-cli','sch','export','netlist',str(R/'integrated.kicad_sch'),'-o',str(R/'exports/integrated.net')],check=True)
m=json.loads((R/'electrical_manifest.json').read_text(encoding='utf-8'));expected={(c['ref'],pin):n for c in m['components'] if c['board_designation'] not in ['harness_model','off_board_assembly'] for pin,n in c['pins'].items()};actual={};scoped={}
for net in cs(ch(parse((R/'exports/integrated.net').read_text(encoding='utf-8')),'nets'),'net'):
 raw=ch(net,'name')[1]
 if raw.startswith('unconnected-'):name=None
 elif raw.endswith('/HOT_NC'):name='HOT_NC';scoped[name]=raw
 else:name=raw.lstrip('/')
 for nd in cs(net,'node'):actual[(ch(nd,'ref')[1],ch(nd,'pin')[1])]=name
errors=[{'ref':k[0],'pin':k[1],'expected':v,'actual':actual.get(k,'MISSING')} for k,v in expected.items() if actual.get(k,'MISSING')!=v]
extra=[{'ref':k[0],'pin':k[1],'net':v} for k,v in actual.items() if k not in expected]
(R/'validation/pin_net_check.json').write_text(json.dumps({'pin_count':len(expected),'errors':errors,'extra_nodes':extra,'scoped_named_nets':scoped},indent=2), encoding='utf-8', newline='\n')
assert not errors and not extra,(errors,extra)
checks={('J201','1'):'HOT_GND',('J201','2'):'HOT_N',('RS201','1'):'HOT_GND',('RS201','4'):'HOT_LOAD',('K101','11'):'HOT_LOAD',('K101','14'):'HOT_SWITCHED',('J102','1'):'HOT_SWITCHED',('J102','2'):'HOT_N',('F501','1'):'HOT_GND',('F501','2'):'HOT_AUX_FUSED',('PS101','2'):'HOT_AUX_FUSED',('U301','6'):'OUTPUT_PRESENT_N',('U101','15'):'OUTPUT_PRESENT_N',('Y201','3'):'HOT_XIN',('Y201','4'):'HOT_3V3',('U201','22'):'HOT_XIN',('U201','23'):None,('CX201','1'):'HOT_3V3',('CX201','2'):'HOT_GND',('Q401','3'):'COIL_5V',('K101','A1'):'COIL_5V',('D101','1'):'COIL_5V',('U404','6'):'TH_THERMAL_READY'}
for key,value in checks.items():assert actual[key]==value,(key,actual[key],value)
assert 'CX202' not in {c['ref'] for c in m['components']}
assert not any(v and 'MCU_REARM' in v for v in actual.values())
assert {c['ref'] for c in m['components'] if c['board_designation']=='remote_sensor'}=={'U401','R401','C401','J404'}
report={'status':'PASS','ERC':{'errors':0,'warnings':0},'numbered_pins_checked':len(expected),'physical_component_count':sum(c['board_designation']!='harness_model' for c in m['components']),'off_board_assembly_components':4,'main_components':sum(c['board_designation']=='integrated' for c in m['components']),'remote_sensor_components':4,'critical_connections_checked':len(checks),'ASV_pin_map':{p:actual[('Y201',p)] for p in ['1','2','3','4']},'scoped_named_nets':scoped,'footprint_and_PCB_verification':'Parent owns integrated PCB; not evaluated by this script','fabrication_release':'HOLD'}
(R/'validation/independent_schematic_checks.json').write_text(json.dumps(report,indent=2), encoding='utf-8', newline='\n');print(json.dumps(report,indent=2))

m['status']='ELECTRICAL SOURCE VERIFIED: ERC 0/0; 334 numbered pins match; PCB/fabrication/energization release HOLD';m['electrical_validation']={'report':'validation/independent_schematic_checks.json','ERC_errors':0,'ERC_warnings':0,'numbered_pins_checked':len(expected),'critical_connections_checked':len(checks)}
tmp=R/'electrical_manifest.json.tmp';tmp.write_text(json.dumps(m,indent=2), encoding='utf-8', newline='\n');tmp.replace(R/'electrical_manifest.json')

# KiCad PCB netlists correctly omit on_board=false parts. A throwaway validation copy includes
# them only for full-assembly/harness graph export; canonical source/board flags stay unchanged.
import shutil
scratch=R/'validation/full_graph';scratch.mkdir(exist_ok=True)
def serial(x):return '('+' '.join(serial(v) for v in x)+')' if isinstance(x,list) else json.dumps(x) if isinstance(x,str) and (not re.fullmatch(r'[^\s()";]+',x) or x in ['']) else str(x)
# Preserve original token spelling to avoid changing KiCad grammar atoms.
def parse_tokens(s):
 st=[]
 for t in re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',s):
  if t=='(':
   a=[]
   if st:st[-1].append(a)
   st.append(a)
  elif t==')':root=st.pop()
  else:st[-1].append(t)
 return root
def stokens(x):return '('+' '.join(stokens(v) for v in x)+')' if isinstance(x,list) else x
include={c['ref'] for c in m['components'] if c['board_designation'] in ['harness_model','off_board_assembly']}
for src in R.glob('integrated*.kicad_sch'):
 tree=parse_tokens(src.read_text(encoding='utf-8'))
 for sym in cs(tree,'symbol'):
  ref=next((json.loads(v[2]) for v in cs(sym,'property') if v[1]=='"Reference"'),None)
  if ref in include:ch(sym,'on_board')[1]='yes'
 (scratch/src.name).write_text(stokens(tree), encoding='utf-8', newline='\n')
fullfile=R/'validation/full_assembly_graph.net'
subprocess.run(['kicad-cli','sch','export','netlist',str(scratch/'integrated.kicad_sch'),'-o',str(fullfile)],check=True)
whole={};scoped={}
for net in cs(ch(parse(fullfile.read_text(encoding='utf-8')),'nets'),'net'):
 raw=ch(net,'name')[1];n=None if raw.startswith('unconnected-') else raw.lstrip('/')
 if n and n.split('/')[-1] in ['PE','RAW_L','HOT_TF_IN']:scoped[n.split('/')[-1]]=raw;n=n.split('/')[-1]
 for nd in cs(net,'node'):whole[(ch(nd,'ref')[1],ch(nd,'pin')[1])]=n
want={(c['ref'],pn):n for c in m['components'] for pn,n in c['pins'].items()}
assert whole==want,([(k,v,whole.get(k)) for k,v in want.items() if whole.get(k)!=v],[k for k in whole if k not in want])
for k,v in {('J601','1'):'RAW_L',('F601','1'):'RAW_L',('F601','2'):'HOT_TF_IN',('TF601','1'):'HOT_TF_IN',('TF601','2'):'HOT_GND',('J601','2'):'HOT_N',('J602','2'):'HOT_N',('J602','1'):'HOT_SWITCHED',('J601','3'):'PE',('J602','3'):'PE'}.items():assert whole[k]==v
for c in m['components']:
 if c['board_designation'] in ['integrated','remote_sensor']:assert all(n not in ['PE','RAW_L','HOT_TF_IN'] for n in c['pins'].values())
assert {k for k,n in whole.items() if n=='PE'}=={('J601','3'),('J602','3')}
report['full_assembly_graph_pins_checked']=len(want);report['off_board_terminals_checked']=10;report['harness_model_pins_checked']=4;report['PE_direct_no_PCB_nodes']='PASS';report['assembly_scoped_nets']=scoped
(R/'validation/independent_schematic_checks.json').write_text(json.dumps(report,indent=2), encoding='utf-8', newline='\n');shutil.rmtree(scratch)
m['status']='ELECTRICAL SOURCE VERIFIED: ERC 0/0; PCB/head and full assembly netlists match; release HOLD';m['electrical_validation'].update(full_assembly_graph_pins_checked=len(want),off_board_terminals_checked=10,PE_direct_no_PCB_nodes=True)
tmp=R/'electrical_manifest.json.tmp';tmp.write_text(json.dumps(m,indent=2), encoding='utf-8', newline='\n');tmp.replace(R/'electrical_manifest.json');print('Full assembly graph:',len(want),'pins; direct PE only between plug/socket verified')
