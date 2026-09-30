import sys,json,math,hashlib
from pathlib import Path
sys.path.append('/usr/lib/freecad/lib')
import FreeCAD as A,Part
import pcbnew as p
R=Path(__file__).resolve().parents[1];bodies_only='--bodies-only' in sys.argv;stem='placement_assembly' if bodies_only else 'integrated_assembly';b=p.LoadBoard(str(R/'integrated.kicad_pcb'));m=json.loads((R/'electrical_manifest.json').read_text());cs={c['ref']:c for c in m['components'] if c['board_designation']=='integrated'};doc=A.newDocument('CARBENTRA_CM_S16_EVT_B');objs=[];env=[];leads=[]
def V(x,y,z=0):return A.Vector(x-50,42.5-y,z)
def mm(v):return(p.ToMM(v.x),p.ToMM(v.y))
def add(name,shape,group,ref=None):
 o=doc.addObject('Part::Feature','MainB_'+name);o.Label=o.Name;o.Shape=shape;objs.append(o)
 if not shape.isNull():
  bb=shape.BoundBox;entry={'ref':ref or name,'object':o.Name,'board_id':'MainB','role':group,'min_xyz_mm':[bb.XMin,bb.YMin,bb.ZMin],'size_xyz_mm':[bb.XLength,bb.YLength,bb.ZLength]}
  if group=='component':env.append(entry)
  elif group in ('lead','lead_reserve'):leads.append(entry)
 return o
print('stageedges',flush=True)
edges=[]
for d in b.GetDrawings():
 if not isinstance(d,p.PCB_SHAPE) or d.GetLayer()!=p.Edge_Cuts:continue
 a=V(*mm(d.GetStart()));z=V(*mm(d.GetEnd()))
 edges.append(Part.Arc(a,V(*mm(d.GetArcMid())),z).toShape() if d.GetShape()==p.SHAPE_T_ARC else Part.makeLine(a,z))
print('stagewire',len(edges),flush=True)
wire=Part.Wire(Part.__sortEdges__(edges));shape=Part.Face(wire).extrude(A.Vector(0,0,1.6));holes=[]
for fp in b.GetFootprints():
 for pd in fp.Pads():
  dr=p.ToMM(pd.GetDrillSize().x)
  if dr>0:holes.append(Part.makeCylinder(dr/2,1.8,V(*mm(pd.GetPosition()),-.1)))
print('stageholes',len(holes),flush=True)
for i,hole in enumerate(holes):
 print('hole',i,flush=True)
 shape=shape.cut(hole)
