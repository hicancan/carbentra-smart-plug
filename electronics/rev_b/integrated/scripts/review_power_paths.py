#!/usr/bin/python3
"""Read separate audit boards; calculate geometry-based loss, not certified ampacity."""
from pathlib import Path
import os,json,math,hashlib,ast,unittest
R=Path(__file__).resolve().parents[1]
for d in ['CONFIG','CACHE','DATA']:os.environ['XDG_'+d+'_HOME']=str(R/'.xdg'/d.lower())
import pcbnew as p
rho=.017241 # mOhm mm at20C
thickness=.070
alpha=.00393
xy=lambda v:[round(p.ToMM(v.x),5),round(p.ToMM(v.y),5)]
def resistance(length,width):return rho*length/(width*thickness)
def barrel(n,plating_um=20):return rho*1.6/(math.pi*.4*(plating_um/1000)*n)
def read(stem):
 raw=(R/(stem+'.kicad_pcb')).read_bytes();b=p.LoadBoard(str(R/(stem+'.kicad_pcb')));groups={n:[] for n in ['HOT_GND_F','HOT_GND_B_parallel','HOT_LOAD_B','HOT_LOAD_F_parallel','HOT_SWITCHED_F','HOT_SWITCHED_B_parallel','HOT_N_B','AUX_PREFUSE_B']}
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA) or p.ToMM(t.GetWidth())<1:continue
  net=t.GetNetname();layer=b.GetLayerName(t.GetLayer());a,z=xy(t.GetStart()),xy(t.GetEnd());key=net+'_'+('F' if layer=='F.Cu' else 'B')
  if net=='HOT_GND' and layer=='B.Cu':key='AUX_PREFUSE_B' if max(a[0],z[0])<=28.5 and min(a[1],z[1])>=62 else 'HOT_GND_B_parallel'
  if net=='HOT_LOAD' and layer=='F.Cu':key='HOT_LOAD_F_parallel'
  if net=='HOT_SWITCHED' and layer=='B.Cu':key='HOT_SWITCHED_B_parallel'
  if key in groups:
   length=p.ToMM(t.GetLength());width=p.ToMM(t.GetWidth());groups[key].append({'start':a,'end':z,'width_mm':width,'layer':layer,'length_mm':length,'R20_mOhm':resistance(length,width)})
 sums={k:{'length_mm':sum(t['length_mm'] for t in v),'R20_mOhm':sum(t['R20_mOhm'] for t in v),'segments':v} for k,v in groups.items()}
 r={k:v['R20_mOhm'] for k,v in sums.items()};gnd=r['HOT_GND_F']
 if r['HOT_GND_B_parallel']:gnd=1/(1/gnd+1/(r['HOT_GND_B_parallel']+barrel(6)))
 load=r['HOT_LOAD_B']+barrel(8);sw=r['HOT_SWITCHED_F'];neck= resistance(7.5,2.4)
 if r['HOT_LOAD_F_parallel']:load-=neck-(1/(1/neck+1/r['HOT_LOAD_F_parallel']))
 if r['HOT_SWITCHED_B_parallel']:sw-=neck-(1/(1/neck+1/r['HOT_SWITCHED_B_parallel']))
 nets={'line_input_to_shunt':gnd,'shunt_to_relay_far_pad':load,'relay_far_pad_to_output':sw,'neutral':r['HOT_N_B']};total=sum(nets.values());optional_neck=neck*(.5 if r['HOT_LOAD_F_parallel'] else 1)+neck*(.5 if r['HOT_SWITCHED_B_parallel'] else 1)
 return {'board_sha256':hashlib.sha256(raw).hexdigest(),'groups':sums,'effective_path_R20_mOhm':nets,'far_pad_total_R20_mOhm':total,'near_pad_alternative_R20_mOhm':total-optional_neck,'far_pad_total_loss_W_at16A':16**2*total/1000,'near_pad_alternative_loss_W_at16A':16**2*(total-optional_neck)/1000,'far_pad_voltage_drop_V_at16A':16*total/1000,'via_array_R20_mOhm_at20um':{'output8vias':barrel(8),'added_input6vias':barrel(6) if r['HOT_GND_B_parallel'] else None},'aux_prefuse_loss_W_at_0p1A':.1**2*r['AUX_PREFUSE_B']/1000}
