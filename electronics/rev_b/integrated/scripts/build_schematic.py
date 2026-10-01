#!/usr/bin/python3
from carbentra_tools import FREECAD_LIB, FONT_REGULAR, PYTHON, kicad_resource
"""Hierarchical merger preserving source circuit drawings and true pins; no PCB writes."""
from pathlib import Path
import re,json,uuid,copy,math
R=Path(__file__).resolve().parents[1];BASE=R.parent
M=json.loads((R/'electrical_manifest.json').read_text(encoding='utf-8'));PARTS={c['ref']:c for c in M['components']}
def uid(x):return str(uuid.uuid5(uuid.NAMESPACE_URL,'carbentra/revb/integrated/'+x))
def q(x):return json.dumps(str(x))
def parse(s):
 st=[]
 for t in re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',s):
  if t=='(':
   a=[]
   if st:st[-1].append(a)
   st.append(a)
  elif t==')':root=st.pop()
  else:st[-1].append(t)
 return root
def ser(x):return '('+' '.join(map(ser,x))+')' if isinstance(x,list) else x
def ch(x,k):return next((v for v in x if isinstance(v,list) and v[0]==k),None)
def cs(x,k):return [v for v in x if isinstance(v,list) and v[0]==k]
def at(v):return tuple(round(float(x),5) for x in ch(v,'at')[1:3])
def atom(x):return json.loads(x) if x.startswith('"') else x
def prop(s,k):return next((v for v in cs(s,'property') if atom(v[1])==k),None)
def geometry(sym):
 out=[]
 for sub in cs(sym,'symbol'):
  for p in cs(sub,'pin'):out.append({'number':atom(ch(p,'number')[1]),'name':atom(ch(p,'name')[1]),'at':list(map(float,ch(p,'at')[1:4])),'type':p[1]})
 return out
libcache={}
def std(lib,name):
 if lib not in libcache:libcache[lib]={atom(s[1]):s for s in cs(parse(Path(kicad_resource('symbols'),lib+'.kicad_sym').read_text(encoding='utf-8')),'symbol')}
 s=copy.deepcopy(libcache[lib][name]);e=ch(s,'extends')
 if e:
  base=std(lib,atom(e[1]));pr={atom(v[1]):v for v in cs(base,'property')};pr.update({atom(v[1]):v for v in cs(s,'property')});s=[s[0],s[1]]+list(pr.values())+[v for v in base[2:] if not(isinstance(v,list) and v[0] in ['property','extends'])]
 for v in cs(s,'symbol'):v[1]=q(name+'_'+atom(v[1]).split('_')[-2]+'_'+atom(v[1]).split('_')[-1])
 return s
# net maps are independent of original drawing label scopes
maps={}
for mod in ['controller','meter','feedback','thermal']:
 mp={}
 for c in PARTS.values():
  if c['source_module']==mod:
   if c['ref']=='J201':continue
   mp.update(c['netmap'])
 maps[mod]=mp
