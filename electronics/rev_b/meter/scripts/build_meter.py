#!/usr/bin/python3
"""Rev B meter source generator. Development only; no manufacturing release."""
import re,json,uuid,copy,csv,math,sys
from pathlib import Path
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]; BASE=ROOT.parents[1]; OUT=ROOT/'exports'; OUT.mkdir(exist_ok=True)
# Reuse the transparent upstream-library parser, not the baseline generator.
s= (BASE/'scripts/build_electronics.py').read_text(); start=s.index('def uid(');end=s.index('parts=[]');exec(s[start:end]);
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'carbentra/rev-b-meter/'+s))
parts=[]
def add(ref,lib,name,value,fp,nets,pos,sch,mpn,url,height=1,body=None):
 sym=libsym(lib,name);pins=[]
 for sub in children(sym,'symbol'):
  for pin in children(sub,'pin'):
   pins.append({'number':atom(child(pin,'number')[1]),'name':atom(child(pin,'name')[1]),'at':list(map(float,child(pin,'at')[1:4])),'type':pin[1]})
 parts.append(dict(ref=ref,lib=lib,name=name,value=value,fp=fp,nets={str(k):v for k,v in nets.items()},pos=pos,sch=sch,mpn=mpn,url=url,height=height,body=body,pins=pins,sym=sym))
# Pin-correct custom DC/DC symbol from RECOM RxxCTxx Rev3/2022 pad table.
def custom_sym(name,pinlist):
 txt=f'(symbol "{name}" (pin_names (offset 0.5)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 16 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 14 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_0_1" (rectangle (start -10 12) (end 10 -12) (stroke (width 0.254) (type default)) (fill (type background)))) (symbol "{name}_1_1" '
 for num,nm,typ,x,y,a in pinlist:txt+=f'(pin {typ} line (at {x} {y} {a}) (length 2.54) (name "{nm}" (effects (font (size 1 1)))) (number "{num}" (effects (font (size 1 1)))))'
 return parse(txt+'))')
