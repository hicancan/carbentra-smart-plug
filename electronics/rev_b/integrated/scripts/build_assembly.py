#!/usr/bin/python3
"""Draw actual off-PCB protection chain and uninterrupted PE. No PCB writes."""
import json,uuid
from pathlib import Path
R=Path(__file__).resolve().parents[1];M=json.loads((R/'electrical_manifest.json').read_text());P={c['ref']:c for c in M['components']}
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'carbentra/revb/integrated/'+s))
def q(s):return json.dumps(str(s))
ROOT=uid('root');SHEET=uid('sheet-instance-assembly');DOC=uid('document-assembly')
def pin(n,name,x,y,ang):return {'number':str(n),'name':name,'type':'passive','at':[x,y,ang]}
geom={'Fuse_Main':[pin(1,'IN',-7.62,0,0),pin(2,'OUT',7.62,0,180)],'Thermal_Link':[pin(1,'CASE / IN',-7.62,0,0),pin(2,'INS / OUT',7.62,0,180)],'Plug_Contacts':[pin(1,'L',7.62,12.7,180),pin(2,'N',7.62,0,180),pin(3,'PE',7.62,-12.7,180)],'Socket_Contacts':[pin(1,'L',-7.62,12.7,0),pin(2,'N',-7.62,0,0),pin(3,'PE',-7.62,-12.7,0)]}
defs=[]
for name,gs in geom.items():
 s=f'(symbol "IntegratedAssembly:{name}" (pin_names (offset 1)) (in_bom yes) (on_board no) (property "Reference" "J" (at 0 20.32 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 17.78 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_0_1"'
 if 'Contacts' in name:
  s+='(rectangle (start -3.81 16.51) (end 3.81 -16.51) (stroke (width .254) (type default)) (fill (type background)))'
 else:
  s+='(rectangle (start -3.81 1.905) (end 3.81 -1.905) (stroke (width .254) (type default)) (fill (type none))) (polyline (pts (xy -3.81 0) (xy 3.81 0)) (stroke (width .254) (type default)) (fill (type none)))'
  if name=='Thermal_Link':s+='(polyline (pts (xy -3.81 -2.54) (xy 3.81 2.54)) (stroke (width .254) (type default)) (fill (type none)))'
 s+=')'+f'(symbol "{name}_1_1"'
 for g in gs:
  x,y,a=g['at'];s+=f'(pin passive line (at {x} {y} {a}) (length 3.81) (name {q(g["name"])} (effects (font (size 1 1)))) (number {q(g["number"])} (effects (font (size 1.1 1.1)))))'
 defs.append(s+'))')
items=[];coords={}
for ref,xy in [('J601',(35.56,76.2)),('F601',(104.14,63.5)),('TF601',(172.72,63.5)),('J602',(368.3,76.2))]:
 c=P[ref];x,y=xy;name=c['symbol_name'];gs=geom[name];c['pin_geometry']=gs;c['source_schematic_position']=list(xy)
 s=f'(symbol (lib_id "IntegratedAssembly:{name}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board no) (uuid {uid(ref)})'
 for pn,pv,dy,hide in [('Reference',ref,-23 if 'Contacts' in name else -12,False),('Value',{'J601':'CUSTOM PLUG / L N PE','J602':'CUSTOM SOCKET / L N PE','F601':'8020.5080 / 16A FAST','TF601':'G5 Tf110C / SUFFIX HOLD'}[ref],-20 if 'Contacts' in name else -8,False),('Footprint','',0,True),('Datasheet',c['datasheet'],0,True)]:s+=f'(property {q(pn)} {q(pv)} (at {x} {y+dy} 0) (effects (font (size 1.1 1.1))'+(' (hide yes)' if hide else '')+'))'
 for g in gs:
  s+=f'(pin {q(g["number"])} (uuid {uid(ref+g["number"])}))';coords[(ref,g['number'])]=(round(x+g['at'][0],5),round(y-g['at'][1],5))
 s+=f'(instances (project "integrated" (path "/{ROOT}/{SHEET}" (reference {q(ref)}) (unit 1)))))';items.append(s)
