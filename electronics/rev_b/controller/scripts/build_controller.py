#!/usr/bin/python3
"""Programmatic development-source generation. Never produces manufacturing files."""
import re,json,uuid,copy,csv,math,sys
from pathlib import Path
import pcbnew as p
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'exports'; OUT.mkdir(exist_ok=True)
def uid(s): return str(uuid.uuid5(uuid.NAMESPACE_URL,'carbonmirror/rev-b-controller/'+s))
def parse(s):
 t=re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',s); stack=[]; root=None
 for x in t:
  if x=='(':
   a=[]
   if stack: stack[-1].append(a)
   stack.append(a)
  elif x==')':
   root=stack.pop()
  else: stack[-1].append(x)
 return root
def atom(x): return json.loads(x) if x.startswith('"') else x
def q(x):return json.dumps(str(x))
def ser(v): return '('+' '.join(map(ser,v))+')' if isinstance(v,list) else v
def children(v,k):return [x for x in v if isinstance(x,list) and x[0]==k]
def child(v,k):return next((x for x in v if isinstance(x,list) and x[0]==k),None)
cache={}
def libsym(lib,name):
 if lib not in cache:cache[lib]={atom(x[1]):x for x in children(parse(Path('/usr/share/kicad/symbols',lib+'.kicad_sym').read_text()),'symbol')}
 s=copy.deepcopy(cache[lib][name]); ext=child(s,'extends')
 if ext:
  base=libsym(lib,atom(ext[1])); props={atom(x[1]):x for x in children(base,'property')};props.update({atom(x[1]):x for x in children(s,'property')})
  s=[s[0],s[1]]+list(props.values())+[x for x in base[2:] if not(isinstance(x,list) and x[0] in ('property','extends'))]
 for i,x in enumerate(children(s,'symbol')):x[1]=q(name+'_'+atom(x[1]).split('_')[-2]+'_'+atom(x[1]).split('_')[-1])
 return s
parts=[]
def add(ref,lib,name,value,fp,nets,pos,sch,mpn='',url='',height=1.2):
 s=libsym(lib,name); pins=[]
 for sub in children(s,'symbol'):
  for pin in children(sub,'pin'):
   pins.append({'number':atom(child(pin,'number')[1]),'name':atom(child(pin,'name')[1]),'at':list(map(float,child(pin,'at')[1:4])),'type':pin[1]})
 parts.append(dict(ref=ref,lib=lib,name=name,value=value,fp=fp,nets={str(k):v for k,v in nets.items()},pos=pos,sch=sch,mpn=mpn,url=url,height=height,pins=pins,sym=s))
