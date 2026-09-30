#!/usr/bin/python3
"""Integrated Rev B placement source. Regeneration discards copper unless --retain-copper recipe is replayed."""
from pathlib import Path
import pcbnew as p,json,math,uuid,sys
R=Path(__file__).resolve().parents[1];m=json.loads((R/'electrical_manifest.json').read_text());parts=[c for c in m['components'] if c['board_designation']=='integrated']
def vec(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'carbonmirror/integrated-b/'+s))
def custom(name,body,origin,pads):
 f=p.FOOTPRINT(None);f.SetFPID(p.LIB_ID('Integrated',name));f.SetValue(name)
 for num,x,y,diam,drill in pads:
  d=p.PAD(f);d.SetNumber(str(num));d.SetAttribute(p.PAD_ATTRIB_PTH);d.SetShape(p.PAD_SHAPE_RECT if num==1 else p.PAD_SHAPE_CIRCLE);d.SetPosition(vec(x,y));d.SetSize(vec(diam,diam));d.SetDrillSize(vec(drill,drill));ls=p.LSET.AllCuMask();ls.AddLayer(p.F_Mask);ls.AddLayer(p.B_Mask);d.SetLayerSet(ls);f.Add(d)
 for layer,extra in ((p.F_Fab,0),(p.F_CrtYd,.5)):
  x,y=origin;w,h=body;x-=extra;y-=extra;w+=2*extra;h+=2*extra
  for a,z in [((x,y),(x+w,y)),((x+w,y),(x+w,y+h)),((x+w,y+h),(x,y+h)),((x,y+h),(x,y))]:
   g=p.PCB_SHAPE();g.SetShape(p.SHAPE_T_SEGMENT);g.SetStart(vec(*a));g.SetEnd(vec(*z));g.SetWidth(p.FromMM(.05));g.SetLayer(layer);f.Add(g)
 p.PCB_IO_KICAD_SEXPR().FootprintSave(str(R/'Integrated.pretty'),f)
custom('MKDS5_2_7p62',[15.24,12.5],[-3.81,-7.9],[(1,0,0,3,1.3),(2,7.62,0,3,1.3)])
custom('Fuse_215_Axial_P30mm',[22.5,5.8],[-11.25,-2.9],[(1,-15,0,1.8,.9),(2,15,0,1.8,.9)])
pos={
'PS101':(14.6,14.2,0),'K101':(69.5,47.5,180),'U101':(80,23,0),'U102':(65,36,0),'L101':(71,36,0),'C101':(61,36,90),'C102':(67,32,90),'C103':(76,36,90),'C104':(80,36,90),'C105':(69,16,90),'Q101':(76,48,0),'D101':(75,43,0),'R101':(80,48,90),'R102':(80,51,90),'R103':(68.5,20,90),'C106':(68.5,24,90),'R104':(92,34,0),'R105':(96,34,0),'R106':(70,33,0),'U103':(60,29,0),'R107':(61,25,0),'R108':(64,25,0),'C107':(59,33,90),'J102':(28.5,45.76,90),'J104':(62,7,90),'SW101':(70.75,74.25,0),'LED101':(82.73,8.5,0),'R110':(68,75,0),'R111':(85,12,0),
'U201':(39.5,75,270),'U202':(59,64.5,180),'PS201':(59,78,180),'RS201':(40,63.5,270),'J201':(28.5,62,90),'R201':(38,68.5,270),'R202':(34,68.5,270),'C201':(36,67.8,90),'C202':(32,67.8,90),'RV201':(14,36,90),'RV202':(14,42,90),'RV203':(14,48,90),'RV204':(14,54,90),'RV205':(18,54,90),'RV206':(31,80,0),'RV207':(35,82,0),'CV201':(31,83,0),'CV202':(38.5,82.5,90),'R203':(45,67.5,0),'C203':(44,70.5,0),'C204':(47.5,70.5,0),'C205':(49,67,0),'C206':(32,70.8,0),'C207':(28.5,70.8,0),'R204':(47,63,90),'C208':(44,63,90),'Y201':(48,80.5,90),'CX201':(43.8,82.5,90),'CP201':(67,76,90),'CP202':(67,80,90),'CP203':(52,73,90),'CP204':(52,76,90),'CI201':(67,63,90),'CI202':(51,63,90),'R205':(49.5,60.5,0),'R206':(67,68,90),
'R301':(8,31,0),'R302':(20,31,0),'R303':(38,35,0),'R304':(32,31,0),'U301':(55,38,0),'R305':(64,40,90),'C301':(62,33,0),
'U402':(90,48,0),'R402':(94,49,0),'C402':(90,51.5,0),'U403':(90,57.5,0),'R403':(94,56,0),'R404':(94,59,0),'C403':(87,55,0),'U404':(82,73,0),'C404':(79,72,0),'J403':(94,39,0),'SW401':(84.75,65.25,0),'R405':(87,73,0),'R407':(91,72.5,0),'C405':(88,80,0),'U405':(83,80,0),'C406':(79,82,0),'Q401':(74,58,0),'R409':(75,55,0),'Q402':(80,58,0),'Q403':(80,62,0),'R410':(85,57,0),'R411':(85,60,0),'R412':(84,63,0),'R413':(78,65,0),'U406':(82,69,0),'C407':(78,69,0),'TP401':(95,64,0),'TP402':(95,68,0),'F501':(16.9,69.5,90)
}
# A separately reviewable placement override allows routing iterations without changing the circuit generator.
over=R/'placement_overrides.json'
if over.exists():pos.update({k:tuple(v) for k,v in json.loads(over.read_text()).items()})
missing=[c['ref'] for c in parts if c['ref'] not in pos]
if missing:raise RuntimeError('Missing physical placement:'+str(missing))
paths={'RevB':R.parent/'meter/RevB.pretty','Feedback':R.parent/'feedback/Feedback.pretty','Thermal':R.parent/'thermal/Thermal.pretty','Integrated':R/'Integrated.pretty'}
boards={'controller':'controller/carbonmirror.kicad_pcb','meter':'meter/meter.kicad_pcb','feedback':'feedback/output_feedback.kicad_pcb','thermal':'thermal/thermal_controller.kicad_pcb'}
sources={}
for mod,path in boards.items():
 if (R.parent/path).exists():sources[mod]=p.LoadBoard(str(R.parent/path))