def wire(a,b,key):items.append(f'(wire (pts (xy {a[0]} {a[1]}) (xy {b[0]} {b[1]})) (stroke (width 0) (type default)) (uuid {uid(key)}))')
def label(n,xy,key,global_=False):items.append(f'({"global_label" if global_ else "label"} {q(n)} '+('(shape passive) ' if global_ else '')+f'(at {xy[0]} {xy[1]} 0) (effects (font (size 1.1 1.1)) (justify left bottom)) (uuid {uid(key)}))')
wire(coords['J601','1'],coords['F601','1'],'rawline');label('RAW_L',(60.96,63.5),'rawlabel')
wire(coords['F601','2'],coords['TF601','1'],'fuse-to-thermal');label('HOT_TF_IN',(132.08,63.5),'thermal-input-label')
wire(coords['TF601','2'],(231.14,63.5),'protected-in');label('HOT_GND',(231.14,63.5),'protected-label',True)
wire((287.02,63.5),coords['J602','1'],'switched-out');label('HOT_SWITCHED',(287.02,63.5),'switched-label',True)
# Neutral remains continuous through the connector interface. No fuse or relay is drawn in it.
wire(coords['J601','2'],coords['J602','2'],'neutral-direct');label('HOT_N',(71.12,76.2),'neutral-left',True);label('HOT_N',(317.5,76.2),'neutral-right',True)
# PE is an uninterrupted off-board conductor, below and outside the main-board box.
wire(coords['J601','3'],coords['J602','3'],'PE-direct');label('PE',(71.12,88.9),'PE-label')
items.append(f'(polyline (pts (xy 231.14 45.72) (xy 287.02 45.72) (xy 287.02 81.28) (xy 231.14 81.28) (xy 231.14 45.72)) (stroke (width .254) (type default)) (fill (type none)) (uuid {uid("main-box")}))')
for txt,x,y,size in [('R10 ASSEMBLY PROTECTION / OFF-BOARD INTERNAL PARTS',12.7,15.24,2),('CANDIDATE ONLY: this sheet closes the drawn assembly path, not qualification or certification',12.7,25.4,1.3),('MAIN PCB',238.76,52.07,1.5),('J201.1 -> shunt + relay -> J102.1',236.22,57.15,1),('J201.2 / J102.2 = HOT_N',236.22,70,1),('PE: direct plug-to-socket path; NEVER through PCB, relay, fuse or software',63.5,101.6,1.3),('F601 = MAIN 16 A fast-acting fuse. F501 = separate PCB auxiliary 1 A time-delay fuse.',12.7,124.46,1.3),('TF601 = distinct one-shot MICROTEMP G5 thermal link, provisional Tf110C; order suffix and mounting HOLD.',12.7,134.62,1.3),('SHF16A:1.5kA@250VAC cos(phi)0.7-0.8. Typical melting I2t760A2s is NOT total clearing or a downstream energy bound.',12.7,144.78,1.2),('Upstream breaker, prospective fault current, fuse I2t/selectivity, hot-condition derating and wiring coordination are UNVERIFIED.',12.7,154.94,1.2),('NO ACTIVE CURRENT LIMIT: a fuse rating is not a continuous-current clamp or a guaranteed socket overload threshold.',12.7,165.1,1.3),('Custom contacts + 2x CQP8040.0003 clips;45x16x2 carrier / Cu collectors; fit accepted, heating/insulation HOLD.',12.7,177.8,1.2),('Assembly contact numbers identify L/N/PE wiring. SHF8020.5080 fuse6.3x32mm replaces216/OGN for higher clip margin.',12.7,187.96,1.2),('The main-PCB box references real circuits on sheets 1-4; it is not an electrical bypass between HOT_GND and HOT_SWITCHED.',12.7,200.66,1.2),('PE continuity, polarity, touch protection, contact heating and cold-weld disconnection still require physical verification.',12.7,213.36,1.2),('F601 / TF601 / J601 / J602 are on_board=false. Main PCB part count remains 101.',12.7,226.06,1.2)]:items.append(f'(text {q(txt)} (at {x} {y} 0) (effects (font (size {size} {size})) (justify left)) (uuid {uid(txt)}))')
(R/'integrated_assembly.kicad_sch').write_text(f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {DOC}) (paper "A3") (title_block (title "R10 full assembly protection") (rev "CANDIDATE / HOLD")) (lib_symbols '+''.join(defs)+')'+''.join(items)+')')
(R/'IntegratedAssembly.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor")'+''.join(s.replace('IntegratedAssembly:','') for s in defs)+')')
M['components']=list(P.values());(R/'electrical_manifest.json').write_text(json.dumps(M,indent=2));print('Assembly sheet: 4 off-PCB parts, 10 numbered terminals, direct PE path')
