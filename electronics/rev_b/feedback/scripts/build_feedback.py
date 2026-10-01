#!/usr/bin/python3
from carbentra_tools import FREECAD_LIB, FONT_REGULAR, PYTHON, kicad_resource
"""Rebuild standalone Rev B detector development candidate. Never edits EVT-A."""
from pathlib import Path
import json, uuid, math, csv, itertools
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]
def uid(s): return str(uuid.uuid5(uuid.NAMESPACE_URL,'carbentra/revb/feedback/'+s))
def q(s): return json.dumps(str(s))
def mm(x,y): return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
URLU='https://docs.broadcom.com/doc/AV02-2153EN'
URLR='https://www.vishay.com/docs/28729/pr010203.pdf'
parts=[]
def add(ref,sym,val,fp,nets,xy,sch,mpn,url,height=1):
 parts.append(dict(ref=ref,symbol=sym,value=val,footprint=fp,pins={str(k):v for k,v in nets.items()},board=xy,schematic=sch,mpn=mpn,datasheet=url,height_mm=height))
for ref,ns,xy,sch in [('R1',{1:'L_POST',2:'L_MID'},(5,3,0),(55.88,50.8)),('R2',{1:'L_MID',2:'AC1'},(15.16,8,180),(81.28,50.8)),('R3',{1:'N_MID',2:'AC2'},(15.16,17,180),(81.28,91.44)),('R4',{1:'N_POST',2:'N_MID'},(5,22,0),(55.88,91.44))]:
 add(ref,'R_H','33k 1% 1W','Feedback:PR01_P10.16',ns,xy,sch,'PR01000103302FA100',URLR,4.5)
add('U1','ACPL_K376','ACPL-K376-560E','Feedback:SSO8_ACPL_K376',{1:'AC1',2:None,3:None,4:'AC2',5:'GND_ISO',6:'OUTPUT_PRESENT_N',7:None,8:'+3V3_ISO'},(24.6,12.5,0),(127,63.5),'ACPL-K376-560E',URLU,3.307)
add('R5','R_H','1.8k 1%','Resistor_SMD:R_0603_1608Metric',{1:'+3V3_ISO',2:'OUTPUT_PRESENT_N'},(31.2,4.7,0),(175.26,43.18),'RC0603FR-071K8L','https://www.yageo.com/en/ProductSearch',0.55)
add('C1','C_V','100nF 16V X7R','Capacitor_SMD:C_0603_1608Metric',{1:'+3V3_ISO',2:'GND_ISO'},(31.2,20,0),(170.18,83.82),'GRM188R71C104KA01D','https://www.murata.com/en-us/products/productdetail?partno=GRM188R71C104KA01D',0.9)
add('J1','WIRE','POST-SWITCH L','Feedback:Wire_Pad_1.2mm',{1:'L_POST'},(1.8,3,0),(30.48,50.8),'Internal harness solder land; wire/strain relief HOLD','',4)
add('J2','WIRE','POST-SWITCH N','Feedback:Wire_Pad_1.2mm',{1:'N_POST'},(1.8,22,0),(30.48,91.44),'Internal harness solder land; wire/strain relief HOLD','',4)
add('J3','HEADER3','3V3 / GND / OUT_N','Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',{1:'+3V3_ISO',2:'GND_ISO',3:'OUTPUT_PRESENT_N'},(33,9,0),(215.9,63.5),'TSW-103-07-G-S','https://www.samtec.com/products/tsw',8.38)
# Compact custom footprints use manufacturer maximum bodies, no inappropriate generic approximation.
fpdir=ROOT/'Feedback.pretty';fpdir.mkdir(exist_ok=True)
def base(name):return f'(footprint "{name}" (version 20241229) (generator "pcbnew") (layer "F.Cu") (property "Reference" "REF**" (at 0 -4 0) (layer "F.SilkS") (effects (font (size .7 .7) (thickness .12)))) (property "Value" "{name}" (at 0 4 0) (layer "F.Fab") (effects (font (size .7 .7) (thickness .12))))'
def rect(a,b,layer,width=.1): return f'(fp_rect (start {a[0]} {a[1]}) (end {b[0]} {b[1]}) (stroke (width {width}) (type default)) (fill none) (layer "{layer}"))'
s=base('SSO8_ACPL_K376')+' (attr smd)'+rect((-3.467,-3.175),(3.467,3.175),'F.Fab')+rect((-6.575,-3.55),(6.575,3.55),'F.CrtYd',.05)
for pin in range(1,9):
 x=-5.3725 if pin<=4 else 5.3725;y=(-1.905+(pin-1)*1.27) if pin<=4 else (1.905-(pin-5)*1.27)
 s+=f'(pad "{pin}" smd rect (at {x} {y}) (size 1.905 .65) (layers "F.Cu" "F.Paste" "F.Mask"))'