pspins=[(1,'CTRL','input',-12.7,10.16,0),(2,'VIN-','power_in',-12.7,5.08,0),(3,'VIN+','power_in',-12.7,7.62,0),(4,'SYNC','input',-12.7,2.54,0),(5,'SYNC_OK','open_collector',-12.7,0,0),(6,'NC','no_connect',-12.7,-2.54,0),(7,'NC','no_connect',-12.7,-5.08,0),(8,'NC','no_connect',-12.7,-7.62,0),(9,'VOUT-','power_out',12.7,-7.62,180),(10,'NC','no_connect',12.7,-5.08,180),(11,'NC','no_connect',12.7,-2.54,180),(12,'NC','no_connect',12.7,0,180),(13,'TRIM','input',12.7,2.54,180),(14,'VOUT+','power_out',12.7,5.08,180),(15,'VOUT-','passive',12.7,7.62,180),(16,'VOUT-','passive',12.7,10.16,180)]
cache['RevB']={'R05CT05S':custom_sym('R05CT05S',pspins)}
R='Resistor_SMD:R_0805_2012Metric';C='Capacitor_SMD:C_0805_2012Metric';term='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal'
ATM='https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/Atmel-46002-SE-M90E26-Datasheet.pdf'
add('U1','Sensor_Energy','ATM90E26-YU','ATM90E26-YU','Package_SO:SSOP-28_5.3x10.2mm_P0.65mm',{1:'HOT_GND',2:'HOT_GND',3:'HOT_3V3',4:'HOT_RESET',5:'HOT_AVDD',6:'HOT_GND',7:'HOT_GND',8:'HOT_GND',9:'HOT_GND',10:'HOT_I1P',11:'HOT_I1N',12:'HOT_GND',13:'HOT_VREF',14:'HOT_GND',15:'HOT_VN',16:'HOT_VP',22:'HOT_XIN',23:'HOT_XOUT',24:'HOT_CS',25:'HOT_SCLK',26:'HOT_MISO',27:'HOT_MOSI',28:'HOT_3V3'},(36,25,0),(210,90),'ATM90E26-YU',ATM,2.0,[5.3,10.2])
add('U2','Isolator','ISO6741','ISO6741DWR','RevB:ISO6741_DW_8p1',{1:'ISO_3V3',2:'ISO_GND',3:'ISO_SCLK',4:'ISO_MOSI',5:'ISO_CS',6:'ISO_MISO',7:'ISO_3V3',8:'ISO_GND',9:'HOT_GND',10:'HOT_3V3',11:'HOT_MISO',12:'HOT_CS',13:'HOT_MOSI',14:'HOT_SCLK',15:'HOT_GND',16:'HOT_3V3'},(56,28,180),(320,85),'ISO6741DWR','https://www.ti.com/lit/ds/symlink/iso6741.pdf',2.65,[7.5,10.3])
add('PS1','RevB','R05CT05S','R05CT05S-R / 3.3V','RevB:R05CT05S_8p1',{1:'ISO_5V',2:'ISO_GND',3:'ISO_5V',13:'HOT_GND',14:'HOT_3V3',9:'HOT_GND',15:'HOT_GND',16:'HOT_GND'},(56,11,180),(320,185),'R05CT05S-R','https://recom-power.com/pdf/Econoline/RxxCTxx.pdf',2.65,[7.5,10.3])
# Main path: protected line is HOT_GND, shunt feeds relay common. Kelvin pads never carry load current.
add('RS1','Device','R_Shunt','1mR / 1% / 8W','RevB:CSS4J_4026',{1:'HOT_GND',2:'HOT_SENSE_UP',3:'HOT_SENSE_DOWN',4:'HOT_LOAD'},(18,25,270),(80,75),'CSS4J-4026R-1L00FE','https://www.bourns.com/docs/product-datasheets/css4j-4026.pdf',2.92,[10.31,6.9])
add('J1','Connector_Generic','Conn_01x02','PROTECTED L / TO RELAY',term,{1:'HOT_LOAD',2:'HOT_GND'},(7,29,90),(35,75),'1711725','https://www.phoenixcontact.com/en-pc/products/pcb-terminal-block-mkds-3-2-508-1711725',18,[10.16,11.2])
add('J2','Connector_Generic','Conn_01x02','N SENSE / NC',term,{1:'HOT_N'},(8,12,0),(35,150),'1711725','https://www.phoenixcontact.com/en-pc/products/pcb-terminal-block-mkds-3-2-508-1711725',18,[10.16,11.2])
add('J3','Connector_Generic','Conn_01x08','CONTROLLER - ISOLATED','Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical',{1:'ISO_3V3',2:'ISO_GND',3:'ISO_SCLK',4:'ISO_MOSI',5:'ISO_MISO',6:'ISO_CS',7:'ISO_5V',8:'ISO_GND'},(70,11,0),(385,90),'TSW-108-07-G-S','https://www.samtec.com/products/tsw',8,[2.54,20.32])
def resistor(ref,value,a,b,pos,sch,fp=R,mpn=None):
 add(ref,'Device','R',value,fp,{1:a,2:b},pos,sch,mpn or ('TNPW0805'+{'100R':'100R','1k':'1K00','10k':'10K0','0R':'0R00'}[value]+'BEEA'),'https://www.vishay.com/docs/28758/tnpw_e3.pdf',.65,[3.2,1.6] if '1206' in fp else [2,1.25])