print('aftercut',shape.isValid(),shape.Volume,flush=True)
add('PCB_100x85_R10_4layer',shape,'board')
print('boardadded',flush=True)
# Native candidate body surfaces, with maximum-envelope overrides for high-profile sourced parts.
print('stagecomponents',flush=True)
for fp in b.GetFootprints():
 ref=fp.GetReference()
 if ref not in cs:continue
 print('component',ref,flush=True)
 c=cs[ref];x,y=mm(fp.GetPosition());ang=fp.GetOrientationDegrees();z=1.6;height=c['height_mm'];bounds=[]
 if ref=='F501':
  # Fuse case maximum diameter5.8, length22.5; B-side1.5mm standoff.
  center=V(x,y,-4.4);axis=A.Vector(0,1,0);case=Part.makeCylinder(2.9,22.5,center-A.Vector(0,11.25,0),axis);add(ref,case,'component',ref)
  # The two leads preserve1.5mm straight run beyond each endcap before R2.25 bends.
  for sign in(-1,1):
   pts=[center+A.Vector(0,sign*11.25,0),center+A.Vector(0,sign*12.75,0),center+A.Vector(0,sign*15,2.25),center+A.Vector(0,sign*15,6.6)]
   mid=center+A.Vector(0,sign*(12.75+2.25/math.sqrt(2)),2.25-2.25/math.sqrt(2))
   spine=Part.Wire([Part.makeLine(pts[0],pts[1]),Part.Arc(pts[1],mid,pts[2]).toShape(),Part.makeLine(pts[2],pts[3])]);profile=Part.Wire([Part.makeCircle(.325,pts[0],A.Vector(0,sign,0))]);lead=spine.makePipeShell([profile],True,False);add(ref+'_FormedLead_'+str(sign),lead,'lead',ref)
  continue
 if ref in ('J102','J201'):
  body=Part.makeBox(15.24,12.5,21.5,A.Vector(-3.81,-4.6,1.6));body.rotate(A.Vector(0,0,0),A.Vector(0,0,1),ang);body.translate(V(x,y));add(ref,body,'component',ref)
  for pd in fp.Pads():
   px,py=mm(pd.GetPosition());pin=Part.makeBox(.9,.9,5.1,V(px-.45,py+.45,-3.5));add(ref+'_Pin'+pd.GetNumber(),pin,'lead',ref)
  continue
 if ref=='PS101':
  w,h=46.2,25.9;cx=x+19.25;cy=y+1.5;height=22.0
 elif ref in ('U202','PS201'):w,h=7.5,10.3;cx,cy=x,y
 elif ref=='RS201':w,h=(6.9,10.31) if round(ang)%180==90 else (10.31,6.9);cx,cy=x,y;height=2.92
 else:
  # Factory F.Fab from a fresh library footprint avoids treating text/silks as package geometry.
  lib,name=c['footprint'].split(':');paths={'Integrated':R/'Integrated.pretty','RevB':R.parent/'meter/RevB.pretty','Feedback':R.parent/'feedback/Feedback.pretty','Thermal':R.parent/'thermal/Thermal.pretty'};ff=p.FootprintLoad(str(paths.get(lib,Path('/usr/share/kicad/footprints')/(lib+'.pretty'))),name)
  if ff:ff.SetPosition(fp.GetPosition());ff.SetOrientationDegrees(ang)
  else:ff=fp
  for g in ff.GraphicalItems():
   if isinstance(g,p.PCB_SHAPE) and g.GetLayer()==p.F_Fab:
    bb=g.GetBoundingBox();bounds.append([p.ToMM(bb.GetLeft()),p.ToMM(bb.GetTop()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom())])
  if not bounds:continue
  xx=min(v[0] for v in bounds);yy=min(v[1] for v in bounds);w=max(v[2] for v in bounds)-xx;h=max(v[3] for v in bounds)-yy;cx=xx+w/2;cy=yy+h/2
 add(ref,Part.makeBox(w,h,height,V(cx-w/2,cy+h/2,z)),'component',ref)
 # Lead geometry is exact where manufacturer dimensions were obtained; other THT tails are conservative reserves.
 for pd in fp.Pads():
  dr=p.ToMM(pd.GetDrillSize().x)
  if dr<=.25 or pd.GetNumber()=='':continue
  px,py=mm(pd.GetPosition())
  if ref=='PS101':dia=1.;length=4.5;role='lead'
  elif ref.startswith('R3') and ref not in ('R305',):dia=.6;length=4.6;role='lead_reserve'
  else:dia=max(.3,dr-.2);length=4.6;role='lead_reserve'
  add(ref+'_Tail'+pd.GetNumber(),Part.makeCylinder(dia/2,length,V(px,py,1.6-length)),role,ref)
# Initial placement export intentionally contains no invented copper; later calls include actual routed items.
for i,t in enumerate([] if bodies_only else b.GetTracks()):
 if isinstance(t,p.PCB_VIA):
  x,y=mm(t.GetPosition());r=p.ToMM(t.GetWidth(p.F_Cu))/2;hole=p.ToMM(t.GetDrillValue())/2;add('Via_'+str(i),Part.makeCylinder(r,.07,V(x,y,1.67)).cut(Part.makeCylinder(hole,.07,V(x,y,1.67))),'via');continue
 a=mm(t.GetStart());z=mm(t.GetEnd());aa=V(*a);zz=V(*z);dx=zz.x-aa.x;dy=zz.y-aa.y;l=math.hypot(dx,dy);width=p.ToMM(t.GetWidth())
 if l<.001:continue
 lev={p.F_Cu:1.60,p.B_Cu:-.07,p.In1_Cu:1.315,p.In2_Cu:.25}[t.GetLayer()]
 sh=Part.makeBox(l,width,.07,A.Vector(aa.x,aa.y-width/2,lev));sh.rotate(A.Vector(aa.x,aa.y,lev),A.Vector(0,0,1),math.degrees(math.atan2(dy,dx)));add('Copper_'+b.GetLayerName(t.GetLayer()).replace('.','')+'_'+str(i),sh,'copper')