s+='(fp_circle (center -2.7 -2.4) (end -2.35 -2.4) (stroke (width .12) (type default)) (fill none) (layer "F.SilkS")))'
(fpdir/'SSO8_ACPL_K376.kicad_mod').write_text(s, encoding='utf-8', newline='\n')
s=base('PR01_P10.16')+' (attr through_hole)'+rect((1.83,-1.25),(8.33,1.25),'F.Fab')+rect((-1.2,-1.7),(11.36,1.7),'F.CrtYd',.05)+rect((1.83,-1.25),(8.33,1.25),'F.SilkS',.12)
for pin,x in [(1,0),(2,10.16)]:s+=f'(pad "{pin}" thru_hole circle (at {x} 0) (size 1.8 1.8) (drill .9) (layers "*.Cu" "*.Mask"))'
(fpdir/'PR01_P10.16.kicad_mod').write_text(s+')', encoding='utf-8', newline='\n')
s=base('Wire_Pad_1.2mm')+' (attr through_hole)'+rect((-1.45,-1.45),(1.45,1.45),'F.CrtYd',.05)+'(pad "1" thru_hole circle (at 0 0) (size 2.4 2.4) (drill 1.2) (layers "*.Cu" "*.Mask")))'
(fpdir/'Wire_Pad_1.2mm.kicad_mod').write_text(s, encoding='utf-8', newline='\n')
(ROOT/'fp-lib-table').write_text('(fp_lib_table (lib (name "Feedback") (type "KiCad") (uri "${KIPRJMOD}/Feedback.pretty") (options "") (descr "Rev B detector footprints, manufacturer based")))', encoding='utf-8', newline='\n')
# Custom simple symbols, pin-correct and embedded for portability.
pindefs={
 'R_H':[(1,'1','passive',-5.08,0,0),(2,'2','passive',5.08,0,180)],
 'C_V':[(1,'1','passive',0,5.08,270),(2,'2','passive',0,-5.08,90)],
 'WIRE':[(1,'1','passive',5.08,0,180)],
 'HEADER3':[(1,'3V3','passive',-7.62,2.54,0),(2,'GND','passive',-7.62,0,0),(3,'OUT_N','passive',-7.62,-2.54,0)],
 'ACPL_K376':[(1,'AC1','passive',-17.78,7.62,0),(2,'DC+','passive',-17.78,2.54,0),(3,'DC-','passive',-17.78,-2.54,0),(4,'AC2','passive',-17.78,-7.62,0),(5,'GND','power_in',17.78,-7.62,180),(6,'VO','open_collector',17.78,-2.54,180),(7,'NC','no_connect',17.78,2.54,180),(8,'VCC','power_in',17.78,7.62,180)]}