b=p.BOARD();b.GetDesignSettings().SetCopperLayerCount(4);b.GetDesignSettings().SetBoardThickness(p.FromMM(1.6));names=sorted(set(n for c in parts for n in c['pins'].values() if n));nets={}
for n in names:net=p.NETINFO_ITEM(b,n);b.Add(net);nets[n]=net
for c in parts:
 print('Loading',c['ref'],c['footprint'],flush=True)
 lib,name=c['footprint'].split(':');root=paths.get(lib,Path('/usr/share/kicad/footprints')/(lib+'.pretty'));f=p.FootprintLoad(str(root),name) if root.exists() else None
 if not f:
  old=next(ff for ff in sources[c['source_module']].GetFootprints() if ff.GetReference()==c['source_ref']);f=p.FOOTPRINT(old)
  # Materialize the exact source footprint into a local library for offline editability.
  root.mkdir(exist_ok=True);f.SetOrientationDegrees(0);f.SetPosition(vec(0,0));f.SetFPID(p.LIB_ID(lib,name));p.PCB_IO_KICAD_SEXPR().FootprintSave(str(root),f)
 f.SetReference(c['ref']);f.SetValue(c['value']);x,y,a=pos[c['ref']];f.SetPosition(vec(x,y));f.SetOrientationDegrees(a)
 b.Add(f)
 if c['ref']=='F501':f.Flip(f.GetPosition(),False)
 f.SetPath(p.KIID_PATH('/'+uid('root')+'/'+uid(c['ref'])))
 for d in f.Pads():
  n=c['pins'].get(d.GetNumber());d.SetNet(nets[n] if n else b.FindNet(0))
 f.Reference().SetLayer(p.B_Fab if f.GetLayer()==p.B_Cu else p.F_Fab);f.Reference().SetTextSize(vec(.8,.8));f.Value().SetVisible(False)
 # Reference factory art remains in F.Fab; crowded source silks are omitted from this review candidate.
 for g in list(f.GraphicalItems()):
  if g.GetLayer()==p.F_SilkS:g.SetLayer(p.F_Fab)
# Shared mechanics outline:100x85,R10; left12x14 and right6x10 rounded feedthrough notches.
def line(a,z):
 g=p.PCB_SHAPE();g.SetShape(p.SHAPE_T_SEGMENT);g.SetStart(vec(*a));g.SetEnd(vec(*z));g.SetLayer(p.Edge_Cuts);g.SetWidth(p.FromMM(.05));b.Add(g)
