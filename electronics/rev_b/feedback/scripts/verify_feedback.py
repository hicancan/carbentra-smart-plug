#!/usr/bin/python3
"""Cross-check real KiCad netlist, pads, domain separation and tolerance calculations."""
import json,re,math,itertools,subprocess,os,shutil
from pathlib import Path
import pcbnew as p
R=Path(__file__).resolve().parents[1]
os.environ['XDG_CONFIG_HOME']=str(R/'.xdg/config');os.environ['XDG_CACHE_HOME']=str(R/'.xdg/cache');os.environ['XDG_DATA_HOME']=str(R/'.xdg/data')
def parse(s):
 ts=re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',s);stack=[]
 for t in ts:
  if t=='(':
   a=[]
   if stack:stack[-1].append(a)
   stack.append(a)
  elif t==')':root=stack.pop()
  else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
 return root
def child(x,k):return next(v for v in x if isinstance(v,list) and v[0]==k)
def children(x,k):return [v for v in x if isinstance(v,list) and v[0]==k]
subprocess.run(['kicad-cli','sch','export','netlist',str(R/'output_feedback.kicad_sch'),'-o',str(R/'exports/feedback.net')],check=True)
m=json.loads((R/'pin_net_manifest.json').read_text());expected={(c['ref'],pn):n for c in m['components'] for pn,n in c['pins'].items()};actual={}
for n in children(child(parse((R/'exports/feedback.net').read_text()),'nets'),'net'):
 name=child(n,'name')[1].lstrip('/');name=None if name.startswith('unconnected-') else name
 for node in children(n,'node'):actual[(child(node,'ref')[1],child(node,'pin')[1])]=name
assert actual==expected, {'expected':expected,'actual':actual}
b=p.LoadBoard(str(R/'output_feedback.kicad_pcb'));pads={};domains={'HV':[],'LV':[]};hvnets={'L_POST','N_POST','L_MID','N_MID','AC1','AC2'}
for f in b.GetFootprints():
 for pad in f.Pads():
  key=(f.GetReference(),pad.GetNumber());n=pad.GetNetname() or None;pads[key]=n
  hv=n in hvnets or (f.GetReference()=='U1' and int(pad.GetNumber())<=4)
  domain='HV' if hv else 'LV';bb=pad.GetBoundingBox();domains[domain].append((f.GetReference()+'.'+pad.GetNumber(),p.ToMM(bb.GetLeft()),p.ToMM(bb.GetRight())))
assert pads==expected
for i,t in enumerate(b.GetTracks()):
 if t.GetNetname() not in hvnets and t.GetNetname() not in ['GND_ISO','+3V3_ISO','OUTPUT_PRESENT_N']:raise AssertionError('Unclassified copper')
 domain='HV' if t.GetNetname() in hvnets else 'LV';bb=t.GetBoundingBox();domains[domain].append((f'track/via {i}',p.ToMM(bb.GetLeft()),p.ToMM(bb.GetRight())))
hvmax=max(domains['HV'],key=lambda x:x[2]);lvmin=min(domains['LV'],key=lambda x:x[1]);gap=lvmin[1]-hvmax[2]
assert gap>=8.0,(gap,hvmax,lvmin)
# Negative control proves the custom isolation rule really executes. Add a deliberately isolated primary copper island within 8 mm of LV.
neg=R/'validation/negative_control';nb=p.LoadBoard(str(R/'output_feedback.kicad_pcb'));track=p.PCB_TRACK(nb);track.SetStart(p.VECTOR2I(p.FromMM(22),p.FromMM(10)));track.SetEnd(p.VECTOR2I(p.FromMM(22.2),p.FromMM(10)));track.SetWidth(p.FromMM(.25));track.SetLayer(p.F_Cu);track.SetNet(nb.FindNet('L_POST'));nb.Add(track);p.SaveBoard(str(neg)+'.kicad_pcb',nb)
for ext in ['kicad_pro','kicad_dru']:shutil.copy(R/('output_feedback.'+ext),str(neg)+'.'+ext)
subprocess.run(['kicad-cli','pcb','drc',str(neg)+'.kicad_pcb','-o',str(neg)+'.rpt'],check=True)
negative_report=Path(str(neg)+'.rpt').read_text();assert 'Primary to isolated logic copper' in negative_report,negative_report
for ext in ['kicad_pcb','kicad_pro','kicad_dru']:Path(str(neg)+'.'+ext).unlink()
calc={}
for tol in [.01,.10]:
 rlo=132000*(1-tol);rhi=132000*(1+tol);v_on_max=.00156*rhi+5.5;v_off_max=.0008*rhi+4.42;v_on_min=.00087*rlo+4.23;v_off_min=.00043*rlo+2.87
 vslo=198*math.sqrt(2);vshi=264*math.sqrt(2)
 minlow=(math.pi-math.asin(v_on_max/vslo)-math.asin(v_off_max/vslo))/(2*math.pi*60)
 minhigh=(math.asin(v_on_min/vshi)+math.asin(v_off_min/vshi))/(2*math.pi*60)
 worst={}
 for count in [4,3]:
  scenarios=list(itertools.product([33000*(1-tol),33000*(1+tol)],repeat=count))
  worst[str(count)+'_active_resistors']={'single_resistor_max_W':max(264**2*r/sum(rs)**2 for rs in scenarios for r in rs),'single_resistor_max_Vrms':max(264*r/sum(rs) for rs in scenarios for r in rs),'total_max_W':264**2/(count*33000*(1-tol)),'peak_current_upper_A':264*math.sqrt(2)/(count*33000*(1-tol))}
 calc[str(tol)]={'R_min_ohm':rlo,'R_max_ohm':rhi,'turn_on_max_instantaneous_V':v_on_max,'turn_off_max_instantaneous_V':v_off_max,'turn_on_min_instantaneous_V':v_on_min,'turn_off_min_instantaneous_V':v_off_min,'sine_RMS_crest_threshold_max_V':v_on_max/math.sqrt(2),'ideal_min_low_ms':minlow*1000,'ideal_min_high_ms':minhigh*1000,'peak_threshold_margin_at_198Vac_V':vslo-v_on_max,'resistor_power_voltage':worst}
 assert vslo>v_on_max
assert 'Errors 0  Warnings 0' in (R/'validation/erc.rpt').read_text()
assert '** Found 0 DRC violations **' in (R/'validation/drc.rpt').read_text() and '** Found 0 unconnected pads **' in (R/'validation/drc.rpt').read_text()
out={'pin_net_consistency':'PASS','checked_pins':len(expected),'no_connect_pins_verified':[['U1',x] for x in ['2','3','7']],'clearance_lower_bound_mm':gap,'method':'all-copper x-extents across both layers, includes NC U1 pads; conservative bound, not a regulatory creepage assessment','rightmost_HV_copper':hvmax,'leftmost_LV_copper':lvmin,'custom_8mm_rule_negative_control':'PASS: injected violation identified by named isolation rule','envelope_mm':[35,25,1.6],'calculations':calc,'physical_test_status':'NOT_RUN','certification_status':'NOT_CLAIMED','fabrication_release':'HOLD'}
(R/'validation/independent_checks.json').write_text(json.dumps(out,indent=2));(R/'calculations.json').write_text(json.dumps(calc,indent=2));print(json.dumps(out,indent=2))