syms={}
for name,pins in pindefs.items():
 hide='(hide yes)' if name in ['R_H','C_V','WIRE'] else ''
 s=f'(symbol "Feedback:{name}" (pin_names (offset 1.016) {hide}) (pin_numbers {hide}) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 15.24 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 12.7 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_0_1"'
 if name=='R_H':s+='(rectangle (start -2.54 1.016) (end 2.54 -1.016) (stroke (width 0) (type default)) (fill (type none)))'
 elif name=='C_V':
  for y in [-.635,.635]:s+=f'(polyline (pts (xy -2.54 {y}) (xy 2.54 {y})) (stroke (width 0) (type default)) (fill (type none)))'
 elif name=='WIRE':s+='(circle (center 1.27 0) (radius 1.27) (stroke (width 0) (type default)) (fill (type none)))'
 else:
  xx=12.7 if name=='ACPL_K376' else 2.54;yy=10.16 if name=='ACPL_K376' else 5.08
  s+=f'(rectangle (start {-xx} {yy}) (end {xx} {-yy}) (stroke (width 0) (type default)) (fill (type background)))'
 s+=')'+f'(symbol "{name}_1_1"'
 for num,pn,typ,x,y,ang in pins:
  length=2.54 if name=='R_H' else 4.445 if name=='C_V' else 2.54 if name=='WIRE' else 5.08
  s+=f'(pin {typ} line (at {x} {y} {ang}) (length {length}) (name "{pn}" (effects (font (size 1 1)))) (number "{num}" (effects (font (size 1 1)))))'
 syms[name]=s+'))'
items=[];ends={}
for c in parts:
 x,y=c['schematic'];name=c['symbol'];ref=c['ref'];s=f'(symbol (lib_id "Feedback:{name}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (uuid {uid(ref)})'
 for pn,pv,dy,hide in [('Reference',ref,-16 if name=='ACPL_K376' else -6,False),('Value',c['value'],-13 if name=='ACPL_K376' else -9 if name=='HEADER3' else -3,False),('Footprint',c['footprint'],0,True),('Datasheet',c['datasheet'],0,True)]:
  s+=f'(property {q(pn)} {q(pv)} (at {x} {y+dy} 0) (effects (font (size 1.1 1.1))'+(' (hide yes)' if hide else '')+'))'
 for pin in pindefs[name]:s+=f'(pin "{pin[0]}" (uuid {uid(ref+str(pin[0]))}))'
 s+=f'(instances (project "output_feedback" (path "/{uid("sheet")}" (reference "{ref}") (unit 1)))))';items.append(s)
 for num,pn,typ,px,py,ang in pindefs[name]:
  a=(round(x+px,5),round(y-py,5));net=c['pins'][str(num)];ends[(ref,str(num))]=a
  if net is None:items.append(f'(no_connect (at {a[0]} {a[1]}) (uuid {uid(ref+str(num)+"nc")}))')
def wire(a,b,key):
 if a!=b:items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid {uid(key)}))')
def path(points,key):
 for i,(a,b) in enumerate(zip(points,points[1:])):wire(a,b,key+str(i))
def label(net,a,key,side='left'):
 items.append(f'(label {q(net)} (at {a[0]} {a[1]} 0) (effects (font (size 1.1 1.1)) (justify {side} bottom)) (uuid {uid(key)}))')
for a,b in [(('J1','1'),('R1','1')),(('R1','2'),('R2','1')),(('J2','1'),('R4','1')),(('R4','2'),('R3','1'))]:wire(ends[a],ends[b],str(a)+str(b))
for r,up in [('R2','1'),('R3','4')]:
 a=ends[(r,'2')];z=ends[('U1',up)];path([a,(99.06,a[1]),(99.06,z[1]),z],r+'U1')
for ref,pins in [('U1',['5','6','8']),('R5',['1','2']),('C1',['1','2']),('J3',['1','2','3'])]:
 c=next(c for c in parts if c['ref']==ref)
 for pin in pins:
  a=ends[(ref,pin)];n=c['pins'][pin];direc=1 if ref=='U1' or(ref=='R5' and pin=='2') else -1
  z=(round(a[0]+direc*5.08,5),a[1]);wire(a,z,ref+pin+'stub');label(n,z,ref+pin+'label','left' if direc==1 else 'right')
for ref,pin,net in [('R1','1','L_POST'),('R1','2','L_MID'),('R2','2','AC1'),('R4','1','N_POST'),('R4','2','N_MID'),('R3','2','AC2')]:
 label(net,ends[(ref,pin)],net+'HVlabel')
