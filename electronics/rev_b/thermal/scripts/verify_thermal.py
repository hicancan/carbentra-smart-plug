#!/usr/bin/python3
"""Validate actual schematic connectivity and discrete ideal logic. No analog/safety claims."""
import json,re,subprocess,os,unittest,math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def parse(s):
 stack=[]
 for t in re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',s):
  if t=='(':
   a=[]
   if stack:stack[-1].append(a)
   stack.append(a)
  elif t==')':root=stack.pop()
  else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
 return root
def children(x,k):return [v for v in x if isinstance(v,list) and v[0]==k]
def child(x,k):return next(v for v in x if isinstance(v,list) and v[0]==k)
for d in ['CONFIG','CACHE','DATA']:os.environ['XDG_'+d+'_HOME']=str(R/'.xdg'/d.lower())
subprocess.run(['kicad-cli','sch','export','netlist',str(R/'thermal_interlock.kicad_sch'),'-o',str(R/'exports/thermal.net')],check=True)
m=json.loads((R/'pin_net_manifest.json').read_text(encoding='utf-8'));expected={(c['ref'],pn):n for c in m['components'] if not c['ref'].startswith('W') for pn,n in c['pins'].items()};actual={}
for n in children(child(parse((R/'exports/thermal.net').read_text(encoding='utf-8')),'nets'),'net'):
 name=child(n,'name')[1].lstrip('/');name=None if name.startswith('unconnected-') else name
 for nd in children(n,'node'):actual[(child(nd,'ref')[1],child(nd,'pin')[1])]=name
assert expected==actual,[(k,expected[k],actual.get(k)) for k in expected if expected[k]!=actual.get(k)]
# Explicit independently transcribed critical pin checks against manufacturer tables.
assert {p:expected[('U4',p)] for p in map(str,range(1,9))}=={'1':'REARM_CLK','2':'+3V3_ISO','3':None,'4':'GND_ISO','5':'COIL_ARMED','6':'THERMAL_READY','7':'+3V3_ISO','8':'+3V3_ISO'}
assert {p:expected[('Q1',p)] for p in ['1','2','3']}=={'1':'COIL_GATE','2':'+5V_ISO','3':'COIL_5V'}
assert expected[('U3','1')]=='READY_RAW' and expected[('U6','4')]=='THERMAL_READY' and expected[('U3','3')]=='HEALTH_VALID' and expected[('U3','4')]=='CT_SELECT'
assert not any(n and 'MCU_REARM' in n for n in expected.values())
# This small transition model is the intended hardware truth behavior after component supply/timing conditions are valid.
class Circuit:
 def __init__(self,delay_ms=300):self.delay=delay_ms;self.healthy_since=None;self.ready=False;self.q=False;self.prev_clk=False
 def step(self,t,power_ok=True,thermal_ok=True,rearm=False,relay_cmd=False,forced_q=None):
  healthy=power_ok and thermal_ok
  if not healthy:self.healthy_since=None;self.ready=False
  else:
   if self.healthy_since is None:self.healthy_since=t
   self.ready=t-self.healthy_since>=self.delay
  edge=rearm and not self.prev_clk
  if not self.ready:self.q=False
  elif edge:self.q=True
  self.prev_clk=rearm
  permission=(self.q if forced_q is None else forced_q) and self.ready
  return permission and relay_cmd
