#!/usr/bin/python3
"""Concrete isolated-LV thermal rearm latch. Schematic/netlist only; not a physical release."""
from pathlib import Path
import re,json,uuid,copy,csv,math
R=Path(__file__).resolve().parents[1]
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'carbonmirror/revb/thermal/'+s))
def q(x):return json.dumps(str(x))
def parse(s):
 stack=[]
 for t in re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',s):
  if t=='(':
   a=[]
   if stack:stack[-1].append(a)
   stack.append(a)
  elif t==')':root=stack.pop()
  else:stack[-1].append(t)
 return root
def ch(x,k):return next((v for v in x if isinstance(v,list) and v[0]==k),None)
def cs(x,k):return [v for v in x if isinstance(v,list) and v[0]==k]
def atom(s):return json.loads(s) if s.startswith('"') else s
def ser(x):return '('+' '.join(map(ser,x))+')' if isinstance(x,list) else x
cache={}
def lib(lib,name):
 if lib not in cache:cache[lib]={atom(v[1]):v for v in cs(parse(Path('/usr/share/kicad/symbols',lib+'.kicad_sym').read_text()),'symbol')}
 s=copy.deepcopy(cache[lib][name]);ext=ch(s,'extends')
 if ext:
  base=libsym=globals()['lib'](lib,atom(ext[1]));props={atom(v[1]):v for v in cs(base,'property')};props.update({atom(v[1]):v for v in cs(s,'property')});s=[s[0],s[1]]+list(props.values())+[v for v in base[2:] if not(isinstance(v,list) and v[0] in ['property','extends'])]
 for v in cs(s,'symbol'):v[1]=q(name+'_'+atom(v[1]).split('_')[-2]+'_'+atom(v[1]).split('_')[-1])
 return s
custom={}
def custom_ic(name,pin_specs):
 # pin tuples: number,name,type,x,y,angle; outer pin at +/-12.7, body +/-10.16
 s=f'(symbol "{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 15.24 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 12.7 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_0_1" (rectangle (start -10.16 10.16) (end 10.16 -10.16) (stroke (width 0) (type default)) (fill (type background)))) (symbol "{name}_1_1"'
 for no,n,t,x,y,a in pin_specs:s+=f'(pin {t} line (at {x} {y} {a}) (length 2.54) (name {q(n)} (effects (font (size 1 1)))) (number {q(no)} (effects (font (size 1 1)))))'
 custom[name]=parse(s+'))')
custom_ic('TMP302B',[(1,'TRIPSET0','input',-12.7,5.08,0),(6,'TRIPSET1','input',-12.7,0,0),(4,'HYSTSET','input',-12.7,-5.08,0),(3,'OUT_N','open_collector',12.7,0,180),(5,'VS','power_in',0,12.7,270),(2,'GND','power_in',0,-12.7,90)])
custom_ic('SN74LVC1G74',[(2,'D','input',-12.7,5.08,0),(1,'CLK','input',-12.7,0,0),(6,'CLR_N','input',-12.7,-5.08,0),(5,'Q','output',12.7,5.08,180),(3,'Q_N','output',12.7,0,180),(7,'PRE_N','input',12.7,-5.08,180),(8,'VCC','power_in',0,12.7,270),(4,'GND','power_in',0,-12.7,90)])
parts=[]
def add(ref,libname,symbol,value,fp,nets,xy,mpn,url,height=1):
 s=copy.deepcopy(custom[symbol]) if libname=='custom' else lib(libname,symbol);pins=[]
 for sub in cs(s,'symbol'):
  for pin in cs(sub,'pin'):pins.append(dict(number=atom(ch(pin,'number')[1]),name=atom(ch(pin,'name')[1]),at=list(map(float,ch(pin,'at')[1:4])),type=pin[1]))
 parts.append(dict(ref=ref,name=symbol,value=value,footprint=fp,pins={str(k):v for k,v in nets.items()},sch=xy,mpn=mpn,datasheet=url,height_mm=height,pin_geometry=pins,symbol=s))