R='Resistor_SMD:R_0603_1608Metric';C='Capacitor_SMD:C_0805_2012Metric';H='Connector_PinHeader_2.54mm:PinHeader_1x'
def res(ref,value,a,b,pos,sch):add(ref,'Device','R',value,R,{1:a,2:b},pos,sch,{'100R':'RC0603FR-07100RL','100k':'RC0603FR-07100KL','10k':'RC0603FR-0710KL','4.7k':'RC0603FR-074K7L','1k':'RC0603FR-071KL'}[value],'https://www.yageo.com/en/ProductSearch',.5)
def cap(ref,value,a,b,pos,sch):add(ref,'Device','C',value,C,{1:a,2:b},pos,sch,'GRM21-series candidate','https://www.murata.com/en-us/products/capacitor/ceramiccapacitor',1.25)
add('PS1','Converter_ACDC','IRM-05-5','IRM-05-5','Converter_ACDC:Converter_ACDC_MeanWell_IRM-05-xx_THT',{1:'N',2:'L_AUX_FUSED',3:'GND_ISO',4:'+5V_ISO'},(4.6,23.2,0),(50,55),'IRM-05-5','https://www.meanwell.com/Upload/PDF/IRM-05/IRM-05-SPEC.PDF',21.5)
add('K1','Relay','RT314A03','RT314005 / 5V','Relay_THT:Relay_SPDT_Schrack-RT1-16A-FormC_RM5mm',{'A1':'COIL_5V','A2':'COIL_LOW',11:'L_FUSED',12:'L_NC_UNUSED',14:'L_SWITCHED'},(52,43,180),(140,55),'RT314005 / 1-1649328-0','https://www.te.com/en/product-1-1649328-0.html',15.7)
add('U1','RF_Module','ESP32-C3-WROOM-02U','ESP32-C3-WROOM-02U-N4','RF_Module:ESP32-C3-WROOM-02U',{1:'+3V3_ISO',2:'EN',3:'SPI_SCLK',4:'SPI_MISO',5:'SPI_MOSI',6:'SPI_CS',7:'BOOT8',8:'BOOT9',9:'GND_ISO',10:'RELAY_CMD',11:'UART_RX',12:'UART_TX',13:'BUTTON',14:'LED_CMD',15:'OUTPUT_PRESENT_N',16:'BOOT2',17:'I2C_SCL',18:'I2C_SDA',19:'GND_ISO'},(59,17,0),(250,65),'ESP32-C3-WROOM-02U-N4','https://www.espressif.com/sites/default/files/documentation/esp32-c3-wroom-02_datasheet_en.pdf',2.4)
add('U2','Regulator_Switching','AP63203WU','AP63203WU-7','Package_TO_SOT_SMD:TSOT-23-6',{1:'+3V3_ISO',2:'+5V_ISO',3:'+5V_ISO',4:'GND_ISO',5:'SW',6:'BST'},(49,33,0),(350,55),'AP63203WU-7','https://www.diodes.com/datasheet/download/AP63200-AP63201-AP63203-AP63205.pdf',1)
add('L1','Device','L','3.9uH','Inductor_SMD:L_Bourns-SRN4018',{1:'SW',2:'+3V3_ISO'},(54,33,0),(440,55),'SRN4018-3R9M','https://www.bourns.com/docs/product-datasheets/srn4018.pdf',1.8)
cap('C1','10uF 16V','+5V_ISO','GND_ISO',(48.5,27,90),(50,120));cap('C2','100nF 16V','BST','SW',(51,28,90),(140,120));cap('C3','22uF 10V','+3V3_ISO','GND_ISO',(59,30,90),(250,120));cap('C4','22uF 10V','+3V3_ISO','GND_ISO',(63,30,90),(350,120));cap('C5','100nF 10V','+3V3_ISO','GND_ISO',(47,10,90),(440,120))
add('Q1','Transistor_FET','AO3400A','AO3400A','Package_TO_SOT_SMD:SOT-23',{1:'GATE',2:'GND_ISO',3:'COIL_LOW'},(59,45,0),(50,185),'AO3400A','https://www.aosmd.com/res/data_sheets/AO3400A.pdf',1.1)
add('D1','Device','D_Schottky','SS14','Diode_SMD:D_SMA',{1:'COIL_5V',2:'COIL_LOW'},(61,37,0),(140,185),'SS14','https://www.vishay.com/docs/88746/ss12.pdf',2.4)
res('R1','100R','RELAY_CMD','GATE',(65,42,90),(250,185));res('R2','100k','GATE','GND_ISO',(63,44,90),(350,185));res('R3','10k','+3V3_ISO','EN',(48.2,14,90),(440,185));cap('C6','1uF 10V','EN','GND_ISO',(48.2,18,90),(50,250))
res('R4','10k','+3V3_ISO','BOOT9',(69,27,0),(140,250));res('R5','10k','+3V3_ISO','BOOT8',(69,31,0),(250,250));res('R6','10k','+3V3_ISO','BOOT2',(54,26,0),(350,250))
add('U3','Sensor_Temperature','TMP102xxDRL','TMP102AIDRLR','Package_TO_SOT_SMD:SOT-563',{1:'I2C_SCL',2:'GND_ISO',4:'GND_ISO',5:'+3V3_ISO',6:'I2C_SDA'},(58,55,0),(440,250),'TMP102AIDRLR','https://www.ti.com/lit/ds/symlink/tmp102.pdf',.6)
res('R7','4.7k','+3V3_ISO','I2C_SCL',(63,53,90),(50,315));res('R8','4.7k','+3V3_ISO','I2C_SDA',(63,57,90),(140,315));cap('C7','100nF 10V','+3V3_ISO','GND_ISO',(60,58,90),(350,315))
for ref,ns,pos,sch in [('J1',{1:'L_FUSED',2:'N'},(10,44.8,0),(440,315)),('J2',{1:'L_SWITCHED',2:'N'},(14,60,0),(50,375)),('J3',{1:'+3V3_ISO',2:'GND_ISO',3:'SPI_SCLK',4:'SPI_MOSI',5:'SPI_MISO',6:'SPI_CS',7:'+5V_ISO',8:'GND_ISO',9:'OUTPUT_PRESENT_N',10:'COIL_5V',11:'GND_ISO'},(68,36,0),(140,375)),('J4',{1:'GND_ISO',2:'UART_TX',3:'UART_RX',4:'BOOT9',5:'EN'},(46,62,90),(250,375)),('J5',{1:'L_AUX_FUSED',2:'N'},(18,5.5,0),(350,375))]:
 n=12 if ref=='J3' else len(ns);fp='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-3-2-5.08_1x02_P5.08mm_Horizontal' if ref in ('J1','J2','J5') else 'Connector_PinHeader_2.54mm:PinHeader_2x06_P2.54mm_Vertical' if ref=='J3' else H+f'{n:02d}_P2.54mm_Vertical'
 add(ref,'Connector_Generic','Conn_02x06_Odd_Even' if ref=='J3' else f'Conn_01x{n:02d}',{'J1':'LINE IN - terminal HOLD','J2':'SWITCHED OUT - HOLD','J3':'B SYSTEM HARNESS','J4':'DEBUG - MAINS DISCONNECTED','J5':'FUSED AUXILIARY INPUT'}[ref],fp,ns,pos,sch,'1711725' if ref in ('J1','J2','J5') else 'TSW-106-07-G-D' if ref=='J3' else 'Samtec TSW-1xx-07 candidate','https://www.phoenixcontact.com/en-pc/products/pcb-terminal-block-mkds-3-2-508-1711725' if ref in ('J1','J2','J5') else 'https://www.samtec.com/products/tsw',18 if ref in ('J1','J2','J5') else 8)