def cap(ref,value,a,b,pos,sch):add(ref,'Device','C',value,C,{1:a,2:b},pos,sch,'GRM21-series '+value+' candidate','https://www.murata.com/en-us/products/capacitor/ceramiccapacitor',1.25,[2,1.25])
resistor('R1','100R','HOT_SENSE_DOWN','HOT_I1P',(24,25,0),(120,65));resistor('R2','100R','HOT_SENSE_UP','HOT_I1N',(24,21,0),(120,90))
cap('C1','330nF 16V','HOT_I1P','HOT_GND',(28,25,90),(150,65));cap('C2','330nF 16V','HOT_I1N','HOT_GND',(28,21,90),(150,90))
# Four precision resistors distribute continuous voltage; impulse qualification is a separate gate.
for i in range(4):resistor('RV'+str(i+1),'249k','HOT_N' if i==0 else 'HOT_DIV'+str(i),'HOT_DIV'+str(i+1),(20+5.5*i,8,0),(65+i*30,150),'Resistor_SMD:R_1206_3216Metric','TNPW1206249KBEEA')
resistor('RV5','1k','HOT_DIV4','HOT_GND',(40,8,90),(185,150));resistor('RV6','1k','HOT_DIV4','HOT_VP',(39,13,0),(210,150));resistor('RV7','1k','HOT_GND','HOT_VN',(39,17,0),(210,180))
cap('CV1','33nF 16V','HOT_VP','HOT_GND',(44,13,90),(245,150));cap('CV2','33nF 16V','HOT_VN','HOT_GND',(44,17,90),(245,180))
resistor('R3','0R','HOT_3V3','HOT_AVDD',(29,32,0),(175,220),mpn='RC0805JR-070RL')
cap('C3','100nF 16V','HOT_AVDD','HOT_GND',(29,35,0),(200,220));cap('C4','100nF 16V','HOT_3V3','HOT_GND',(29,28,0),(225,220));cap('C5','10uF 10V','HOT_3V3','HOT_GND',(27,39,0),(250,220))
cap('C6','1uF 16V','HOT_VREF','HOT_GND',(40,34,0),(200,255));cap('C7','1nF C0G','HOT_VREF','HOT_GND',(44,34,0),(230,255))
resistor('R4','10k','HOT_3V3','HOT_RESET',(20,35,90),(100,235));cap('C8','100nF 16V','HOT_RESET','HOT_GND',(23,36,90),(130,235))
add('Y1','Device','Crystal','8.192MHz CL18pF','Crystal:Crystal_SMD_HC49-SD',{1:'HOT_XIN',2:'HOT_XOUT'},(38,40,0),(60,230),'ABLS-8.192MHZ-B2-T','https://abracon.com/Resonators/abls.pdf',4.9,[11.4,4.7])
cap('CX1','27pF C0G','HOT_XIN','HOT_GND',(33,35,90),(35,255));cap('CX2','27pF C0G','HOT_XOUT','HOT_GND',(36,35,90),(65,255))
for ref,val,a,b,pos,sch in [('CP1','10uF 16V','ISO_5V','ISO_GND',(65,6,0),(280,235)),('CP2','100nF 16V','ISO_5V','ISO_GND',(65,9,0),(310,235)),('CP3','10uF 10V','HOT_3V3','HOT_GND',(47,6,0),(350,235)),('CP4','100nF 16V','HOT_3V3','HOT_GND',(47,9,0),(380,235)),('CI1','100nF 16V','ISO_3V3','ISO_GND',(65,22,90),(285,125)),('CI2','100nF 16V','HOT_3V3','HOT_GND',(47,25,90),(350,125))]:cap(ref,val,a,b,pos,sch)
# Explicit idle levels: default-high isolation keeps CS deasserted on input loss.
resistor('R5','10k','HOT_3V3','HOT_CS',(45,30,0),(280,50));resistor('R6','10k','ISO_3V3','ISO_CS',(65,28,90),(350,50))
# Local library footprints. SOP footprints intentionally use documented HV 8.1mm pad gap.
def newfp(name,body,pads):
 f=p.FOOTPRINT(None);f.SetFPID(p.LIB_ID('RevB',name));f.SetValue(name)
 for num,x,y,w,h in pads:
  pd=p.PAD(f);pd.SetNumber(str(num));pd.SetAttribute(p.PAD_ATTRIB_SMD);pd.SetShape(p.PAD_SHAPE_RECT);pd.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));pd.SetSize(p.VECTOR2I(p.FromMM(w),p.FromMM(h)));ls=p.LSET();ls.AddLayer(p.F_Cu);ls.AddLayer(p.F_Paste);ls.AddLayer(p.F_Mask);pd.SetLayerSet(ls);f.Add(pd)
 for layer,extra in [(p.F_Fab,0),(p.F_CrtYd,.5)]:
  w,h=body;w=w/2+extra;h=h/2+extra
  for aa,bb in [((-w,-h),(w,-h)),((w,-h),(w,h)),((w,h),(-w,h)),((-w,h),(-w,-h))]:
   ln=p.PCB_SHAPE();ln.SetShape(p.SHAPE_T_SEGMENT);ln.SetStart(p.VECTOR2I(p.FromMM(aa[0]),p.FromMM(aa[1])));ln.SetEnd(p.VECTOR2I(p.FromMM(bb[0]),p.FromMM(bb[1])));ln.SetWidth(p.FromMM(.05));ln.SetLayer(layer);f.Add(ln)
 p.PCB_IO_KICAD_SEXPR().FootprintSave(str(ROOT/'RevB.pretty'),f);return f