RF='Resistor_SMD:R_0603_1608Metric';CF='Capacitor_SMD:C_0603_1608Metric';SOT='Package_TO_SOT_SMD:SOT-23'
def rr(ref,val,n1,n2,xy,mpn):add(ref,'Device','R',val,RF,{1:n1,2:n2},xy,mpn,'https://www.yageo.com/en/ProductSearch',.55)
def cc(ref,n1,n2,xy):add(ref,'Device','C','100nF 16V X7R',CF,{1:n1,2:n2},xy,'GRM188R71C104KA01D','https://www.murata.com/en-us/products/productdetail?partno=GRM188R71C104KA01D',.9)
S='+3V3_ISO';G='GND_ISO';H='+3V3_HEAD';HG='GND_HEAD';T='THERM_RETURN';PG='THERMAL_READY';A='COIL_ARMED'
add('U1','custom','TMP302B','TMP302BDRLR', 'Package_TO_SOT_SMD:SOT-563',{1:HG,2:HG,3:T,4:H,5:H,6:HG},(50.8,71.12),'TMP302BDRLR','https://www.ti.com/lit/gpn/TMP302',.6)
rr('R1','10k 1%',H,T,(83.82,55.88),'RC0603FR-0710KL');cc('C1',H,HG,(22.86,109.22))
add('U2','74xGxx','74LVC1G17','SN74LVC1G17DBVR','Package_TO_SOT_SMD:SOT-23-5',{1:None,2:T,3:G,4:'HEALTH_VALID',5:S},(132.08,71.12),'SN74LVC1G17DBVR','https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf',1.45)
rr('R2','100k 1%',T,G,(111.76,109.22),'RC0603FR-07100KL');cc('C2',S,G,(152.4,109.22))
add('U3','Power_Supervisor','TPS3808DBV','TPS3808G30DBVR','Package_TO_SOT_SMD:SOT-23-6',{1:'READY_RAW',2:G,3:'HEALTH_VALID',4:'CT_SELECT',5:S,6:S},(228.6,71.12),'TPS3808G30DBVR','https://www.ti.com/lit/ds/symlink/tps3808.pdf',1.45)
rr('R3','100k 1%',S,'CT_SELECT',(190.5,109.22),'RC0603FR-07100KL');rr('R4','10k 1%',S,'READY_RAW',(254,109.22),'RC0603FR-0710KL');cc('C3',S,G,(223.52,109.22))
add('U4','custom','SN74LVC1G74','SN74LVC1G74DCUR','Package_SO:VSSOP-8_2.3x2mm_P0.5mm',{1:'REARM_CLK',2:S,3:None,4:G,5:A,6:PG,7:S,8:S},(335.28,71.12),'SN74LVC1G74DCUR','https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf',1.1)
cc('C4',S,G,(304.8,109.22))
# Head and controller connector pair; actual cable nets are explicit W1/W2 series links for fault injection.
for ref,nets,xy,mpn in [('J3',{1:S,2:G,3:T},(45.72,142.24),'TSW-103-07-G-S'),('J4',{1:H,2:HG,3:T},(99.06,142.24),'TSW-103-07-G-S')]:add(ref,'Connector_Generic','Conn_01x03','SENSOR HARNESS', 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',nets,xy,mpn,'https://www.samtec.com/products/tsw-103-07-g-s',8.38)
# Wire harness is a documented off-board two-conductor link plus the shared return net. These are schematic-only zero-ohm wire models.
rr('W1','HARNESS: 3V3',S,H,(157.48,137.16),'OFF-BOARD WIRE MODEL / NOT BOM');rr('W2','HARNESS: GND',G,HG,(195.58,137.16),'OFF-BOARD WIRE MODEL / NOT BOM')
# Manual reset switch and MCU OR path. Do NOT AND clock with healthy: a held reset must not rearm on fault release.
add('SW1','Switch','SW_Push','MANUAL REARM','Button_Switch_THT:SW_PUSH_6mm',{1:S,2:'MANUAL_RAW'},(38.1,195.58),'B3F-1000','https://components.omron.com/us-en/products/switches/B3F',4.3)
rr('R5','1k 1%','MANUAL_RAW','REARM_RC',(63.5,210.82),'RC0603FR-071KL')
rr('R6','1k 1%','MCU_REARM','REARM_DIODE_A',(38.1,241.3),'RC0603FR-071KL')
add('D1','Device','D_Schottky','BAT54H,115','Diode_SMD:D_SOD-123F',{1:'REARM_RC',2:'REARM_DIODE_A'},(73.66,241.3),'BAT54H,115','https://assets.nexperia.com/documents/data-sheet/BAT54H.pdf',1.1)
rr('R7','100k 1%','REARM_RC',G,(99.06,210.82),'RC0603FR-07100KL');cc('C5','REARM_RC',G,(129.54,210.82))
add('U5','74xGxx','74LVC1G17','SN74LVC1G17DBVR','Package_TO_SOT_SMD:SOT-23-5',{1:None,2:'REARM_RC',3:G,4:'REARM_CLK',5:S},(160.02,185.42),'SN74LVC1G17DBVR','https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf',1.45)
cc('C6',S,G,(165.1,241.3));rr('R8','100k 1%','MCU_REARM',G,(114.3,241.3),'RC0603FR-07100KL')
# High-side PMOS, two series NPN sinks: latch AND current power/thermal permission.
add('Q1','Transistor_FET','AO3401A','AO3401A',SOT,{1:'COIL_GATE',2:'+5V_ISO',3:'COIL_5V'},(284.48,180.34),'AO3401A','https://www.aosmd.com/res/data_sheets/AO3401A.pdf',1.12)
rr('R9','47k 1%','+5V_ISO','COIL_GATE',(248.92,180.34),'RC0603FR-0747KL')
add('Q2','Transistor_BJT','MMBT3904','MMBT3904',SOT,{1:'ARM_B',2:'SINK_MID',3:'COIL_GATE'},(284.48,213.36),'MMBT3904,215','https://assets.nexperia.com/documents/data-sheet/MMBT3904.pdf',1.1)
add('Q3','Transistor_BJT','MMBT3904','MMBT3904',SOT,{1:'READY_B',2:G,3:'SINK_MID'},(284.48,246.38),'MMBT3904,215','https://assets.nexperia.com/documents/data-sheet/MMBT3904.pdf',1.1)
rr('R10','10k 1%',A,'ARM_B',(218.44,210.82),'RC0603FR-0710KL');rr('R11','100k 1%','ARM_B','SINK_MID',(248.92,210.82),'RC0603FR-07100KL')
rr('R12','47k 1%',PG,'READY_B',(218.44,246.38),'RC0603FR-0747KL');rr('R13','100k 1%','READY_B',G,(248.92,246.38),'RC0603FR-07100KL')
add('J1','Connector_Generic','Conn_01x06','HOST INTERLOCK','Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical',{1:'+5V_ISO',2:S,3:G,4:'MCU_REARM',5:A,6:PG},(365.76,203.2),'TSW-106-07-G-S','https://www.samtec.com/products/tsw',8.38)
add('J2','Connector_Generic','Conn_01x02','SAFE COIL FEED','Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',{1:'COIL_5V',2:G},(365.76,241.3),'TSW-102-07-G-S','https://www.samtec.com/products/tsw',8.38)
add('U6','74xGxx','74LVC1G17','SN74LVC1G17DBVR','Package_TO_SOT_SMD:SOT-23-5',{1:None,2:'READY_RAW',3:G,4:PG,5:S},(335.28,137.16),'SN74LVC1G17DBVR','https://www.ti.com/lit/ds/symlink/sn74lvc1g17.pdf',1.45)
cc('C7',S,G,(284.48,137.16))
# Local-only service reset: no remote rearm path or required MCU GPIO.
parts=[c for c in parts if c['ref'] not in ['R6','R8','D1','J1','J2']]
add('J1','Connector_Generic','Conn_01x04','MAIN 4-WIRE COIL INTERLOCK','Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical',{1:'+5V_ISO',2:S,3:G,4:'COIL_5V'},(365.76,203.2),'TSW-104-07-G-S','https://www.samtec.com/products/tsw',8.38)
for ref,net,xy in [('TP1',A,(43.18,241.3)),('TP2',PG,(104.14,241.3))]:
 add(ref,'Connector','TestPoint',net,'TestPoint:TestPoint_Pad_D1.0mm',{1:net},xy,'PCB TEST PAD ONLY','',0)
# Remote head uses low-profile soldered pigtail lands, no tall connector body.
for c in parts:
 if c['ref']=='J4':
  c.update(value='SENSOR PIGTAIL',footprint='Thermal:Sensor_Pigtail_3xP2.54',mpn='Soldered insulated pigtail / strain relief HOLD',datasheet='',height_mm=2.0)
fpdir=R/'Thermal.pretty';fpdir.mkdir(exist_ok=True)
sfp='(footprint "Sensor_Pigtail_3xP2.54" (version 20241229) (generator "pcbnew") (layer "F.Cu") (attr smd) (property "Reference" "REF**" (at 0 -2 0) (layer "F.SilkS") (effects (font (size .7 .7) (thickness .12)))) (property "Value" "PIGTAIL" (at 0 7 0) (layer "F.Fab") (effects (font (size .7 .7) (thickness .12)))) (fp_rect (start -1.1 -1.1) (end 1.1 6.18) (stroke (width .1) (type default)) (fill none) (layer "F.Fab")) (fp_rect (start -1.2 -1.2) (end 1.2 6.28) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))'
for pn,y in [(1,0),(2,2.54),(3,5.08)]:sfp+=f'(pad "{pn}" smd rect (at 0 {y}) (size 2.0 1.4) (layers "F.Cu" "F.Paste" "F.Mask"))'
(fpdir/'Sensor_Pigtail_3xP2.54.kicad_mod').write_text(sfp+')')
(R/'fp-lib-table').write_text('(fp_lib_table (lib (name "Thermal") (type "KiCad") (uri "${KIPRJMOD}/Thermal.pretty") (options "") (descr "Sensor pigtail lands")))')
# Embedded library and compact labeled schematic.
syms={};items=[];ends={}
for c in parts:
 name=c['name'];key='Thermal:'+name;s=copy.deepcopy(c['symbol']);s[1]=q(key);syms[key]=ser(s);ref=c['ref'];x,y=c['sch'];ins=f'(symbol (lib_id {q(key)}) (at {x} {y} 0) (unit 1) (in_bom {"no" if ref.startswith("W") else "yes"}) (on_board {"no" if ref.startswith("W") else "yes"}) (uuid {uid(ref)})'
 top=max(v['at'][1] for v in c['pin_geometry']);passive=name in ['R','C']
 for pn,pv,hide in [('Reference',ref,False),('Value',c['value'],False),('Footprint',c['footprint'],True),('Datasheet',c['datasheet'],True)]:
  px=x+(6.35 if passive else 20.32 if ref.startswith(('U','Q')) else 0);py=y+(-1.27 if pn=='Reference' else 2.54) if passive else y-top-(7.62 if pn=='Reference' else 5.08)
  ins+=f'(property {q(pn)} {q(pv)} (at {px} {py} 0) (effects (font (size 1.0 1.0))'+(' (hide yes)' if hide else '')+'))'
 for pin in c['pin_geometry']:ins+=f'(pin {q(pin["number"])} (uuid {uid(ref+pin["number"])}))'
 ins+=f'(instances (project "thermal_interlock" (path "/{uid("sheet")}" (reference {q(ref)}) (unit 1)))))';items.append(ins)
 for pin in c['pin_geometry']:
  no=pin['number'];px,py,ang=pin['at'];a=(round(x+px,5),round(y-py,5));n=c['pins'].get(no)
  if n is None:items.append(f'(no_connect (at {a[0]} {a[1]}) (uuid {uid(ref+no+"nc")}))');continue
  rad=math.radians(ang);z=(round(a[0]-5.08*math.cos(rad),5),round(a[1]+5.08*math.sin(rad),5));ends[(ref,no)]=z
  items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {z[0]} {z[1]})) (stroke (width 0) (type default)) (uuid {uid(ref+no+"w")}))')
  items.append(f'(label {q(n)} (at {z[0]} {z[1]} 0) (effects (font (size .9 .9)) (justify {"right" if ang==0 else "left"} bottom)) (uuid {uid(ref+no+"n")}))')