class Tests(unittest.TestCase):
 def ready(self):c=Circuit();c.step(0);c.step(421);return c
 def test_powerup_off_even_cmd_high(self):
  c=Circuit();self.assertFalse(c.step(0,relay_cmd=True));self.assertFalse(c.step(500,relay_cmd=True));self.assertFalse(c.q)
 def test_manual_press_after_ready(self):c=self.ready();self.assertTrue(c.step(500,rearm=True,relay_cmd=True))
 def test_thermal_fault_dominates_reset_edge(self):c=self.ready();self.assertFalse(c.step(500,thermal_ok=False,rearm=True,relay_cmd=True));self.assertFalse(c.q)
 def test_trip_clears_prior_arm(self):c=self.ready();c.step(500,rearm=True);self.assertFalse(c.step(501,thermal_ok=False,relay_cmd=True))
 def test_cooling_never_auto_rearms(self):
  c=self.ready();c.step(500,rearm=True);c.step(501,thermal_ok=False,rearm=False);c.step(600);self.assertFalse(c.step(1100,relay_cmd=True));self.assertFalse(c.q)
 def test_button_held_through_trip_and_recovery(self):
  c=self.ready();c.step(500,rearm=True);c.step(501,thermal_ok=False,rearm=True);c.step(600,rearm=True);self.assertFalse(c.step(1100,rearm=True,relay_cmd=True));c.step(1200,rearm=False);self.assertTrue(c.step(1300,rearm=True,relay_cmd=True))
 def test_button_held_from_powerup(self):
  c=Circuit();c.step(0,rearm=True);self.assertFalse(c.step(500,rearm=True,relay_cmd=True))
 def test_brownout_erases_arm(self):c=self.ready();c.step(500,rearm=True);self.assertFalse(c.step(501,power_ok=False,relay_cmd=True));c.step(600);self.assertFalse(c.step(1100,relay_cmd=True))
 def test_broken_return_fail_low_input(self):c=self.ready();c.step(500,rearm=True);self.assertFalse(c.step(501,thermal_ok=False,relay_cmd=True))
 def test_live_fault_blocks_forced_stale_q(self):c=self.ready();self.assertFalse(c.step(500,thermal_ok=False,relay_cmd=True,forced_q=True))
 def test_settling_timer_restarts(self):
  c=Circuit();c.step(0);c.step(250,thermal_ok=False);c.step(251);self.assertFalse(c.step(500,rearm=True,relay_cmd=True));self.assertFalse(c.ready)
 def test_original_relay_command_still_needed(self):c=self.ready();self.assertFalse(c.step(500,rearm=True,relay_cmd=False));self.assertTrue(c.q)
 def test_each_datasheet_delay_corner(self):
  for d in [180,300,420]:
   c=Circuit(d);c.step(0);self.assertFalse(c.step(d-1,rearm=True,relay_cmd=True));c.step(d,rearm=False);self.assertTrue(c.step(d+1,rearm=True,relay_cmd=True))
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests));assert result.wasSuccessful()
# Conservative DC corner calculations (normal operating rails, tested component behavior remains a release hold).
vddlo=3.135;vddhi=3.465
head=(vddlo/10100-5e-6)/(1/10100+1/99000)
pg_no_vbe=(vddlo/10100-5e-6)/(1/10100+1/46530) # maximal load: Q3 base resistance shorted to ground, R13 adds no further load
calc={'healthy_return_min_V_with_5uA_input_leak':head,'open_return_max_V_with_5uA_input_leak':5e-6*101000,'head_trip_sink_upper_mA':1000*vddhi/9900,'READY_RAW_min_V_with_5uA_buffer_input_leak':3.135-10100*5e-6,'THERMAL_READY_VOH_min_V_at_100uA':3.135-.1,'U6_output_load_upper_uA':1e6*(3.465/46530+5e-6),'ready_pullup_max_mA':1000*vddhi/9900,'G30_falling_min_V':2.79*(1-.015),'G30_falling_max_V':2.79*(1+.015),'G30_release_upper_V_conservative':2.79*1.015+2.79*.025,'supervisor_delay_min_ms':180,'supervisor_delay_max_ms':420,'sensor_startup_ms':35,'minimum_settling_excess_ms':180-35,'reset_pressed_RC_tau_ms':1000*(1000*100000/(101000))*100e-9,'reset_released_RC_tau_ms':1000*100000*100e-9,'coil_gate_sink_required_max_mA':1000*5.25/46530,'PMOS_loss_upper_W_150mA_85mohm_25C':.15*.15*.085,'PMOS_drop_upper_V_150mA_85mohm_25C':.15*.085}
assert calc['G30_release_upper_V_conservative']<vddlo;assert pg_no_vbe>2.0
out={'schematic_pin_net_match':'PASS','pins_checked':len(expected),'critical_manufacturer_pin_maps':'PASS','no_MCU_rearm_net':'PASS','ideal_logic_tests_passed':result.testsRun,'calculations':calc,'ERC_report':'erc.rpt','PCB_status':'Separate controller and sensor candidates; see physical verification','physical_power_ramp_reset_and_thermal_tests':'NOT_RUN; required before claiming release','thermal_cutoff_and_load_break':'EXTERNAL integration required; this latch does not interrupt welded load contacts'}
(R/'validation/independent_checks.json').write_text(json.dumps(out,indent=2), encoding='utf-8', newline='\n');print(json.dumps(out,indent=2))
assert 'Errors 0  Warnings 0' in (R/'validation/erc.rpt').read_text(encoding='utf-8')
# Board-to-manifest agreement, including duplicated through-hole switch pads with the same pin number.
import pcbnew as pcb
board_refs=set();physical=[]
for stem,board_mm in [('thermal_controller',[45,35,1.6]),('thermal_sensor',[12,12,1.6])]:
 board=pcb.LoadBoard(str(R/(stem+'.kicad_pcb')));pins={};duplicates=0
 for fp in board.GetFootprints():
  board_refs.add(fp.GetReference())
  for pd in fp.Pads():
   key=(fp.GetReference(),pd.GetNumber());net=pd.GetNetname() or None
   if key in pins:assert pins[key]==net;duplicates+=1
   pins[key]=net;assert expected[key]==net,(stem,key,expected[key],net)
 drc=(R/'validation'/('controller_drc.rpt' if stem=='thermal_controller' else 'sensor_drc.rpt')).read_text(encoding='utf-8')
 assert '** Found 0 DRC violations **' in drc and '** Found 0 unconnected pads **' in drc,drc
 if stem=='thermal_sensor':
  jf=next(f for f in board.GetFootprints() if f.GetReference()=='J4');assert all(pd.GetAttribute()==pcb.PAD_ATTRIB_SMD for pd in jf.Pads())
  islands=[d for d in board.GetDrawings() if isinstance(d,pcb.PCB_SHAPE) and d.GetLayer()==pcb.B_Cu and d.GetNetname()=='GND_HEAD'];assert len(islands)==1 and islands[0].IsFilled()
  tv=[v for v in board.GetTracks() if isinstance(v,pcb.PCB_VIA) and v.GetNetname()=='GND_HEAD'];assert len(tv)==4
 physical.append({'board':stem,'board_mm':board_mm,'component_count':len(list(board.GetFootprints())),'pins_checked':len(pins),'duplicate_switch_pads_checked':duplicates,'tracks_and_vias':len(list(board.GetTracks())),'DRC':'0 violations / 0 unconnected'})
assert board_refs=={c['ref'] for c in m['components'] if not c['ref'].startswith('W')}
out['physical_boards']=physical;out['PCB_status']='ROUTED DIGITAL CANDIDATES; no fabrication/energization release';(R/'validation/independent_checks.json').write_text(json.dumps(out,indent=2), encoding='utf-8', newline='\n');print(json.dumps(physical,indent=2))