sop=[(i+1,-4.875,-4.445+i*1.27,1.65,.6) for i in range(8)]+[(16-i,4.875,-4.445+i*1.27,1.65,.6) for i in range(8)]
newfp('R05CT05S_8p1',[11.4,10.5],sop);newfp('ISO6741_DW_8p1',[11.4,10.5],sop)
newfp('CSS4J_4026',[10.6,7.3],[(1,-4.025,.85,2.55,5.6),(4,4.025,.85,2.55,5.6),(2,-4.025,-2.75,2.55,.8),(3,4.025,-2.75,2.55,.8)])
# Board source: all nets explicit, load-carrying copper will be reviewed separately.
if '--schematic-only' not in sys.argv:
 b=p.BOARD();b.GetDesignSettings().SetBoardThickness(p.FromMM(1.6));names=sorted(set(n for c in parts for n in c['nets'].values()));nets={}
 for n in names:net=p.NETINFO_ITEM(b,n);b.Add(net);nets[n]=net
 for c in parts:
  lib,name=c['fp'].split(':');fp=p.FootprintLoad(str(ROOT/'RevB.pretty') if lib=='RevB' else '/usr/share/kicad/footprints/'+lib+'.pretty',name)
  if not fp:raise RuntimeError(c['fp'])
  fp.SetReference(c['ref']);fp.SetValue(c['value']);fp.SetPosition(p.VECTOR2I(p.FromMM(c['pos'][0]),p.FromMM(c['pos'][1])));fp.SetOrientationDegrees(c['pos'][2]);fp.SetPath(p.KIID_PATH('/'+uid('sheet')+'/'+uid(c['ref'])))
  for pd in fp.Pads():
   if pd.GetNumber() in c['nets']:pd.SetNet(nets[c['nets'][pd.GetNumber()]])
  fp.Reference().SetLayer(p.F_Fab);fp.Value().SetVisible(False);b.Add(fp)
 for i,(x,y) in enumerate([(3,3),(72,3),(3,42),(72,42)]):
  f=p.FootprintLoad('/usr/share/kicad/footprints/MountingHole.pretty','MountingHole_2.2mm_M2');f.SetReference('H'+str(i+1));f.Reference().SetLayer(p.F_Fab);f.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));b.Add(f)
 for a,z in [((0,0),(75,0)),((75,0),(75,45)),((75,45),(0,45)),((0,45),(0,0))]:
  ln=p.PCB_SHAPE();ln.SetShape(p.SHAPE_T_SEGMENT);ln.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));ln.SetEnd(p.VECTOR2I(p.FromMM(z[0]),p.FromMM(z[1])));ln.SetLayer(p.Edge_Cuts);ln.SetWidth(p.FromMM(.05));b.Add(ln)
 p.SaveBoard(str(ROOT/'meter.kicad_pcb'),b)