# External sources are explicitly declared by power flags to keep ERC meaningful.
for i,(net,x) in enumerate([('+3V3_ISO',55.88),('GND_ISO',86.36)]):
 # simple power_out symbol and labeled pin, only sheet assertion of supplied interface
 name='SupplyFlag';syms[name]='(symbol "Feedback:SupplyFlag" (pin_names (offset 0) (hide yes)) (pin_numbers (hide yes)) (in_bom no) (on_board no) (property "Reference" "#FLG" (at 0 0 0) (effects (font (size 1 1)) (hide yes))) (property "Value" "External supply" (at 0 3 0) (effects (font (size 1 1)))) (symbol "SupplyFlag_1_1" (pin power_out line (at 0 0 90) (length 0) (name "pwr" (effects (font (size 1 1)))) (number "1" (effects (font (size 1 1)))))))'
 items.append(f'(symbol (lib_id "Feedback:SupplyFlag") (at {x} 119.38 0) (unit 1) (in_bom no) (on_board no) (uuid {uid(net+"flag")}) (property "Reference" "#FLG0{i+1}" (at {x} 119.38 0) (effects (font (size 1 1)) (hide yes))) (property "Value" "External supply" (at {x} 116.38 0) (effects (font (size 1 1)))) (instances (project "output_feedback" (path "/{uid("sheet")}" (reference "#FLG0{i+1}") (unit 1)))))')
 label(net,(x,119.38),net+'flaglabel')
for text,x,y,size in [('REV B OUTPUT PRESENCE / DEVELOPMENT ONLY',17.78,15.24,2),('198-264 VAC, 50/60 Hz | NO FABRICATION / NO ENERGIZATION RELEASE',17.78,22.86,1.3),('MAINS INPUT: tap the ACTUAL socket contacts after all switched poles',17.78,33.02,1.3),('ISOLATED 3.3 V: active-low pulses, 100/120 Hz when AC is present',147.32,106.68,1.1),('DC+ / DC- / NC intentionally open. Do not bridge either isolation domain.',17.78,132.08,1.2),('No safety isolation proof, no proof of absence of voltage, no physical contact-position feedback.',17.78,139.7,1.2),('132k total series resistance; built-in bridge/threshold controller inside U1.',17.78,147.32,1.2),('Use a separate hardware thermal interlock AND a qualified series thermal cutoff.',17.78,154.94,1.2)]:items.append(f'(text {q(text)} (at {x} {y} 0) (effects (font (size {size} {size})) (justify left)) (uuid {uid(text)}))')
(ROOT/'output_feedback.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {uid("sheet")}) (paper "A4") (title_block (title "CARBENTRA Rev B output detector") (rev "B-CANDIDATE / HOLD")) (lib_symbols '+''.join(syms.values())+')'+''.join(items)+')', encoding='utf-8', newline='\n')
(ROOT/'Feedback.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")'+''.join(v.replace('Feedback:','') for v in syms.values())+')', encoding='utf-8', newline='\n')
(ROOT/'sym-lib-table').write_text('(sym_lib_table (lib (name "Feedback") (type "KiCad") (uri "${KIPRJMOD}/Feedback.kicad_sym") (options "") (descr "Pin-verified custom detector symbols")))', encoding='utf-8', newline='\n')
# 35 x 25 mm board, whole-width two domains; blank barrier has no copper on either layer.
b=p.BOARD();b.GetDesignSettings().SetCopperLayerCount(2);b.GetDesignSettings().SetBoardThickness(p.FromMM(1.6))
names=sorted({n for c in parts for n in c['pins'].values() if n});nets={}
for n in names:nn=p.NETINFO_ITEM(b,n);b.Add(nn);nets[n]=nn
fps={}
for c in parts:
 lib,name=c['footprint'].split(':');pathlib=fpdir if lib=='Feedback' else Path(kicad_resource('footprints'))/(lib+'.pretty');fp=p.FootprintLoad(str(pathlib),name)
 fp.SetReference(c['ref']);fp.SetValue(c['value']);fp.SetPosition(mm(*c['board'][:2]));fp.SetOrientationDegrees(c['board'][2]);fp.SetPath(p.KIID_PATH('/'+uid('sheet')+'/'+uid(c['ref'])))
 fp.Reference().SetVisible(False);fp.Value().SetVisible(False)
 for pad in fp.Pads():
  net=c['pins'].get(pad.GetNumber())
  if net:pad.SetNet(nets[net])
 b.Add(fp);fps[c['ref']]=fp