# Explicit short series gate-sink wiring reinforces functional topology.
for ra,pa,rb,pb in [('Q1','1','Q2','3'),('Q2','2','Q3','3')]:
 a=ends[(ra,pa)];z=ends[(rb,pb)];mid=(a[0],z[1])
 for i,(aa,zz) in enumerate([(a,mid),(mid,z)]):
  if aa!=zz:items.append(f'(wire (pts (xy {aa[0]} {aa[1]}) (xy {zz[0]} {zz[1]})) (stroke (width 0) (type default)) (uuid {uid(ra+rb+str(i))}))')
for i,(n,x) in enumerate([(S,22.86),(G,53.34),('+5V_ISO',83.82),(H,114.3),(HG,144.78)]):
 s=lib('power','PWR_FLAG');s[1]=q('Thermal:PWR_FLAG');syms['Thermal:PWR_FLAG']=ser(s);ref='#FLG0'+str(i+1)
 items.append(f'(symbol (lib_id "Thermal:PWR_FLAG") (at {x} 121.92 0) (unit 1) (in_bom no) (on_board no) (uuid {uid(ref)}) (property "Reference" "{ref}" (at {x} 121.92 0) (effects (font (size 1 1)) (hide yes))) (property "Value" "PWR_FLAG" (at {x} 116.84 0) (effects (font (size 1 1)))) (instances (project "thermal_interlock" (path "/{uid("sheet")}" (reference "{ref}") (unit 1)))))')
 items.append(f'(label {q(n)} (at {x} 121.92 0) (effects (font (size 1 1)) (justify left bottom)) (uuid {uid(ref+"l")}))')