add('SW1','Switch','SW_Push','LOCAL BUTTON','Button_Switch_THT:SW_PUSH_6mm',{1:'BUTTON',2:'GND_ISO'},(32.75,61.15,0),(500,55),'B3F-1000 candidate','https://components.omron.com/us-en/products/switches/B3F',4.3)
add('LED1','Device','LED','STATUS LED GREEN','LED_THT:LED_D3.0mm',{1:'GND_ISO',2:'LED_A'},(34.73,3,0),(500,120),'WP710A10GD candidate','https://www.kingbrightusa.com/',5.3)
res('R10','10k','+3V3_ISO','BUTTON',(61,61,180),(500,185))
res('R11','1k','LED_CMD','LED_A',(42,4,0),(500,250))
if '--schematic-only' not in sys.argv:
 # Board
 b=p.BOARD(); b.GetDesignSettings().SetCopperLayerCount(2); b.GetDesignSettings().SetBoardThickness(p.FromMM(1.6))
 names=sorted(set(n for c in parts for n in c['nets'].values())); nets={}
 for n in names:net=p.NETINFO_ITEM(b,n);b.Add(net);nets[n]=net
 for c in parts:
  lib,name=c['fp'].split(':'); fp=p.FootprintLoad('/usr/share/kicad/footprints/'+lib+'.pretty',name)
  if not fp:raise RuntimeError(c['fp'])
  fp.SetReference(c['ref']);fp.SetValue(c['value']);fp.SetPosition(p.VECTOR2I(p.FromMM(c['pos'][0]),p.FromMM(c['pos'][1])));fp.SetOrientationDegrees(c['pos'][2]);fp.SetPath(p.KIID_PATH('/'+uid('sheet')+'/'+uid(c['ref'])))
  for pad in fp.Pads():
   num=pad.GetNumber()
   if num in c['nets']:pad.SetNet(nets[c['nets'][num]])
   if c['ref'] in ('J1','J2','J5'):pad.SetSize(p.VECTOR2I(p.FromMM(2.5),p.FromMM(2.5)))
  fp.Value().SetVisible(False);fp.Reference().SetLayer(p.F_Fab);fp.Reference().SetTextSize(p.VECTOR2I(p.FromMM(.8),p.FromMM(.8)))
  b.Add(fp)
 for i,(x,y) in enumerate([(5,5),(67,5),(67,63),(5,63)]):
  f=p.FootprintLoad('/usr/share/kicad/footprints/MountingHole.pretty','MountingHole_3.2mm_M3');f.SetReference('H'+str(i+1));f.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));b.Add(f)
 for a,z in [((0,0),(72,0)),((72,0),(72,68)),((72,68),(0,68)),((0,68),(0,0))]:
  s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));s.SetEnd(p.VECTOR2I(p.FromMM(z[0]),p.FromMM(z[1])));s.SetLayer(p.Edge_Cuts);s.SetWidth(p.FromMM(.05));b.Add(s)
 for txt,x,y,size in [('CARBONMIRROR DEV-B',35,65,1),('FABRICATION HOLD',23,2,1),('MAINS / UNROUTED',18,41,.8),('SELV CANDIDATE',59,34,.7),('NO PE ON PCB',19,33,.8)]:
  t=p.PCB_TEXT(b);t.SetText(txt);t.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));t.SetTextSize(p.VECTOR2I(p.FromMM(size),p.FromMM(size)));t.SetTextThickness(p.FromMM(.13));t.SetLayer(p.Dwgs_User);b.Add(t)
 p.SaveBoard(str(ROOT/'carbonmirror.kicad_pcb'),b)
 # Omit J5's clipped decorative silk, retaining Fab/courtyard/pads unchanged.
 tree=parse((ROOT/'carbonmirror.kicad_pcb').read_text())
 for fp in children(tree,'footprint'):
  ref=next((atom(v[2]) for v in children(fp,'property') if atom(v[1])=='Reference'),'')
  if ref in ('J5','PS1'):fp[:]=[v for v in fp if not(isinstance(v,list) and v[0] in ('fp_line','fp_poly','fp_circle','fp_arc') and child(v,'layer') and atom(child(v,'layer')[1])=='F.SilkS')]
 (ROOT/'carbonmirror.kicad_pcb').write_text(ser(tree))
 project=ROOT/'carbonmirror.kicad_pro'
 if project.exists():
  conf=json.loads(project.read_text());conf['board']['design_settings']['rules']['min_through_hole_diameter']=.2;project.write_text(json.dumps(conf,indent=2))