ROOT=uid('root');sheetids={m:uid('sheet-instance-'+m) for m in maps};sourcefiles={'controller':'carbentra.kicad_sch','meter':'meter.kicad_sch','feedback':'output_feedback.kicad_sch','thermal':'thermal_interlock.kicad_sch'}
libraries=[]
# Native clock and its dedicated bypass are drawn on the integration overview.
rootrefs={'F501','Y201','CX201'}
for mod in maps:
 tree=parse((BASE/mod/sourcefiles[mod]).read_text(encoding='utf-8'));ls=ch(tree,'lib_symbols');defs={atom(s[1]):s for s in cs(ls,'symbol')};rowmap={c['source_ref']:c for c in PARTS.values() if c['source_module']==mod and c['ref'] not in rootrefs}
 # Integrated-only pin-compatible higher-margin supply; change native symbol too.
 if mod=='controller':
  newdef=std('Converter_ACDC','IRM-10-5');newdef[1]=q('Converter_ACDC:IRM-10-5');ls.append(newdef);defs['Converter_ACDC:IRM-10-5']=newdef
  for inst in cs(tree,'symbol'):
   if atom(prop(inst,'Reference')[2])=='PS1':ch(inst,'lib_id')[1]=q('Converter_ACDC:IRM-10-5')
 delete_points=set();delete_symbols=set();override_labels={};newinstances=[]
 def pinpositions(inst):
  key=atom(ch(inst,'lib_id')[1]);sym=defs.get(key) or next(v for k,v in defs.items() if k.split(':')[-1]==key.split(':')[-1]);x,y=at(inst);rot=math.radians(float(ch(inst,'at')[3]));co,si=math.cos(rot),math.sin(rot)
  return {p['number']:(round(x+p['at'][0]*co-p['at'][1]*si,5),round(y-p['at'][0]*si-p['at'][1]*co,5)) for p in geometry(sym)}
 # Remove connector/wire-model flags and changed symbols along with their dedicated stubs.
 for inst in cs(tree,'symbol'):
  oldref=atom(prop(inst,'Reference')[2]);poses=pinpositions(inst);c=rowmap.get(oldref)
  if c is None:
   delete_symbols.add(id(inst));delete_points.update(poses.values());continue
  # Wiring changes per pin are local to this component (terminal reassignment and OSCO NC).
  olds={p['number']:None for p in geometry(defs[atom(ch(inst,'lib_id')[1])])};olds.update(c['source_pins'])
  for pin,pos in poses.items():
   newnet=c['pins'].get(pin)
   if newnet is None and olds.get(pin) is not None:delete_points.add(pos)
   elif newnet is not None and maps[mod].get(olds.get(pin),olds.get(pin))!=newnet:
    override_labels[pos]=newnet
    for w in cs(tree,'wire'):
     pts=[tuple(round(float(x),5) for x in v[1:3]) for v in ch(w,'pts')[1:]]
     if pos in pts:
      for pt in pts:override_labels[pt]=newnet
  prop(inst,'Reference')[2]=q(c['ref']);prop(inst,'Value')[2]=q(c['value']);prop(inst,'Footprint')[2]=q(c['footprint']);ds=prop(inst,'Datasheet')
  if ds:ds[2]=q(c['datasheet'])
  name=atom(ch(inst,'lib_id')[1]).split(':')[-1];ch(inst,'lib_id')[1]=q('Integrated_'+mod+':'+name)
  oldi=ch(inst,'instances')
  if oldi:inst.remove(oldi)
  inst.append(parse(f'(instances (project "integrated" (path "/{ROOT}/{sheetids[mod]}" (reference {q(c["ref"])}) (unit 1))))'))
  # Manifest's true pin geometry comes from the source embedded symbol.
  c['pin_geometry']=geometry(defs[atom(ch(inst,'lib_id')[1]).replace('Integrated_'+mod+':',atom(ch(tree,'lib_symbols')[1][1]).split(':')[0]+':')]) if False else geometry(next(s for key,s in defs.items() if key.split(':')[-1]==name))
  # New NC on external-clock OSCO.
  for pin,pos in poses.items():
   if c['pins'].get(pin) is None and olds.get(pin) is not None:tree.append(parse(f'(no_connect (at {pos[0]} {pos[1]}) (uuid {uid(c["ref"]+pin+"nc")}))'))
 # First collect removed stub far endpoints. Do not erase source inter-component wiring on surviving circuits.
 remove_wire=set();far=set()
 for w in cs(tree,'wire'):
  pts=[tuple(round(float(x),5) for x in v[1:3]) for v in ch(w,'pts')[1:]]
  if any(pt in delete_points for pt in pts):remove_wire.add(id(w));far.update(pts)
 new=[]
 for obj in tree:
  if not isinstance(obj,list):new.append(obj);continue
  tag=obj[0]
  if tag=='symbol' and id(obj) in delete_symbols:continue
  if tag=='wire' and id(obj) in remove_wire:continue
  if tag in ['label','global_label'] and (at(obj) in far or at(obj) in delete_points):continue
  if tag=='no_connect' and at(obj) in delete_points:
   # Keep the newly created OSCO NC; removed symbols' NCs disappear.
   is_new=any(c['ref']=='U201' and at(obj)==pinpositions(next(i for i in cs(tree,'symbol') if prop(i,'Reference') and atom(prop(i,'Reference')[2])=='U201')).get('23') for c in rowmap.values()) if mod=='meter' else False
   if not is_new:continue
  if tag in ['label','global_label']:
   old=atom(obj[1]);name=override_labels.get(at(obj),maps[mod].get(old,old));obj[0]='global_label';obj[1]=q(name)
   if obj[0]=='global_label' and not ch(obj,'shape'):obj.insert(2,['shape','passive'])
   eff=ch(obj,'effects');font=ch(eff,'font') if eff else None
   if font and ch(font,'size'):ch(font,'size')[1:]=['0.9','0.9']
  new.append(obj)
 tree=new
 # Distinguish system operating proposal from detector analysis headroom.
 for tx in cs(tree,'text'):
  val=atom(tx[1])
  if mod=='feedback' and val.startswith('198-264 VAC'):val='198-242 VAC OPERATING PROPOSAL; 264 VAC ANALYSIS HEADROOM ONLY; QUALIFICATION HOLD'
  if mod=='controller' and 'Off-board:' in val:val='Off-board coordinated branch fuse + thermal cutoff. F501 is the on-board auxiliary fuse. PE remains continuous and unswitched.'
  if mod=='controller' and val.startswith('07') and 'HARNESS' in val:tree.remove(tx);continue
  if mod=='controller' and ('J3 accepts' in val or val.startswith('J3:')):val='SPI metering, output feedback and thermal permission are directly integrated; no inter-module host connector.'
  if mod=='thermal' and val.startswith('J1.4 replaces'):val='COIL_5V feeds K101.A1 and D101 cathode; no ungated coil-supply bypass is permitted.'
  if mod=='meter' and 'CLOCK / RESET / DECOUPLING' in val:val='06  RESET / DECOUPLING; POWERED CLOCK ON OVERVIEW'
  tx[1]=q(val)
 if mod=='thermal':tree.append(parse(f'(text "REMOTE HEAD: U401 / R401 / C401 / J404 only. W401/W402 are cable models, not PCB parts." (at 12.7 27.94 0) (effects (font (size 1 1)) (justify left)) (uuid {uid("head-scope")}))'))
 # If removing an external terminal also removed a direct wire to a surviving pin, attach its manifest net explicitly.
 endpoints={pt for w in cs(tree,'wire') for pt in [tuple(round(float(x),5) for x in v[1:3]) for v in ch(w,'pts')[1:]]}
 labelpoints={at(v) for tag in ['label','global_label'] for v in cs(tree,tag)}
 for inst in cs(tree,'symbol'):
  ref=atom(prop(inst,'Reference')[2]);c=PARTS.get(ref)
  if not c:continue
  for pin,pos in pinpositions(inst).items():
   net=c['pins'].get(pin)
   if net is not None and pos not in endpoints and pos not in labelpoints:
    tree.append(parse(f'(global_label {q(net)} (shape passive) (at {pos[0]} {pos[1]} 0) (effects (font (size .9 .9)) (justify right bottom)) (uuid {uid(ref+pin+"restored_label")}))'))
 # Replace library namespace and renew UUIDs without touching external references or PCB data.
 for sym in cs(ls,'symbol'):
  base=atom(sym[1]).split(':')[-1];sym[1]=q('Integrated_'+mod+':'+base)
 def renew(node):
  if not isinstance(node,list):return
  if node and node[0]=='uuid':node[1]=q(uid(mod+'/'+atom(node[1])))
  else:
   for v in node:renew(v)
 renew(tree);ch(tree,'uuid')[1]=q(uid('document-'+mod));title=ch(tree,'title_block')
 if title:
  if ch(title,'title'):ch(title,'title')[1]=q('CARBENTRA EVT-B: '+mod)
  if ch(title,'rev'):ch(title,'rev')[1]=q('EVT-B HOLD')
 (R/('integrated_'+mod+'.kicad_sch')).write_text(ser(tree), encoding='utf-8', newline='\n')
 lname='Integrated_'+mod;libs=[]
 for sym in cs(ls,'symbol'):
  cp=copy.deepcopy(sym);cp[1]=q(atom(cp[1]).split(':')[-1]);libs.append(ser(cp))
 (R/(lname+'.kicad_sym')).write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")'+''.join(libs)+')', encoding='utf-8', newline='\n');libraries.append(lname)