for text,x,y,size in [('REV B HARDWARE THERMAL TRIP + LOCAL PHYSICAL REARM ONLY',12.7,15.24,2),('DEVELOPMENT CANDIDATE - NO ENERGIZATION OR FABRICATION RELEASE',12.7,22.86,1.4),('01  REMOTE TEMPERATURE HEAD',12.7,33.02,1.3),('02  WIRE-OPEN FAIL-LOW',106.68,33.02,1.3),('03  POWER + THERMAL SETTLING',195.58,33.02,1.3),('04  ASYNCHRONOUS TRIP LATCH',299.72,33.02,1.3),('05  FRESH REARM EDGE (DO NOT GATE CLOCK WITH READY)',12.7,162.56,1.3),('06  SERIES COIL FEED PERMISSION',223.52,152.4,1.3),('J1.4 replaces original relay-coil +5V feed. Flyback diode cathode MUST move to J1.4.',12.7,267.97,1.1),('A coil interlock cannot interrupt welded load contacts. Separate qualified line-series thermal cutoff remains required.',12.7,275.59,1.1)]:items.append(f'(text {q(text)} (at {x} {y} 0) (effects (font (size {size} {size})) (justify left)) (uuid {uid(text)}))')
(R/'thermal_interlock.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {uid("sheet")}) (paper "A3") (title_block (title "CarbonMirror Rev B hardware thermal interlock") (rev "B-CANDIDATE / HOLD")) (lib_symbols '+''.join(syms.values())+')'+''.join(items)+')')
(R/'Thermal.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '+''.join(v.replace(q(k),q(k.split(':')[1]),1) for k,v in syms.items())+')')
(R/'sym-lib-table').write_text('(sym_lib_table (lib (name "Thermal") (type "KiCad") (uri "${KIPRJMOD}/Thermal.kicad_sym") (options "") (descr "Manufacturer-pin-checked thermal logic")))')
manifest={'status':'DEVELOPMENT_CANDIDATE_NOT_ENERGIZABLE','components':[{k:v for k,v in c.items() if k!='symbol'} for c in parts],'candidate_controller_reservation_mm':[45,35,1.6],'candidate_sensor_head_reservation_mm':[12,12,1.6],'board_geometry_verified':True,'assembled_insulation_harness_qualified':False,'sensor_head_assembly':{'orientation':'component face rear; smooth B.Cu side to qualified insulating pad; rotate 180 degrees about local Y for case integration','pigtail_exit':'F.Cu SMD lands, rear-facing in installed orientation','contact_side_protrusion':'no solder/wire protrusions; via fill/tenting and flatness qualification HOLD','component_face_wire_reserve_mm':2,'contact_island_B_Cu_kicad_mm':[1.2,4.3,4.5,6.9],'contact_island_net':'GND_HEAD','thermal_vias_mm':[[1.6,4.7],[2.4,4.7],[3.4,4.7],[4.2,4.7]],'process_qualification':'HOLD'},'additional_controller_GPIO_required':0,'main_header_crossmap':{'J1.1':'MAIN_J3.7','J1.2':'MAIN_J3.1','J1.3':'MAIN_J3.11','J1.4':'MAIN_J3.10'},'supply_assumptions':{'logic_V':[3.135,3.465],'coil_V':[4.75,5.25],'coil_current_upper_A':.15},'host_pins':{'J1.1':'+5V_ISO','J1.2':S,'J1.3':G,'TP1':A,'TP2':PG,'J1.4':'COIL_5V'},'latched_permission':'!READY => Q=0 asynchronously; READY && fresh REARM edge => Q=1; else hold','coil_permission':'Q1 ON only when Q2 (Q) AND Q3 (READY) sink gate; original low-side RELAY_CMD remains required','rearm_policy':'Local physical button only; no MCU rearm connection. Requires press after every power restoration.', 'wire_open_coverage':'THERM_RETURN open goes low at R2; +3V3_HEAD open removes head pullup. Sensor ground opening/internal stuck-high not covered.'}
(R/'pin_net_manifest.json').write_text(json.dumps(manifest,indent=2))
with (R/'bom.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Reference','Value','MPN candidate','Footprint','Source','Status'])
 for c in parts:
  if not c['ref'].startswith('W'):w.writerow([c['ref'],c['value'],c['mpn'],c['footprint'],c['datasheet'],'UNRELEASED / SCHEMATIC ONLY'])
proj=json.loads((R.parents[1]/'carbonmirror.kicad_pro').read_text());proj['meta']={'filename':'thermal_interlock.kicad_pro','version':1};(R/'thermal_interlock.kicad_pro').write_text(json.dumps(proj,indent=2))
print('Thermal schematic generated:',len(parts),'parts including off-board harness models')