# Functional schematic arrangement (A3); placements do not alter PCB.
positions={'PS1':(95,65),'J5':(40,65),'U2':(65,140),'L1':(100,140),'C1':(35,140),'C2':(85,115),'C3':(115,160),'C4':(135,160),'K1':(180,65),'Q1':(180,120),'D1':(215,65),'R1':(150,120),'R2':(160,145),'J1':(150,42),'J2':(225,42),'U1':(320,85),'C5':(295,42),'R3':(260,65),'C6':(260,95),'R4':(340,142),'R5':(365,142),'R6':(390,142),'J4':(380,75),'U3':(320,205),'R7':(280,180),'R8':(270,210),'R9':(360,180),'C7':(355,218),'SW1':(185,215),'R10':(155,195),'LED1':(215,250),'R11':(180,250),'J3':(60,245)}
for c in parts:c['sch']=positions[c['ref']]
# Schematic embeds upstream library symbol geometry and true pin numbers.
symbols={};items=[];ends={}
for c in parts:
 key='CarbonMirror:'+c['name'];s=copy.deepcopy(c['sym']);s[1]=q(key);symbols[key]=ser(s)
 x,y=[round(v/1.27)*1.27 for v in c['sch']];inst=f'(symbol (lib_id {q(key)}) (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {uid(c["ref"])})'
 top=max((pp['at'][1] for pp in c['pins']),default=0);
 for name,value,dy,hide in [('Reference',c['ref'],-top-7,False),('Value',c['value'],-top-4,False),('Footprint',c['fp'],0,True),('Datasheet',c['url'],0,True)]:inst+=f'(property {q(name)} {q(value)} (at {x+(-20 if c["ref"]=="K1" else 20 if c["ref"]=="Q1" else 15 if c["ref"].startswith("U") else 6 if c["name"] in ("R","C","L") else 0)} {y+((-2 if name=="Reference" else 2) if (c["name"] in ("R","C","L") or c["ref"] in ("K1","Q1")) and name in ("Reference","Value") else dy)} 0) (effects (font (size 1.27 1.27))'+(' (hide yes)' if hide else '')+'))'
 for pin in c['pins']:inst+=f'(pin {q(pin["number"])} (uuid {uid(c["ref"]+pin["number"])}))'
 inst+=f'(instances (project "carbonmirror" (path "/{uid("sheet")}" (reference {q(c["ref"])}) (unit 1)))))';items.append(inst)
 for pin in c['pins']:
  px,py,ang=pin['at'];sx=x+px;sy=y-py;n=c['nets'].get(pin['number'])
  if not n:items.append(f'(no_connect (at {sx} {sy}) (uuid {uid(c["ref"]+pin["number"]+"nc")}))');continue
  rad=math.radians(ang);ex=round(sx-5.08*math.cos(rad),4);ey=round(sy+5.08*math.sin(rad),4)
  if c['ref']=='K1' and pin['number']=='12':ey=round(ey-7.62,4)
  ends[(c['ref'],n)]=(ex,ey)
  items.append(f'(wire (pts (xy {sx} {sy}) (xy {ex} {ey})) (stroke (width 0) (type default)) (uuid {uid(c["ref"]+pin["number"]+"w")}))')
  items.append(f'(label {q(n)} (at {ex} {ey} 0) (effects (font (size 1 1)) (justify {'right' if ang==0 else 'left'} bottom)) (uuid {uid(c["ref"]+pin["number"]+"l")}))')