baseline=read('integrated_power_baseline');candidate=read('integrated_power_candidate');out={'assumptions':{'resistivity_ohm_m_20C':1.7241e-8,'outer_copper_nominal_mm':.070,'inner_copper_nominal_mm':.035,'finished_copper_is_guaranteed':False,'copper_temperature_coefficient_per_K':alpha,'barrel_plating_model_um':20,'array_sharing':'ideal equal sharing; solder/pad spreading/contact resistance excluded','full_length_model':'16A along every series segment to far duplicated relay pads; actual internal relay/pin sharing unmeasured','near_pad_alternative':'omit7.5mm inter-pin trace legs; not a rigorous lower bound on complete assembly loss'},'baseline':baseline,'candidate':candidate,'nominal_far_pad_reduction_percent':100*(1-candidate['far_pad_total_R20_mOhm']/baseline['far_pad_total_R20_mOhm']),'temperature_sensitivity':[],'auxiliary_prefuse_is_not_protected_by_F501':True,'fuse_total_clearing_I2t':'UNKNOWN:760A2s is typical melting at10xIn only; no clearing-energy bound inferred'}
for t in [20,60,100]:out['temperature_sensitivity'].append({'copper_C':t,'factor':1+alpha*(t-20),'baseline_far_pad_W':baseline['far_pad_total_loss_W_at16A']*(1+alpha*(t-20)),'candidate_far_pad_W':candidate['far_pad_total_loss_W_at16A']*(1+alpha*(t-20))})
out['via_array_plating_sensitivity']=[{'plating_um':v,'output_8via_R_mOhm':barrel(8,v),'input_6via_R_mOhm':barrel(6,v)} for v in [15,20,25]]
(R/'validation/power_path_review.json').write_text(json.dumps(out,indent=2), encoding='utf-8', newline='\n');print(json.dumps({k:v for k,v in out.items() if k not in ['baseline','candidate']},indent=2));print('BASE',baseline['effective_path_R20_mOhm'],baseline['far_pad_total_loss_W_at16A']);print('CAND',candidate['effective_path_R20_mOhm'],candidate['far_pad_total_loss_W_at16A'])
# Re-run only the pure ideal logic classes, not the frozen module's file-writing verification.
source=ast.parse((R.parent/'thermal/scripts/verify_thermal.py').read_text(encoding='utf-8'));ns={'unittest':unittest};classes=ast.Module(body=[n for n in source.body if isinstance(n,ast.ClassDef) and n.name in ['Circuit','Tests']],type_ignores=[]);exec(compile(classes,'thermal_logic_tests','exec'),ns)
result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.loadTestsFromTestCase(ns['Tests']));assert result.wasSuccessful()
m=json.loads((R/'electrical_manifest.json').read_text(encoding='utf-8'));parts={c['ref']:c for c in m['components']};pins={k:v['pins'] for k,v in parts.items()}
assert pins['U404']=={'2':'+3V3_ISO','1':'TH_REARM_CLK','6':'TH_THERMAL_READY','5':'TH_COIL_ARMED','3':None,'7':'+3V3_ISO','8':'+3V3_ISO','4':'GND_ISO'}
assert pins['U405']['4']==pins['U404']['1']=='TH_REARM_CLK'
assert pins['SW401']=={'1':'+3V3_ISO','2':'TH_MANUAL_RAW'}
assert pins['Q401']=={'1':'TH_COIL_GATE','3':'COIL_5V','2':'+5V_ISO'}
assert pins['Q402']['3']=='TH_COIL_GATE' and pins['Q402']['2']==pins['Q403']['3']=='TH_SINK_MID' and pins['Q403']['2']=='GND_ISO'
assert pins['K101']['A1']==pins['D101']['1']=='COIL_5V'
assert not any(n and 'REARM' in n for n in pins['U101'].values())
report={'ideal_logic_tests':result.testsRun,'actual_integrated_pin_topology':'PASS','MCU_rearm_path':'ABSENT','held_button_fault_recovery':'No new rising edge in ideal powered logic; fault clear alone cannot arm','hardware_trip_dominance':'DFF async clear and independent series NPN gate-sink block','physical_robustness':'UNPROVEN at sub-threshold supply ramps, component faults, actual thermal coupling, and contact welds','board_linkage':'Independent PCB pin audit separately covers all321 main-board pin keys'}
(R/'validation/integrated_latch_review.json').write_text(json.dumps(report,indent=2), encoding='utf-8', newline='\n');print(json.dumps(report,indent=2))
