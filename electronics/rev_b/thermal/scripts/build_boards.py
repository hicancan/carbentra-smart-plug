#!/usr/bin/python3
"""Physical low-voltage candidates, sourced footprints, separate sensor head."""
import pcbnew as p,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];m=json.loads((R/'pin_net_manifest.json').read_text())
head={'U1','R1','C1','J4'}
positions={'J1':(3,4,0),'J3':(3,22,0),'SW1':(35,3,0),'U2':(10,22,0),'R2':(8,29,0),'C2':(14,25,0),'U3':(19,20,0),'R3':(17,27,0),'R4':(23,20,0),'C3':(19,15,0),'U4':(29,20,0),'C4':(29,15,0),'R5':(29,9,0),'R7':(24,10,0),'C5':(27,5,0),'U5':(22,5,0),'C6':(18,3,0),'Q1':(12,8,0),'Q2':(17,8,0),'Q3':(17,12,0),'R9':(10,4,0),'R10':(35,20,0),'R11':(22,13,0),'R12':(23,27,0),'R13':(29,29,0),'TP1':(39,21,0),'TP2':(39,27,0),'U6':(34,26,0),'C7':(34,30,0)}
poshead={'U1':(3.4,6,0),'R1':(5.5,3,0),'C1':(2.5,2.3,0),'J4':(9,3,0)}
def vec(a):return p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1]))
for stem,parts,pos,W,H in [('thermal_controller',[c for c in m['components'] if c['ref'] not in head and not c['ref'].startswith('W')],positions,45,35),('thermal_sensor',[c for c in m['components'] if c['ref'] in head],poshead,12,12)]:
 if len(sys.argv)>1 and stem!=sys.argv[1]:continue
 assert set(pos)=={c['ref'] for c in parts},(set(pos),{c['ref'] for c in parts})
 b=p.BOARD();b.GetDesignSettings().SetCopperLayerCount(2);b.GetDesignSettings().SetBoardThickness(p.FromMM(1.6));nets={}
 for n in sorted({n for c in parts for n in c['pins'].values() if n}):net=p.NETINFO_ITEM(b,n);b.Add(net);nets[n]=net
 for c in parts:
  lib,name=c['footprint'].split(':');f=p.FootprintLoad(str(R/'Thermal.pretty') if lib=='Thermal' else '/usr/share/kicad/footprints/'+lib+'.pretty',name);f.SetReference(c['ref']);f.SetValue(c['value']);f.SetPosition(vec(pos[c['ref']]));f.SetOrientationDegrees(pos[c['ref']][2]);f.Reference().SetVisible(False);f.Value().SetVisible(False)
  for pad in f.Pads():
   if c['pins'].get(pad.GetNumber()):pad.SetNet(nets[c['pins'][pad.GetNumber()]])
  b.Add(f)
 for a,z in [((0,0),(W,0)),((W,0),(W,H)),((W,H),(0,H)),((0,H),(0,0))]:
  e=p.PCB_SHAPE();e.SetShape(p.SHAPE_T_SEGMENT);e.SetStart(vec(a));e.SetEnd(vec(z));e.SetLayer(p.Edge_Cuts);e.SetWidth(p.FromMM(.05));b.Add(e)
 for txt,x,y,size in [('REV B / HOLD',W/2,H-1.4,.7),('ISOLATED LV ONLY',W/2,H-2.7,.6)]:
  t=p.PCB_TEXT(b);t.SetText(txt);t.SetPosition(vec((x,y)));t.SetTextSize(vec((size,size)));t.SetTextThickness(p.FromMM(.1));t.SetLayer(p.Dwgs_User);b.Add(t)
 # Explicit fine-pitch escapes and small sensor routing avoid a grid router's pad-channel quantization.
 def tr(net,pts,layer=p.F_Cu,w=.15):
  for a,z in zip(pts,pts[1:]):
   if a==z:continue
   t=p.PCB_TRACK(b);t.SetStart(vec(a));t.SetEnd(vec(z));t.SetWidth(p.FromMM(w));t.SetLayer(layer);t.SetNet(nets[net]);b.Add(t)
 def vi(net,xy):
  v=p.PCB_VIA(b);v.SetPosition(vec(xy));v.SetWidth(p.F_Cu,p.FromMM(.6));v.SetWidth(p.B_Cu,p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nets[net]);
  if stem=='thermal_sensor':v.SetFrontTentingMode(p.TENTING_MODE_TENTED);v.SetBackTentingMode(p.TENTING_MODE_TENTED)
  b.Add(v)
 if stem=='thermal_controller':
  tr('+3V3_ISO',[(20.1375,20),(20.1375,19.05),(21.3,19.05),(21.3,18)]);vi('+3V3_ISO',(21.3,18))
  for net,pts in [('REARM_CLK',[(27.6,19.25),(26.5,19.25),(26.5,18.5),(25.5,18.5)]),('+3V3_ISO',[(27.6,19.75),(25.5,19.75)]),('GND_ISO',[(27.6,20.75),(26.5,20.75),(26.5,22)]),('COIL_ARMED',[(30.4,20.75),(31.5,20.75),(31.5,22)]),('THERMAL_READY',[(30.4,20.25),(32.5,20.25)]),('+3V3_ISO',[(30.4,19.75),(30.4,19.25),(31.5,19.25),(31.5,18.5),(32.5,18.5)])]:
   tr(net,pts);vi(net,pts[-1])
 else:
  tr('GND_HEAD',[(2.6875,6),(2.6875,5.5),(2,5.5),(2,4.7),(4.8,4.7),(4.8,5.5),(4.1125,5.5)])
  tr('GND_HEAD',[(3.275,2.3),(3.275,4.7)])
  tr('GND_HEAD',[(9,5.54),(7,5.54),(7,4.7),(4.8,4.7)])
  tr('THERM_RETURN',[(2.6875,6.5),(2,6.5),(2,8.08),(9,8.08)])
  tr('THERM_RETURN',[(6.325,3),(6.325,4)]);vi('THERM_RETURN',(6.325,4));tr('THERM_RETURN',[(6.325,4),(7.5,4),(7.5,8.08),(10.7,8.08)],p.B_Cu);vi('THERM_RETURN',(10.7,8.08));tr('THERM_RETURN',[(10.7,8.08),(9,8.08)])
  tr('+3V3_HEAD',[(4.1125,6),(4.1125,6.5),(5,6.5),(5,7.2)]);vi('+3V3_HEAD',(5,7.2))
  tr('+3V3_HEAD',[(4.675,3),(4.675,2)]);vi('+3V3_HEAD',(4.675,2))
  tr('+3V3_HEAD',[(1.725,2.3),(1.725,1.2)]);vi('+3V3_HEAD',(1.725,1.2))
  tr('+3V3_HEAD',[(1.725,1.2),(4.675,1.2),(4.675,2),(7,2),(8,1.6)],p.B_Cu);vi('+3V3_HEAD',(8,1.6));tr('+3V3_HEAD',[(8,1.6),(9,1.6),(9,3)])
  tr('+3V3_HEAD',[(5,7.2),(5.7,7.2),(5.7,2.5),(4.675,2.5),(4.675,2)],p.B_Cu)
 if stem=='thermal_sensor':
  tr('GND_HEAD',[(1.6,4.7),(2,4.7)])
  for pt in [(1.6,4.7),(2.4,4.7),(3.4,4.7),(4.2,4.7)]:vi('GND_HEAD',pt)
  island=p.PCB_SHAPE();island.SetShape(p.SHAPE_T_RECT);island.SetStart(vec((1.2,4.3)));island.SetEnd(vec((4.5,6.9)));island.SetLayer(p.B_Cu);island.SetWidth(0);island.SetFilled(True);island.SetNet(nets['GND_HEAD']);b.Add(island)
 p.SaveBoard(str(R/(stem+'.kicad_pcb')),b)
 proj=json.loads((R/'thermal_interlock.kicad_pro').read_text());proj['meta']={'filename':stem+'.kicad_pro','version':1};proj['net_settings']={'classes':[{'name':'Default','clearance':.15,'track_width':.15,'via_diameter':.6,'via_drill':.3,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.2,'diff_pair_gap':.25,'diff_pair_via_gap':.25}], 'netclass_assignments':{},'netclass_patterns':[], 'meta':{'version':4}}
 rules=proj['board']['design_settings']['rules'];rules['min_clearance']=.15;rules['min_track_width']=.15;rules['min_through_hole_diameter']=.3
 (R/(stem+'.kicad_pro')).write_text(json.dumps(proj,indent=2));(R/(stem+'.kicad_dru')).write_text('(version 1)\n(rule "Isolated LV fine-pitch clearance" (constraint clearance (min 0.15mm)))\n')
 (R/'validation'/(stem+'_placement.json')).write_text(json.dumps({'board_mm':[W,H,1.6],'components':[c['ref'] for c in parts],'positions':pos,'status':'SOURCE_PLACEMENT_RECORD; final checks are independent_checks.json'},indent=2))
 print(stem,len(parts),'parts',W,H)