for text,x,y in [('DEVELOPMENT RELEASE - NOT FOR FABRICATION OR ENERGIZATION',15,15),('Off-board: coordinated branch fuse + thermal cutoff + protected auxiliary fuse. PE is continuous stamped/wired path, NEVER switched.',15,22),('J3: meter SPI + 5V; output feedback pin9; interlocked coil power pin10. No hot meter ground on this connector.',15,29)]:items.append(f'(text {q(text)} (at {x} {y} 0) (effects (font (size 1.5 1.5)) (justify left)) (uuid {uid(text)}))')
def local_wire(ra,rb,net):
 a=ends[(ra,net)];b=ends[(rb,net)];corner=(b[0],a[1]) if (ra,rb,net) in [('K1','D1','COIL_5V'),('R1','Q1','GATE'),('R2','Q1','GND_ISO'),('R11','LED1','LED_A')] else (a[0],b[1]);points=[a,corner,b]
 if (ra,rb,net)==('K1','D1','COIL_5V'):points=[a,(a[0],a[1]-10.16),(b[0],a[1]-10.16),b]
 for i,(start,end) in enumerate(zip(points,points[1:])):
  if start==end:continue
  items.append(f'(wire (pts (xy {start[0]} {start[1]}) (xy {end[0]} {end[1]})) (stroke (width 0) (type default)) (uuid {uid("local"+ra+rb+net+str(i))}))')