# Root overview with real fuse, clock and supply assertions.
rootdefs={};items=[]
def add(ref,lib,name,xy,nets,value,fp='',ds='',bom=True):
 sym=std(lib,name);sym[1]=q('IntegratedRoot:'+name);rootdefs[name]=ser(sym);x,y=xy;s=f'(symbol (lib_id "IntegratedRoot:{name}") (at {x} {y} 0) (unit 1) (in_bom {"yes" if bom else "no"}) (on_board {"yes" if bom else "no"}) (uuid {uid(ref)})'
 g=geometry(sym)
 for pn,pv,dy,hide in [('Reference',ref,-10,False),('Value',value,-7,False),('Footprint',fp,0,True),('Datasheet',ds,0,True)]:s+=f'(property {q(pn)} {q(pv)} (at {x+12.7} {y+dy} 0) (effects (font (size 1.1 1.1))'+(' (hide yes)' if hide else '')+'))'
 for p in g:s+=f'(pin {q(p["number"])} (uuid {uid(ref+p["number"])}))'
 s+=f'(instances (project "integrated" (path "/{ROOT}" (reference {q(ref)}) (unit 1)))))';items.append(s)
 for p in g:
  px,py,ang=p['at'];a=(x+px,y-py);net=nets.get(p['number'])
  if net is None:items.append(f'(no_connect (at {a[0]} {a[1]}) (uuid {uid(ref+p["number"]+"nc")}))');continue
  rad=math.radians(ang);z=(round(a[0]-5.08*math.cos(rad),5),round(a[1]+5.08*math.sin(rad),5))
  if z!=a:items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {z[0]} {z[1]})) (stroke (width 0) (type default)) (uuid {uid(ref+p["number"]+"w")}))')
  items.append(f'(global_label {q(net)} (shape passive) (at {z[0]} {z[1]} 0) (effects (font (size 1 1)) (justify {"right" if ang==0 else "left"} bottom)) (uuid {uid(ref+p["number"]+"n")}))')
 if ref in PARTS:PARTS[ref]['pin_geometry']=g