# Outline and one 1.0 mm routed slot under optical package. It is extra contamination margin, not a substitute for clearance.
def edge(a,z):
 s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(mm(*a));s.SetEnd(mm(*z));s.SetLayer(p.Edge_Cuts);s.SetWidth(p.FromMM(.05));b.Add(s)
for poly in [[(0,0),(35,0),(35,25),(0,25),(0,0)],[(24.1,2),(25.1,2),(25.1,23),(24.1,23),(24.1,2)]]:
 for a,z in zip(poly,poly[1:]):edge(a,z)
def pp(ref,pin):
 v=next(pd for pd in fps[ref].Pads() if pd.GetNumber()==str(pin)).GetPosition();return (p.ToMM(v.x),p.ToMM(v.y))
def route(net,pts,layer=p.F_Cu,width=.35):
 for a,z in zip(pts,pts[1:]):
  if a==z:continue
  t=p.PCB_TRACK(b);t.SetStart(mm(*a));t.SetEnd(mm(*z));t.SetWidth(p.FromMM(width));t.SetLayer(layer);t.SetNet(nets[net]);b.Add(t)
def via(net,a):
 v=p.PCB_VIA(b);v.SetPosition(mm(*a));v.SetWidth(p.F_Cu,p.FromMM(.65));v.SetWidth(p.B_Cu,p.FromMM(.65));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nets[net]);b.Add(v)
route('L_POST',[pp('J1',1),pp('R1',1)],width=.6);route('N_POST',[pp('J2',1),pp('R4',1)],width=.6)
route('L_MID',[pp('R1',2),pp('R2',1)]);route('N_MID',[pp('R4',2),pp('R3',1)])
route('AC1',[pp('R2',2),(5,10.595),pp('U1',1)]);route('AC2',[pp('R3',2),(5,14.405),pp('U1',4)])
# LV front paths with bottom-layer rails to avoid crossings.
route('+3V3_ISO',[pp('U1',8),(31.1,10.595),(31.1,9),pp('J3',1)],width=.25)
route('OUTPUT_PRESENT_N',[pp('U1',6),(31.1,13.135),(31.9,14.08),pp('J3',3)],width=.25)
route('GND_ISO',[pp('U1',5),(30.3,14.405),(30.3,16.3)],width=.25);via('GND_ISO',(30.3,16.3));route('GND_ISO',[(30.3,16.3),(31.3,16.3),(31.3,11.54),pp('J3',2)],p.B_Cu,.25)
for ref,pin,net,dest in [('R5',1,'+3V3_ISO',(30.375,3.3)),('R5',2,'OUTPUT_PRESENT_N',(32.025,3.3)),('C1',1,'+3V3_ISO',(30.375,21.6)),('C1',2,'GND_ISO',(32.025,21.6))]:
 a=pp(ref,pin);route(net,[a,dest],width=.25);via(net,dest)
route('+3V3_ISO',[(30.375,3.3),(29.5,3.3),(29.5,9),(33,9)],p.B_Cu,.25)
route('OUTPUT_PRESENT_N',[(32.025,3.3),(34.3,3.3),(34.3,14.08),pp('J3',3)],p.B_Cu,.25)
route('+3V3_ISO',[(30.375,21.6),(29.1,21.6),(29.1,9),(29.5,9)],p.B_Cu,.25)
route('GND_ISO',[(32.025,21.6),(32.025,16.3),(31.3,16.3)],p.B_Cu,.25)
for txt,x,y,size in [('REV B / FAB HOLD',11,12.5,.75),('NO PE ON PCB',11,24,.65),('L POST',5,1.1,.6),('N POST',5,23.9,.6),('8mm MIN',24.6,1.1,.6),('1 3V3',32,7,.55),('2 GND',32,17.3,.55),('3 OUT_N',31,23.5,.55)]:
 t=p.PCB_TEXT(b);t.SetText(txt);t.SetPosition(mm(x,y));t.SetTextSize(mm(size,size));t.SetTextThickness(p.FromMM(.1));t.SetLayer(p.Dwgs_User);b.Add(t)