for ra,rb,n in [('K1','Q1','COIL_LOW'),('K1','D1','COIL_5V'),('D1','Q1','COIL_LOW'),('R1','Q1','GATE'),('R2','Q1','GATE'),('R2','Q1','GND_ISO'),('L1','C3','+3V3_ISO'),('R3','C6','EN'),('R10','SW1','BUTTON'),('R11','LED1','LED_A')]:local_wire(ra,rb,n)
for label,x,y in [('01  ISOLATED INPUT',15,38),('02  BUCK CONVERTER',15,100),('03  INTERLOCKED LOAD RELAY + DRIVER',145,34),('04  EDGE CONTROLLER',250,34),('05  LOCAL CONTROLS',145,175),('06  BOARD TEMPERATURE',250,165),('07  ISOLATED SYSTEM HARNESS',15,220)]:
 items.append(f'(text {q(label)} (at {x} {y} 0) (effects (font (size 1.5 1.5) (bold yes)) (justify left)) (uuid {uid(label)}))')
# Direct local rails link parallel buck output capacitors; global labels retained for cross-block clarity.
for py in [-8.89,8.89]:
 x1=round(115/1.27)*1.27;x2=round(135/1.27)*1.27;y=round(160/1.27)*1.27+py
 items.append(f'(wire (pts (xy {x1} {y}) (xy {x2} {y})) (stroke (width 0) (type default)) (uuid {uid("caprail"+str(py))}))')
for j,n in enumerate(['L_AUX_FUSED','N','+3V3_ISO','L_NC_UNUSED']):
 key='CarbonMirror:PWR_FLAG';ss=libsym('power','PWR_FLAG');ss[1]=q(key);symbols[key]=ser(ss);x=round(90/1.27)*1.27+j*25.4;y=265.43;ref='#FLG0'+str(j+1)
 items.append(f'(symbol (lib_id "{key}") (at {x} {y} 0) (unit 1) (in_bom no) (on_board yes) (uuid {uid(ref)}) (property "Reference" "{ref}" (at {x} {y} 0) (effects (font (size 1 1)) (hide yes))) (property "Value" "PWR_FLAG" (at {x} {y-5.08} 0) (effects (font (size 1 1)))) (instances (project "carbonmirror" (path "/{uid("sheet")}" (reference "{ref}") (unit 1)))))')
 items.append(f'(label "{n}" (at {x} {y} 0) (effects (font (size 1 1)) (justify left bottom)) (uuid {uid(ref+"label")}))')
(ROOT/'carbonmirror.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {uid("sheet")}) (paper "A3") (title_block (title "CarbonMirror - REV B single socket controller") (rev "DEV-B / FAB HOLD")) (lib_symbols '+''.join(symbols.values())+')'+''.join(items)+')')
(ROOT/'CarbonMirror.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator \"kicad_symbol_editor\") '+''.join(v.replace(q(k),q(k.split(':')[1]),1) for k,v in symbols.items())+')')
(ROOT/'sym-lib-table').write_text('(sym_lib_table (lib (name \"CarbonMirror\") (type \"KiCad\") (uri \"${KIPRJMOD}/CarbonMirror.kicad_sym\") (options \"\") (descr \"Vendored upstream KiCad symbol geometry\")))')
(ROOT/'circuit_manifest.json').write_text(json.dumps([{k:v for k,v in c.items() if k!='sym'} for c in parts],indent=2))
with (ROOT/'bom.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['Reference','Value','Manufacturer part candidate','Footprint','Source URL','Status']);
 for c in parts:w.writerow([c['ref'],c['value'],c['mpn'],c['fp'],c['url'],'UNRELEASED: verify exact variant, sourcing and application'])
print('Created',len(parts),'components,',len(set(n for c in parts for n in c['nets'].values())),'nets')