def arc(a,m,z):
 g=p.PCB_SHAPE();g.SetShape(p.SHAPE_T_ARC);g.SetArcGeometry(vec(*a),vec(*m),vec(*z));g.SetLayer(p.Edge_Cuts);g.SetWidth(p.FromMM(.05));b.Add(g)
line((10,0),(90,0));arc((90,0),(97.0710678,2.9289322),(100,10));line((100,10),(100,20.5));line((100,20.5),(95,20.5));arc((95,20.5),(94.2928932,20.7928932),(94,21.5));line((94,21.5),(94,29.5));arc((94,29.5),(94.2928932,30.2071068),(95,30.5));line((95,30.5),(100,30.5));line((100,30.5),(100,75));arc((100,75),(97.0710678,82.0710678),(90,85));line((90,85),(10,85));arc((10,85),(2.9289322,82.0710678),(0,75));line((0,75),(0,64.5));line((0,64.5),(11,64.5));arc((11,64.5),(11.7071068,64.2071068),(12,63.5));line((12,63.5),(12,51.5));arc((12,51.5),(11.7071068,50.7928932),(11,50.5));line((11,50.5),(0,50.5));line((0,50.5),(0,10));arc((0,10),(2.9289322,2.9289322),(10,0))
for i,(x,y) in enumerate([(6,6.5),(94,6.5),(6,78.5),(94,78.5)]):
 f=p.FootprintLoad('/usr/share/kicad/footprints/MountingHole.pretty','MountingHole_3.2mm_M3');f.SetReference('H'+str(i+1));f.SetPosition(vec(x,y));f.Reference().SetLayer(p.F_Fab);b.Add(f)
 for layer in (p.F_CrtYd,p.B_CrtYd):
  g=p.PCB_SHAPE();g.SetShape(p.SHAPE_T_CIRCLE);g.SetStart(vec(x,y));g.SetEnd(vec(x+3.5,y));g.SetLayer(layer);g.SetWidth(p.FromMM(.05));b.Add(g)
for text,x,y,size in [('CARBENTRA INTEGRATED B',76,4,1),('DEVELOPMENT / NO ENERGIZATION',51,84,.7),('HOT: LINE REFERENCED',22,30,.7),('ISOLATED LOGIC',82,37,.8)]:
 t=p.PCB_TEXT(b);t.SetText(text);t.SetPosition(vec(x,y));t.SetTextSize(vec(size,size));t.SetTextThickness(p.FromMM(.12));t.SetLayer(p.Dwgs_User);b.Add(t)
p.SaveBoard(str(R/'integrated.kicad_pcb'),b)
(R/'placement.json').write_text(json.dumps({'status':'PLACEMENT CANDIDATE; no routing proof yet','board_mm':[100,85,1.6],'corner_radius_mm':10,'layer_count':4,'frame':'PCB upper-leftXY,mm; mechanics x=pcb_x-50,y=42.5-pcb_y; board bottom assembly z11.5','positions':pos,'bottom_components':['F501'],'holes_mm':[[6,6.5,3.2],[94,6.5,3.2],[6,78.5,3.2],[94,78.5,3.2]],'mount_keepout_diameter_mm':7,'left_notch_pcb_mm':[0,50.5,12,14],'right_notch_pcb_mm':[94,20.5,6,10]},indent=2))
# Library paths remain local and explicit, rather than relying on a user's global installation.
(R/'fp-lib-table').write_text('(fp_lib_table '+''.join(f'(lib (name "{lib}") (type "KiCad") (uri "${{KIPRJMOD}}/{__import__("os").path.relpath(path,R)}") (options "") (descr "Revision B candidate"))' for lib,path in paths.items())+')')
if not (R/'integrated.kicad_pro').exists():(R/'integrated.kicad_pro').write_text((R.parent/'controller/carbonmirror.kicad_pro').read_text())
(R/'integrated.kicad_dru').write_text((R/'design_rules.kicad_dru').read_text())
conf=json.loads((R/'integrated.kicad_pro').read_text());conf.setdefault('board',{}).setdefault('design_settings',{}).setdefault('rules',{}).update(min_through_hole_diameter=.2,min_via_diameter=.45);(R/'integrated.kicad_pro').write_text(json.dumps(conf,indent=2))
print('Placed',len(parts),'electrical components;',len(names),'nets')