p.SaveBoard(str(ROOT/'output_feedback.kicad_pcb'),b)
# Explicit net classes plus physical distance rule; component NC pads 2/3 are also primary, 7 secondary.
proj=json.loads((ROOT.parents[1]/'carbentra.kicad_pro').read_text(encoding='utf-8'))
proj['meta']={'filename':'output_feedback.kicad_pro','version':1}
proj['net_settings']={'classes':[{'name':'Default','clearance':.2,'track_width':.25,'via_diameter':.65,'via_drill':.3,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.2,'diff_pair_gap':.25,'diff_pair_via_gap':.25},{'name':'MAINS','clearance':.25,'track_width':.35,'via_diameter':.65,'via_drill':.3,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.2,'diff_pair_gap':.25,'diff_pair_via_gap':.25},{'name':'SELV','clearance':.2,'track_width':.25,'via_diameter':.65,'via_drill':.3,'microvia_diameter':.3,'microvia_drill':.1,'diff_pair_width':.2,'diff_pair_gap':.25,'diff_pair_via_gap':.25}], 'netclass_assignments':{n:('MAINS' if n in ['L_POST','N_POST','L_MID','N_MID','AC1','AC2'] else 'SELV') for n in names},'netclass_patterns':[], 'meta':{'version':4}}
proj['board']['design_settings']['rules']['min_through_hole_diameter']=.3
(ROOT/'output_feedback.kicad_pro').write_text(json.dumps(proj,indent=2), encoding='utf-8', newline='\n')
(ROOT/'output_feedback.kicad_dru').write_text('''(version 1)
(rule "Primary to isolated logic copper" (condition "(A.NetClass == 'MAINS' && B.NetClass == 'SELV') || (A.NetClass == 'SELV' && B.NetClass == 'MAINS')") (constraint clearance (min 8mm)))
(rule "Unattenuated input L to N" (condition "(A.NetName == 'L_POST' && B.NetName == 'N_POST') || (A.NetName == 'N_POST' && B.NetName == 'L_POST')") (constraint clearance (min 3.2mm)))
''', encoding='utf-8', newline='\n')
manifest={'status':'DEVELOPMENT_CANDIDATE_NO_ENERGIZATION','board_mm':[35,25,1.6],'envelope_height_above_pcb_mm':9.0,'envelope_height_below_pcb_mm':3.0,'components':parts,'U1_verified_pin_names':{str(x[0]):x[1] for x in pindefs['ACPL_K376']},'unconnected_pads':{'U1':['2','3','7']},'isolation':{'minimum_design_copper_clearance_mm':8,'opto_nominal_pad_edge_clearance_mm':8.84,'slot_mm':[24.1,2,25.1,23]},'host_interface':{'J3.1':'+3V3_ISO','J3.2':'GND_ISO','J3.3':'OUTPUT_PRESENT_N','GPIO_required':1,'logic':'active-low pulses, not a static relay-position state'}}
(ROOT/'pin_net_manifest.json').write_text(json.dumps(manifest,indent=2), encoding='utf-8', newline='\n')
with (ROOT/'bom.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Reference','Value','MPN candidate','Footprint','Max height mm','Source','Status'])
 for c in parts:w.writerow([c['ref'],c['value'],c['mpn'],c['footprint'],c['height_mm'],c['datasheet'],'DEVELOPMENT / VERIFY ASSEMBLY'])
print('Generated',len(parts),'parts;',len(names),'nets; 35x25mm board.')