boxnotes={
 'controller':['PS101 IRM-10-5; AP63203 3.3 V rail','ESP32-C3 + low-side relay driver','K101: HOT_LOAD to HOT_SWITCHED','Coil feed = hardware-gated COIL_5V','OUTPUT_PRESENT_N enters U101.15'],
 'meter':['RS201 Kelvin shunt + voltage divider','ATM90E26 AFE + reinforced SPI isolation','R05CT isolated supply for HOT_3V3','Powered ASV clock / CX201 shown at right','HOT_GND is live line reference'],
 'feedback':['Four 33k resistors + ACPL-K376 detector','Senses HOT_SWITCHED relative to HOT_N','OUTPUT_PRESENT_N returns to the MCU','Active-low 100/120 Hz pulses','No proof of dead output or contact position'],
 'thermal':['Remote head: U401 / R401 / C401 / J404','TMP302 + supervisor + trip-dominant latch','SW401 physical rearm only; no MCU rearm','Q401 gates coil feed; TP401 / TP402 optional','Backside coupling / insulation needs qualification']}
for i,mod in enumerate(maps):
 x=25.4+(i%2)*127;y=58.42+(i//2)*66.04
 items.append(f'(sheet (at {x} {y}) (size 111.76 43.18) (stroke (width 0) (type default)) (fill (color 0 0 0 0)) (uuid {sheetids[mod]}) (property "Sheetname" {q(str(i+1)+" "+mod)} (at {x} {y-1.27} 0) (effects (font (size 1.5 1.5)) (justify left bottom))) (property "Sheetfile" "integrated_{mod}.kicad_sch" (at {x} {y+44.45} 0) (effects (font (size 1.1 1.1)) (justify left top))) (instances (project "integrated" (path "/{ROOT}" (page "{i+2}")))))')
 for j,txt in enumerate(boxnotes[mod]):items.append(f'(text {q(txt)} (at {x+5.08} {y+7.62+j*5.08} 0) (effects (font (size 1.1 1.1)) (justify left)) (uuid {uid(mod+str(j)+"boxnote")}))')
# Explicit off-PCB full-assembly chain is a fifth functional sheet.
items.append(f'(sheet (at 25.4 177.8) (size 228.6 20.32) (stroke (width 0) (type default)) (fill (color 0 0 0 0)) (uuid {uid("sheet-instance-assembly")}) (property "Sheetname" "5 assembly protection" (at 25.4 176.53 0) (effects (font (size 1.5 1.5)) (justify left bottom))) (property "Sheetfile" "integrated_assembly.kicad_sch" (at 25.4 199.39 0) (effects (font (size 1.1 1.1)) (justify left top))) (instances (project "integrated" (path "/{ROOT}" (page "6")))))')
for txt,yy in [('Plug L -> F601 main fuse -> TF601 thermal link -> protected main PCB input',184.15),('Socket output follows K101; PE is direct and never enters PCB or relay',189.23)]:items.append(f'(text {q(txt)} (at 30.48 {yy} 0) (effects (font (size 1.1 1.1)) (justify left)) (uuid {uid(txt)}))')
libraries.append('IntegratedAssembly')
for ref,lib,name,xy in [('F501','Device','Fuse',(330.2,76.2)),('Y201','Oscillator','ASV-xxxMHz',(330.2,152.4)),('CX201','Device','C',(381,152.4))]:
 c=PARTS[ref];add(ref,lib,name,xy,c['pins'],c['value'],c['footprint'],c['datasheet'])
for i,net in enumerate(['+3V3_ISO','HOT_N','HOT_AUX_FUSED','HOT_AVDD','TH_3V3_HEAD','TH_GND_HEAD','HOT_NC']):
 add('#FLG'+str(i+1),'power','PWR_FLAG',(30.48+(i%4)*91.44,218.44+(i//4)*22.86),{'1':net},'NC LIVE-POTENTIAL NET ANCHOR' if net=='HOT_NC' else 'EXTERNAL / PASSIVE RAIL',bom=False)
for txt,x,y,siz in [('CARBENTRA / CARBENTRA-P16-EVT-B INTEGRATED ELECTRICAL SOURCE',12.7,15.24,2),('101 main-board parts + 4 remote-head parts + 4 off-board assemblies; harness models are not PCB parts',12.7,25.4,1.3),('Hierarchy is functional grouping. Shared global net names are real electrical connections.',12.7,33.02,1.3),('CANDIDATE ONLY: no fabrication, energization, safety or certification release',12.7,40.64,1.3),('AUXILIARY FUSE: protected line to isolated supply input',279.4,48.26,1.1),('POWERED CLOCK: OSCO is NC; exact frequency procurement HOLD',279.4,116.84,1.1),('HOT_GND is LINE POTENTIAL. PE is external, continuous and never switched.',12.7,266.7,1.2),('Remote head: component face rear; smooth GND copper backside to qualified insulating pad. Thermal lag/insulation HOLD.',12.7,276.86,1.1)]:items.append(f'(text {q(txt)} (at {x} {y} 0) (effects (font (size {siz} {siz})) (justify left)) (uuid {uid(txt)}))')
(R/'integrated.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {ROOT}) (paper "A3") (title_block (title "CARBENTRA CARBENTRA-P16-EVT-B integrated source") (rev "EVT-B HOLD")) (lib_symbols '+''.join(rootdefs.values())+')'+''.join(items)+')', encoding='utf-8', newline='\n')
(R/'IntegratedRoot.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")'+''.join(s.replace('IntegratedRoot:','') for s in rootdefs.values())+')', encoding='utf-8', newline='\n');libraries.append('IntegratedRoot')
(R/'sym-lib-table').write_text('(sym_lib_table'+''.join(f'(lib (name "{n}") (type "KiCad") (uri "${{KIPRJMOD}}/{n}.kicad_sym") (options "") (descr "Integrated source symbols"))' for n in libraries)+')', encoding='utf-8', newline='\n')
# Do not overwrite parent's PCB project configuration.
if not (R/'integrated.kicad_pro').exists():(R/'integrated.kicad_pro').write_text(json.dumps({'meta':{'filename':'integrated.kicad_pro','version':1}},indent=2), encoding='utf-8', newline='\n')
M['status']='SCHEMATIC GENERATED; awaiting ERC and independent netlist check';M['components']=list(PARTS.values());(R/'electrical_manifest.json').write_text(json.dumps(M,indent=2), encoding='utf-8', newline='\n');print('Generated integration overview + five functional/assembly sheets')