# Schematic: functional A3 groups, symbols embedded, actual pins/nets.
symbols={};items=[];ends={}
for c in parts:
 key='RevB:'+c['name'];sym=copy.deepcopy(c['sym']);sym[1]=q(key);symbols[key]=ser(sym);x,y=[round(v/1.27)*1.27 for v in c['sch']]
 angle=90 if c['ref'] in ('R1','R2','RV1','RV2','RV3','RV4','R3') else 0
 inst=f'(symbol (lib_id {q(key)}) (at {x} {y} {angle}) (unit 1) (in_bom yes) (on_board yes) (uuid {uid(c["ref"])})'
 top=max(pp['at'][1] for pp in c['pins']);passive=c['name'] in ('R','C','Crystal','R_Shunt')
 for nm,val,dy,hide in [('Reference',c['ref'],-top-5,False),('Value',c['value'],-top-2,False),('Footprint',c['fp'],0,True),('Datasheet',c['url'],0,True)]:
  xx=x-12 if c['ref']=='RS1' else x+8 if passive else x+18 if c['ref'] in ('U1','U2') else x; yy=y+(-2 if nm=='Reference' else 2) if passive and not hide else y+dy
  inst+=f'(property {q(nm)} {q(val)} (at {xx} {yy} 0) (effects (font (size 1 1))'+(' (hide yes)' if hide else '')+'))'
 for pin in c['pins']:inst+=f'(pin {q(pin["number"])} (uuid {uid(c["ref"]+pin["number"])}))'
 inst+=f'(instances (project "meter" (path "/{uid("sheet")}" (reference {q(c["ref"])}) (unit 1)))))';items.append(inst)
 for pin in c['pins']:
  px,py,ang=pin['at'];px,py=(-py,px) if angle==90 else (px,py);ang=(ang+angle)%360;sx=x+px;sy=y-py;n=c['nets'].get(pin['number'])
  if not n:items.append(f'(no_connect (at {sx} {sy}) (uuid {uid(c["ref"]+pin["number"]+"nc")}))');continue
  rad=math.radians(ang);ex=round(sx-2.54*math.cos(rad),4);ey=round(sy+2.54*math.sin(rad),4);ends[(c['ref'],n)]=(ex,ey)
  items.append(f'(wire (pts (xy {sx} {sy}) (xy {ex} {ey})) (stroke (width 0) (type default)) (uuid {uid(c["ref"]+pin["number"]+"w")}))')
  items.append(f'(label {q(n)} (at {ex} {ey} 0) (effects (font (size .85 .85)) (justify {"right" if ang==0 else "left"} bottom)) (uuid {uid(c["ref"]+pin["number"]+"l")}))')
# Real local wires within functional groups; labels remain for cross-block nets.
def local(a,b,net,corner=None):
 aa=ends[(a,net)];zz=ends[(b,net)];pts=[aa,zz] if aa[0]==zz[0] or aa[1]==zz[1] else [aa,(round((aa[0]+zz[0])/2/1.27)*1.27,aa[1]),(round((aa[0]+zz[0])/2/1.27)*1.27,zz[1]),zz]
 if corner:pts=[aa,(corner,aa[1]),(corner,zz[1]),zz]
 for i,(u,v) in enumerate(zip(pts,pts[1:])):
  if u==v:continue
  items.append(f'(wire (pts (xy {u[0]} {u[1]}) (xy {v[0]} {v[1]})) (stroke (width 0) (type default)) (uuid {uid("local"+a+b+net+str(i))}))')