if not bodies_only:
 for fp in b.GetFootprints():
  for pd in fp.Pads():
   if pd.GetAttribute()==p.PAD_ATTRIB_NPTH:continue
   for layer,lev in ((p.F_Cu,1.6),(p.B_Cu,-.07),(p.In1_Cu,1.315),(p.In2_Cu,.25)):
    if not pd.IsOnLayer(layer):continue
    poly=pd.GetEffectivePolygon(layer)
    for j in range(poly.OutlineCount()):
     c=poly.COutline(j);pts=[V(*mm(c.CPoint(k)),lev)for k in range(c.PointCount())]
     if len(pts)<3:continue
     sh=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(A.Vector(0,0,.07 if layer in(p.F_Cu,p.B_Cu)else .035));dr=p.ToMM(pd.GetDrillSize().x)
     if dr>0:sh=sh.cut(Part.makeCylinder(dr/2,.2,V(*mm(pd.GetPosition()),lev-.05)))
     add('Pad_'+b.GetLayerName(layer).replace('.','')+'_'+fp.GetReference()+'_'+pd.GetNumber()+'_'+str(j),sh,'pad')
doc.recompute();doc.saveAs(str(R/'exports'/f'{stem}.FCStd'));Part.export(objs,str(R/'exports'/f'{stem}.step'))
with (R/'exports'/f'{stem}.obj').open('w') as f:
 off=1
 for o in objs:
  vs,fs=o.Shape.tessellate(.08);f.write('o '+o.Name+'\n')
  for v in vs:f.write(f'v {v.x:.5f} {v.y:.5f} {v.z:.5f}\n')
  for tri in fs:f.write('f '+' '.join(str(k+off) for k in tri)+'\n')
  off+=len(vs)
(R/'exports/component_envelopes.json').write_text(json.dumps({'board_id':'MainB','status':'ROUTED DEVELOPMENT CANDIDATE / NO ENERGIZATION','coordinate_system':'mm, centeredXY,boardbottomz0,topz1.6; assemblytranslationz11.5 provisional','board_mm':[100,85,1.6],'corner_radius_mm':10,'mount_holes_mm':[[-44,36,3.2],[44,36,3.2],[-44,-36,3.2],[44,-36,3.2]],'components':env,'leads':leads,'fuse_forming':{'pin_pitch_mm':30,'straight_beyond_max_case_mm':1.5,'bend_radius_mm':2.25,'lead_diameter_mm':.65,'body_max_mm':[22.5,5.8],'underside_standoff_mm':1.5,'max_depth_below_pcb_mm':7.3,'solder_tail_above_top_mm':.6},'terminal_entry_height_mm_above_pcb':{'nominal':7.5,'uncertainty_plus_minus':1,'basis':'inferred from manufacturer section drawing; not a dimensioned/qualified interface'},'limitations':['Candidate nominal/max body envelopes, not full manufacturer solids','Lead reserves identified separately; terminal0.9square/PSU1mm/fuse0.65mm geometry from sources','Actual pads/tracks/vias exported; copper raised for inspection, not a manufacturing stack model; planes authoritative in native PCB','No material, thermal, strain-relief, creepage, fault or insulation approval']},indent=2))
(R/'validation'/('placement_geometry.json' if bodies_only else 'geometry.json')).write_text(json.dumps({'board_sha256':hashlib.sha256((R/'integrated.kicad_pcb').read_bytes()).hexdigest(),'object_count':len(objs),'body_count':len(env),'lead_count':len(leads),'all_valid_positive_volume':all(o.Shape.isValid() and o.Shape.Volume>0 for o in objs)},indent=2));print('Exported',len(objs),'validobjects?',all(o.Shape.isValid() and o.Shape.Volume>0 for o in objs),'bodies',len(env))