for a,b,n in [('RV1','RV2','HOT_DIV1'),('RV2','RV3','HOT_DIV2'),('RV3','RV4','HOT_DIV3'),('RV4','RV5','HOT_DIV4'),('R1','C1','HOT_I1P'),('R2','C2','HOT_I1N'),('RV6','CV1','HOT_VP'),('RV7','CV2','HOT_VN'),('R4','C8','HOT_RESET'),('C6','C7','HOT_VREF'),('CP1','CP2','ISO_5V'),('CP1','CP2','ISO_GND'),('CP3','CP4','HOT_3V3'),('CP3','CP4','HOT_GND')]:local(a,b,n)
for j,n in enumerate(['ISO_3V3','ISO_5V','ISO_GND','HOT_AVDD']):
 key='RevB:PWR_FLAG';ss=libsym('power','PWR_FLAG');ss[1]=q(key);symbols[key]=ser(ss);x=285.75+j*30.48;y=265.43;ref='#FLG0'+str(j+1)
 items.append(f'(symbol (lib_id "{key}") (at {x} {y} 0) (unit 1) (in_bom no) (on_board no) (uuid {uid(ref)}) (property "Reference" "{ref}" (at {x} {y} 0) (effects (font (size 1 1)) (hide yes))) (property "Value" "PWR_FLAG" (at {x} {y-3.81} 0) (effects (font (size 1 1)))) (instances (project "meter" (path "/{uid("sheet")}" (reference "{ref}") (unit 1)))))')
 items.append(f'(label "{n}" (at {x} {y} 0) (effects (font (size 1 1)) (justify left bottom)) (uuid {uid(ref+"label")}))')
for txt,x,y in [('CARBENTRA REV B - METER - DEVELOPMENT / ENERGIZATION HOLD',15,15),('HOT_* = LIVE LINE REFERENCED. Never connect hot ground to PE, USB, isolated ground or accessible metal.',15,23),('Protected line -> Kelvin shunt -> relay COM. Voltage samples input L-N; separate ACPL-K376 senses switched output.',15,30),('01  LOAD SHUNT + MATCHED RC',15,43),('02  VOLTAGE DIVIDER + FILTER',15,120),('03  ATM90E26 AFE',170,43),('04  REINFORCED SPI BARRIER',280,38),('05  ISOLATED POWER 5V -> 3.3V',280,155),('06  CLOCK / RESET / DECOUPLING',15,202)]:items.append(f'(text {q(txt)} (at {x} {y} 0) (effects (font (size 1.2 1.2)) (justify left)) (uuid {uid(txt)}))')
(ROOT/'meter.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {uid("sheet")}) (paper "A3") (title_block (title "CARBENTRA REV B isolated metering") (rev "ENGINEERING CANDIDATE")) (lib_symbols '+''.join(symbols.values())+')'+''.join(items)+')')
(ROOT/'RevB.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") '+''.join(v.replace(q(k),q(k.split(':')[1]),1) for k,v in symbols.items())+')')
(ROOT/'sym-lib-table').write_text('(sym_lib_table (lib (name "RevB") (type "KiCad") (uri "${KIPRJMOD}/RevB.kicad_sym") (options "") (descr "Rev B symbols")))')
(ROOT/'fp-lib-table').write_text('(fp_lib_table (lib (name "RevB") (type "KiCad") (uri "${KIPRJMOD}/RevB.pretty") (options "") (descr "Datasheet-derived candidate footprints")))')
(ROOT/'circuit_manifest.json').write_text(json.dumps([{k:v for k,v in c.items() if k!='sym'} for c in parts],indent=2))
with (ROOT/'bom.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Reference','Value','MPN candidate','Footprint','Source','Release']);
 for c in parts:w.writerow([c['ref'],c['value'],c['mpn'],c['fp'],c['url'],'engineering candidate / hold'])
if '--schematic-only' not in sys.argv:(ROOT/'meter.kicad_dru').write_text('''(version 1)
(rule "minimum signal clearance" (constraint clearance (min 0.15mm)))
(rule "HOT to ISO barrier 8mm" (condition "(A.NetName == 'HOT_*' && B.NetName == 'ISO_*') || (B.NetName == 'HOT_*' && A.NetName == 'ISO_*')") (constraint clearance (min 8mm)))
''')
print(len(parts),'parts',len(set(n for c in parts for n in c['nets'].values())),'nets')
