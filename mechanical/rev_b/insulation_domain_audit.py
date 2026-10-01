#!/usr/bin/python3
from carbentra_tools import FREECAD_LIB, FONT_REGULAR, PYTHON, kicad_resource
"""Read-only nominal 3D insulation-domain proximity audit. NOT safety clearance certification.
Only writes insulation_domain_report.json/.md; never recomputes/saves source CAD or PCB.
"""
import sys,json,math,hashlib,re,time,zipfile
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[1]
sys.path.extend([FREECAD_LIB,str(BASE)])
import FreeCAD as A,Part
from carbentra_pcb import pcbnew as pcb
import socket_b_features as mech
CONTACT_ONLY='--affected-contact' in sys.argv
RF_ONLY='--rf-reservation' in sys.argv
EXACT_MIRROR='--exact-mirror' in sys.argv
INCREMENTAL='--affected-rear' in sys.argv or CONTACT_ONLY or RF_ONLY or EXACT_MIRROR
PRIOR=json.loads((BASE/'insulation_domain_report.json').read_text(encoding='utf-8')) if INCREMENTAL else None
V=A.Vector;P=json.loads((BASE/'design_parameters.json').read_text(encoding='utf-8'));Z=P['pcb']['bottom_z'];E=ROOT/'electronics/rev_b/integrated'
paths=[BASE/'CARBENTRA-P16-B-base-provisional.FCStd',BASE/'socket_b_features.py',BASE/'power_links.py',BASE/'design_parameters.json',E/'integrated.kicad_pcb',E/'exports/placement_assembly.FCStd',E/'exports/component_envelopes.json',E/'electrical_manifest.json',E/'exports/remote_head_assembled.step']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
snapshot={p.relative_to(ROOT).as_posix():{'sha256':sha(p),'mtime_ns':p.stat().st_mtime_ns}for p in paths if p.exists()}
PCB_CHANGED=bool(INCREMENTAL and snapshot[(E/'integrated.kicad_pcb').relative_to(ROOT).as_posix()]['sha256']!=PRIOR['input_snapshot'][(E/'integrated.kicad_pcb').relative_to(ROOT).as_posix()]['sha256'])
fixed_input_reconciliation=[]
if INCREMENTAL:
 for fixed in [E/'exports/placement_assembly.FCStd',E/'exports/component_envelopes.json',E/'electrical_manifest.json',E/'exports/remote_head_assembled.step']:
  key=fixed.relative_to(ROOT).as_posix()
  expected=PRIOR.get('postflight_metadata_reconciliation',{}).get('updated_json_hashes',{}).get(key,PRIOR['input_snapshot'][key]['sha256'])
  if snapshot[key]['sha256']!=expected:
   backups=[f for f in fixed.parent.glob(fixed.stem+'.*.FCBak')if sha(f)==expected]if fixed.suffix=='.FCStd'else []
   def breps(f):
    with zipfile.ZipFile(f)as z:return {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()if n.lower().endswith('.brp')}
   if backups and breps(backups[0]) and breps(backups[0])==breps(fixed):
    fixed_input_reconciliation.append({'file':key,'reason':'Re-export changed container metadata; every named embedded BRep is byte-identical to prior audit input','matching_backup':backups[0].relative_to(ROOT).as_posix(),'brep_member_count':len(breps(fixed))})
   elif fixed.name=='component_envelopes.json':
    jj=json.loads(fixed.read_text(encoding='utf-8'));dd=A.openDocument(str(E/'exports/placement_assembly.FCStd'));old_leads={q['id']:q for q in PRIOR['lead_assignments']};bad=[]
    for q in jj['components']+jj['leads']:
     oo=dd.getObject(q['object']);bb=oo.Shape.BoundBox;vals=[bb.XMin,bb.YMin,bb.ZMin,bb.XLength,bb.YLength,bb.ZLength]
     if max(abs(x-y)for x,y in zip(vals,q['min_xyz_mm']+q['size_xyz_mm']))>1e-6 or not q['object'].startswith('MainB_'+q['ref']):bad.append(q['object'])
     if q['role']!='component' and(q['object']not in old_leads or old_leads[q['object']]['representation']!=q['role']):bad.append(q['object'])
    if bad:raise RuntimeError('Envelope mapping changed: '+str(bad))
    fixed_input_reconciliation.append({'file':key,'reason':'Updated metadata; all referenced envelopes match unchanged embedded native BRep geometry and prior lead roles/ref mapping','records_checked':len(jj['components'])+len(jj['leads'])})
   else:raise RuntimeError('Fixed electronics geometry input changed; full rerun required: '+key)
D=A.openDocument(str(paths[0]));M={o.Name:o.Shape.copy() for o in D.Objects if hasattr(o,'PartKind')}
ED=A.openDocument(str(E/'exports/placement_assembly.FCStd'));B=pcb.LoadBoard(str(E/'integrated.kicad_pcb'));env=json.loads((E/'exports/component_envelopes.json').read_text(encoding='utf-8'));em=json.loads((E/'electrical_manifest.json').read_text(encoding='utf-8'));byref={c['ref']:c for c in em['components']};fps={f.GetReference():f for f in B.GetFootprints()}
def domain(net):return 'primary' if net.startswith('HOT') or net in ('RAW_L','RAW_N') else 'isolated' if net and net!='PE' else 'unclassified'
def world(q,z):return V(pcb.ToMM(q.x)-50,42.5-pcb.ToMM(q.y),z)
def item(name,shape,kind,net=None,**kw):return {'id':name,'shape':shape,'kind':kind,'net':net,**kw}
def serial(o):return {k:v for k,v in o.items()if k!='shape' and not k.startswith('_')}
src=[];groups={g:[] for g in ['isolated_external_copper','isolated_solder_tails','isolated_package_envelopes','accessible_controls_and_guide_envelopes','accessible_case_screws','rf_service_loop_reservation','isolated_internal_copper','mixed_domain_package_envelopes','remote_sensor_assembly']}
print('STAGE bare portions',flush=True)
# Covered and bare portions of the same solid links are deliberately separate.
for name,path in mech.links.ROUTES.items():
 a,b=mech.links.TRIMS[name];L=sum(e.Length for e in path.edges)
 for end,sh in [('start',path.pipe(1.0,0,L-a)),('end',path.pipe(1.0,L-b,0))]:src.append(item('PowerCore_'+name+'__bare_'+end,sh,'bare_link_end',route=name,trim_length_mm=a if end=='start' else b))
 src.append(item('PowerCore_'+name+'__covered',path.pipe(1.0,a,b),'covered_link_core',route=name,_pruning_boxes=[[e.BoundBox.XMin-1,e.BoundBox.YMin-1,e.BoundBox.ZMin-1,e.BoundBox.XMax+1,e.BoundBox.YMax+1,e.BoundBox.ZMax+1]for e in path.edges],insulation='Nominal 1mm carrier wall, resin and joints unqualified; no air-gap inference'))
for n in ['MainFuseClip1','MainFuseClip2','MainFuseCollector1','MainFuseCollector2','MainFuseCap1','MainFuseCap2','ThermalBody','ThermalLead1','ThermalLead2','Contact_L','Contact_N','Blade_L','Blade_N']:
 if n in M:src.append(item(n,M[n],'fuse_metal'if n.startswith('MainFuse')else 'potential_primary_thermal_body_envelope'if n=='ThermalBody'else 'thermal_cutoff_lead'if n.startswith('Thermal')else 'primary_contact_or_blade'))
print('STAGE package domains',flush=True)
# Package body domains from complete pin-net manifest; mixed packages never assigned wholly isolated.
for c in env['components']:
 if c['ref'] not in byref:continue
 ds={domain(n)for n in byref[c['ref']]['pins'].values()if n};ds.discard('unclassified')
 group='isolated_package_envelopes'if ds=={'isolated'}else 'mixed_domain_package_envelopes'if ds=={'primary','isolated'}else None
 if group:
  sh=ED.getObject(c['object']).Shape.copy();sh.translate(V(0,0,Z));groups[group].append(item(c['object'],sh,'package_envelope',ref=c['ref'],representation='Nominal/max vendor-dimension or F.Fab package envelope, not exposed copper or detailed supplier solid'))
print('STAGE tails',flush=True)
# Match tails by actual pad location, not FreeCAD's duplicate-name suffixes.
lead_assignments=[]
for c in env['leads']:
 sh=ED.getObject(c['object']).Shape.copy();sh.translate(V(0,0,Z));fp=fps[c['ref']]
 candidates=[]
 for pad in fp.Pads():
  if pcb.ToMM(pad.GetDrillSize().x)<=.25:continue
  pt=world(pad.GetPosition(),Z+1.6)
  candidates.append((sh.distToShape(Part.Vertex(pt))[0],pad))
 if not candidates:continue
 dd,pad=min(candidates,key=lambda a:a[0]);net=pad.GetNetname();dom=domain(net)
 o=item(c['object'],sh,'primary_solder_tail'if dom=='primary'else 'isolated_solder_tail',net,ref=c['ref'],pin=pad.GetNumber(),representation=c['role'],pad_assignment_distance_mm=dd)
 lead_assignments.append(serial(o))
 if dom=='primary':src.append(o)
 elif dom=='isolated':groups['isolated_solder_tails'].append(o)
print('STAGE copper pads',flush=True)
# Use native KiCad effective pad polygons. Copper z/thickness reproduce the supplied visualization export.
levs=[(pcb.F_Cu,Z+1.6,.07,'isolated_external_copper'),(pcb.B_Cu,Z-.07,.07,'isolated_external_copper'),(pcb.In1_Cu,Z+1.315,.035,'isolated_internal_copper'),(pcb.In2_Cu,Z+.25,.035,'isolated_internal_copper')]
for fp in B.GetFootprints():
 for pi,pad in enumerate(fp.Pads()):
  net=pad.GetNetname()
  if domain(net)!='isolated'or pad.GetAttribute()==pcb.PAD_ATTRIB_NPTH:continue
  for layer,z,th,group in levs:
   if not pad.IsOnLayer(layer):continue
   poly=pad.GetEffectivePolygon(layer)
   for j in range(poly.OutlineCount()):
    curve=poly.COutline(j);pts=[world(curve.CPoint(k),z)for k in range(curve.PointCount())]
    if len(pts)<3:continue
    sh=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,th));dr=pcb.ToMM(pad.GetDrillSize().x)
    if dr>0:sh=sh.cut(Part.makeCylinder(dr/2,th+.2,world(pad.GetPosition(),z-.1)))
    groups[group].append(item(f'Pad_{B.GetLayerName(layer)}_{fp.GetReference()}_{pad.GetNumber()}_{pi}_{j}',sh,'native_pad_polygon',net,ref=fp.GetReference(),pin=pad.GetNumber()))
print('STAGE tracks',flush=True)
# Track capsules from native centerlines; vias use conservative copper annular columns.
for i,t in enumerate(B.GetTracks()):
 net=t.GetNetname()
 if domain(net)!='isolated':continue
 if isinstance(t,pcb.PCB_VIA):
  rad=pcb.ToMM(t.GetWidth(pcb.F_Cu))/2;dr=pcb.ToMM(t.GetDrillValue())/2;v=world(t.GetPosition(),Z-.07)
  sh=Part.makeCylinder(rad,1.74,v).cut(Part.makeCylinder(dr,1.94,v-V(0,0,.1)))
  groups['isolated_external_copper'].append(item('Via_reserve_'+str(i),sh,'via_annular_column_reserve',net,representation='Conservative full land annulus through board; not measured barrel plating'))
  continue
 layer=t.GetLayer();rec=next((r for r in levs if r[0]==layer),None)
 if not rec:continue
 _,z,th,group=rec;a=world(t.GetStart(),z);b=world(t.GetEnd(),z);v=b-a;L=v.Length;r=pcb.ToMM(t.GetWidth())/2
 if L<1e-6:continue
 n=V(-v.y/L*r,v.x/L*r,0);pts=[a+n,b+n,b-n,a-n]
 rect=Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(V(0,0,th))
 sh=Part.Compound([rect,Part.makeCylinder(r,th,a),Part.makeCylinder(r,th,b)])
 groups[group].append(item('Track_'+B.GetLayerName(layer)+'_'+str(i),sh,'native_track_capsule',net))
# Exact native filled copper, spatially partitioned with KiCad integer Boolean clipping.
# Partitioning changes query speed, not occupied copper. No outline simplification.
print('STAGE native filled zones',flush=True)
fill_metadata=[]
for zi,zone in enumerate(B.Zones()):
 if not zone.IsFilled() or domain(zone.GetNetname())!='isolated':continue
 layer=zone.GetLayer();rec=next((r for r in levs if r[0]==layer),None)
 if not rec:continue
 _,z,th,group=rec;poly=zone.GetFilledPolysList(layer);count=0
 for gx in range(0,100,10):
  for gy in range(0,90,10):
   clip=pcb.SHAPE_POLY_SET();clip.NewOutline()
   for xx,yy in [(gx,gy),(gx+10,gy),(gx+10,gy+10),(gx,gy+10)]:clip.Append(pcb.FromMM(xx),pcb.FromMM(yy))
   cut=pcb.SHAPE_POLY_SET();cut.BooleanIntersection(poly,clip)
   for oi in range(cut.OutlineCount()):
    curve=cut.COutline(oi);pts=[world(curve.CPoint(k),z)for k in range(curve.PointCount())]
    if len(pts)<3:continue
    face=Part.Face(Part.makePolygon(pts+[pts[0]]))
    for hi in range(cut.HoleCount(oi)):
     hole=cut.CHole(oi,hi);hp=[world(hole.CPoint(k),z)for k in range(hole.PointCount())]
     if len(hp)>=3:face=face.cut(Part.Face(Part.makePolygon(hp+[hp[0]])))
    sh=face.extrude(V(0,0,th))
    if sh.isNull() or sh.Volume<=1e-12:continue
    assert sh.isValid(),('invalid filled-zone partition',zi,gx,gy,oi)
    groups[group].append(item(f'FilledZone_{B.GetLayerName(layer)}_{zi}_cell_{gx}_{gy}_{oi}',sh,'native_filled_zone_partition',zone.GetNetname(),representation='Native filled polygon clipped into10mm cells using exact KiCad integer Boolean; no outline simplification'))
    count+=1
 fill_metadata.append({'zone':zi,'net':zone.GetNetname(),'layer':B.GetLayerName(layer),'original_outlines':poly.OutlineCount(),'original_vertices':sum(poly.COutline(j).PointCount()for j in range(poly.OutlineCount())),'query_partition_count':count,'z_interval_mm':[z,z+th]})

print('STAGE guides',flush=True)
# Accessible pushers are insulating components; guide outer envelopes are conservative solid cylinders.
for n,key,r in [('LocalButton','local',3.0),('RearmButton','rearm',2.7)]:
 groups['accessible_controls_and_guide_envelopes'].append(item(n,M[n],'plastic_pusher'))
 x,y=P['controls'][key];sh=Part.makeCylinder(r,62.6-34,V(x,y,34))
 if n=='LocalButton':sh=Part.Compound([sh,Part.makeCylinder(5.5,2.6,V(x,y,60))])
 groups['accessible_controls_and_guide_envelopes'].append(item(n+'_GuideOuterEnvelope',sh,'plastic_guide_outer_envelope',representation='Outer envelope of front-lid guide, not a metal touch probe or certified insulating barrier'))
if 'RFServiceSlackEnvelope'in M:
 groups['rf_service_loop_reservation'].append(item('RFServiceSlackEnvelope',M['RFServiceSlackEnvelope'],'nonphysical_isolated_RF_routing_reservation',representation='NON-PHYSICAL/default-hidden annular routing reservation for about44mm of selected100mm coax; not an actual shield/cable solid, qualified bend or strain relief'))
for n in ['Screw_0','Screw_1','Screw_2','Screw_3']:
 groups['accessible_case_screws'].append(item(n,M[n],'case_screw_major_envelope',representation='Nominal metallic thread-major/shaft/head envelope; rear head potentially accessible when unplugged or partly withdrawn; insulating-boss engagement ignored as intentional mounting'))
# Already world-placed sensor assembly is isolated circuitry; solids are conservatively considered as a whole.
if (E/'exports/remote_head_assembled.step').exists():
 sh=Part.Shape();sh.read(str(E/'exports/remote_head_assembled.step'))
 groups['remote_sensor_assembly'].append(item('RemoteHead_assembled_all_solids',sh,'remote_sensor_package_and_copper',representation='Whole world-placed STEP assembly, not all surfaces conductive'))
print('INPUTS',len(src),'primary source regions;', {g:len(v)for g,v in groups.items()},flush=True)
def bbox_lower(a,b):
 a=a.BoundBox;b=b.BoundBox
 return math.sqrt(sum(max(0,getattr(a,f'{v}Min')-getattr(b,f'{v}Max'),getattr(b,f'{v}Min')-getattr(a,f'{v}Max'))**2 for v in 'XYZ'))
def source_lower(a,b):
 if '_pruning_boxes' not in a:return bbox_lower(a['shape'],b['shape'])
 bb=b['shape'].BoundBox;t=[bb.XMin,bb.YMin,bb.ZMin,bb.XMax,bb.YMax,bb.ZMax]
 return min(math.sqrt(sum(max(0,v[k]-t[k+3],t[k]-v[k+3])**2 for k in range(3)))for v in a['_pruning_boxes'])
def pair(a,b):
 dist,points,_=a['shape'].distToShape(b['shape']);vol=0
 if dist<1e-6 and a['shape'].BoundBox.intersect(b['shape'].BoundBox):vol=a['shape'].common(b['shape']).Volume
 return {'source':serial(a),'target':serial(b),'distance_mm':dist,'closest_points_mm':[[list(x),list(y)]for x,y in points[:1]],'common_volume_mm3':vol,'meaning':'Euclidean BRep separation only; not an established air/creepage/solid-insulation withstand result'}
nearest=[];intersections=[]
def affected(a):
 if RF_ONLY:return False
 if EXACT_MIRROR:return a['id']in('Contact_L','Contact_N','ThermalBody','ThermalLead1','ThermalLead2')
 if CONTACT_ONLY:return a['id']=='Contact_L'
 return a['id']in('Blade_L','Blade_N')or a['id'].startswith(('PowerCore_L_RAW__','PowerCore_N_RAW__'))
NEW_FILL=bool(INCREMENTAL and not PRIOR.get('filled_zone_metadata'))
if RF_ONLY:
 proof=PRIOR.get('rf_geometry_reconciliation',{})
 assert proof.get('updated_native_sha256')==sha(BASE/'CARBENTRA-P16-B-base-provisional.FCStd'),'RF-only mode requires saved cleaned-BRep reconciliation for this exact native file'
 assert proof.get('power_link_generator_unchanged') and len(proof.get('parts',[]))==33
 assert all(q['identical_clean_brep']for q in proof['parts'])
cached={(q['source']['id'],q['target_group']):q for q in PRIOR['nearest_by_source_and_target_group']}if INCREMENTAL else {}
src.sort(key=lambda a:a['kind']=='covered_link_core')
for ix,a in enumerate(src):
 print('SOURCE',ix,a['id'],flush=True)
 for group,targets in groups.items():
  previous=cached.get((a['id'],group))
  need_new_group=INCREMENTAL and previous is None
  need_copper=PCB_CHANGED and group in('isolated_external_copper','isolated_internal_copper')
  need_fill=NEW_FILL and group=='isolated_internal_copper'
  if INCREMENTAL and not affected(a) and not(need_new_group or need_copper or need_fill):
   if previous:nearest.append(previous)
   intersections.extend(q for q in PRIOR.get('volume_intersections',[])if q['source']['id']==a['id']and q['target_group']==group)
   continue
  selected=([b for b in targets if b['kind']=='native_filled_zone_partition']if INCREMENTAL and not affected(a) and need_fill and not PCB_CHANGED else targets)
  print('GROUP',group,flush=True)
  candidates=sorted(((source_lower(a,b),b)for b in selected),key=lambda x:x[0]);best=(previous if INCREMENTAL and not affected(a) and need_fill and not PCB_CHANGED else None)
  for lower,b in candidates:
   if best is not None and lower>best['distance_mm']+1e-7:break
   q=pair(a,b);q['target_group']=group
   if best is None or q['distance_mm']<best['distance_mm']:best=q
   if q['common_volume_mm3']>1e-6:intersections.append(q)
  if best:
   nearest.append(best)
   print('MIN',a['id'],group,best['target']['id'],round(best['distance_mm'],6),flush=True)
 if(ix+1)%10==0:print('AUDITED',ix+1,'/',len(src),flush=True)
summary={g:sorted([q for q in nearest if q['target_group']==g],key=lambda q:q['distance_mm'])[:10] for g in groups}
thermal={}
if groups['remote_sensor_assembly']and'ThermalPad'in M:
 head=groups['remote_sensor_assembly'][0]
 for n in ['Contact_L','ThermalPad','ThermalBody','ThermalLead1','ThermalLead2']:
  thermal[n]=pair(item(n,M[n],'thermal_interface_member'),head)
 thermal['intent']='Nominal0.5mm thermal pad intentionally separates primary pickup and isolated head. Solid-insulation material/system qualification remains OPEN.'
changed=[p.relative_to(ROOT).as_posix()for p in paths if p.exists()and p.relative_to(ROOT).as_posix()in snapshot and sha(p)!=snapshot[p.relative_to(ROOT).as_posix()]['sha256']]
report={'brand':'CARBENTRA','revision':'CARBENTRA-P16-EVT-B','status':'DEVELOPMENT AUDIT / NO INSULATION OR ENERGIZATION APPROVAL','scope':'Concrete nominal 3D proximity of exposed primary link ends, fuse metal, thermal-cutoff leads, contacts and primary solder tails to isolated circuitry and controls; covered-link/core distances separately identified','units':'mm','rf_geometry_reconciliation':(PRIOR.get('rf_geometry_reconciliation')if INCREMENTAL else None),'fixed_input_reconciliation':fixed_input_reconciliation,'filled_zone_metadata':fill_metadata,'incremental_scope':(('Exact-mirror export-fidelity correction: rechecked Contact_L,Contact_N,ThermalBody,ThermalLead1,ThermalLead2 against all targets and thermal head; added ThermalBody conservatively as potentially primary, total53 sources. Prior other sources/target layouts unchanged.'if EXACT_MIRROR else'Reconciled33 unchanged cleaned BReps; checked new non-physical RF service-loop reservation against all52 primary regions; retained verified prior distances for unchanged source/target geometry.'if RF_ONLY else'Recomputed reduced Contact_L against all target classes and all 52 primary regions against newly added case-screw metal envelopes; retained prior unaffected results against unchanged copper/body inputs.'if CONTACT_ONLY else 'Recomputed Blade_L/Blade_N and rear L_RAW/N_RAW bare/covered regions after rear termination revision; if PCB changed, recomputed both external/internal copper for all 52 sources; retained only unaffected body/control/tail distances whose placement/envelope/pin-manifest inputs are unchanged; checked native filled-zone geometry against all 52 sources.')if INCREMENTAL else 'Full source/target distance audit'),'prior_full_audit_input_snapshot':(PRIOR['input_snapshot']if INCREMENTAL else None),'input_snapshot':snapshot,'inputs_changed_during_run':changed,'source_count':len(src),'target_counts':{g:len(v)for g,v in groups.items()},'classification':{'primary':'Native pad nets HOT* and RAW_L/RAW_N; explicit off-board power sources','isolated':'Nonempty other non-PE nets on this reviewed board; not an automatic rule for arbitrary designs','mixed_domain_packages':'PS101,K101,U202,PS201,U301 are package bodies only; their actual pads/tails are individually classified','lead_pad_matching':'Nearest THT native pad point to actual exported tail shape, at main PCB topz13.1; avoids FreeCAD duplicate-name suffix ambiguity'},'lead_assignments':lead_assignments,'nearest_by_source_and_target_group':nearest,'smallest_pairs_by_group':summary,'volume_intersections':intersections,'thermal_interface':thermal,'limitations':['All distances are direct Euclidean geometry, not a solved free-air path or surface creepage path. Plastic may lie between nearest points.','Six covered links have1mm nominal carrier wall,0.2mm nominal radial copper-to-carrier bore gap and unqualified resin/joints. Proximity through that plastic is not an8mm air-gap pass.','Thermal pad0.5mm is an intentional primary/isolated solid-insulation interface, not certified insulation.','Component envelopes use nominal/max vendor dimensions or F.Fab rectangles, not manufacturer detailed CAD. lead_reserve geometries are conservative pin reservations.','Copper z/thickness are visualization inputs(.07outer/.035inner), not a released layer stack. Via columns are conservative annular envelopes.','Internal tracks/pads and native filled GND_ISO plane polygons are included in internal-copper results. Filled polygons are partitioned using exact KiCad integer clipping. Internal-layer separation is solid insulation, not an air-clearance result. Native PCB DRC remains necessary.','Accessible pusher and guide-envelope distances are to insulating geometry, not standardized access probes or touchable metal.','RFServiceSlackEnvelope is non-physical reference geometry, excluded from physical part count/mass; distances to it are conservative routing-reservation distances, not actual coax-shield clearance. About44mm service-loop allocation assumesR>=6mm/loopR~7mm; vendor bend and strain relief remain unqualified.','Four case screws are modeled metallic major/shaft/head envelopes; distance to an embedded shaft is not a certified touch path. Boss plastic and partial-withdrawal access require review.','ThermalBody is conservatively treated as a potentially-primary metal/body envelope until its exact construction and insulation status are qualified; it is separate from the actual exposed TF1 lead solids.','No tolerance, warpage, contamination, material CTI, impulse, working-voltage, dielectric, thermal, spring-force or fault-withstand qualification.','Source CAD is opened read-only and not recomputed/saved; exposed-link segmentation is reconstructed from current power_links.py. Input hash consistency is reported.']}
(BASE/'insulation_domain_report.json').write_text(json.dumps(report,indent=2)+'\n', encoding='utf-8', newline='\n')
def name(q,k):return q[k]['id']+((' ['+q[k]['net']+']')if q[k].get('net')else'')
md=['# CARBENTRA CARBENTRA-P16-EVT-B · Insulation-domain proximity audit','','**Engineering development only. No electrical insulation or energization approval.**','',f'- Primary source regions: {len(src)}',f'- Source files changed during this audit: {len(changed)}',f'- Native filled-zone partitions: {sum(v["query_partition_count"]for v in fill_metadata)}',f'- Positive-volume intersections against all target groups: {len(intersections)} (package/guide overlaps are not automatically electrical shorts)','- Main PCB bottom z11.5; actual native pad/track net names classify domains','- All tabulated distances are nominal Euclidean BRep separation, not qualified clearance or creepage','','## Smallest pairs by target group','']
for g,qs in summary.items():
 md+=['### '+g,'','| Primary region | Target | Distance mm | Overlap mm³ |','|---|---|---:|---:|']
 for q in qs[:6]:md.append(f"| {name(q,'source')} | {name(q,'target')} | {q['distance_mm']:.4f} | {q['common_volume_mm3']:.6g} |")
 md+=['']
md+=['## Thermal-pickup interface','','| Member | Distance to world-placed isolated head, mm |','|---|---:|']
for n,q in thermal.items():
 if isinstance(q,dict):md.append(f"| {n} | {q['distance_mm']:.4f} |")
md+=['',thermal.get('intent','No remote head input available.'),'','## Positive-volume intersections','']
if intersections:
 for q in intersections:md.append(f"- {name(q,'source')} / {name(q,'target')}: {q['common_volume_mm3']:.6g}mm³; category {q['target_group']}")
else:md+=['No positive-volume intersections were found in these tested pairs. This does not prove electrical separation, safe access, or compliant solid insulation.']
md+=['','## Interpretation and open gates','']+['- '+s for s in report['limitations']]
md+=['','## Evidence and repeatability','','Run `/usr/bin/python3 mechanical/rev_b/insulation_domain_audit.py` from the repository. Full source hashes, exact closest-point coordinates, per-region minima and lead/pad assignments are in `insulation_domain_report.json`. No source geometry is modified.','', 'Primary references: [GB1002-2024 official record](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=F8C9E208891B7BB5AF1B3E64933693C2), [SHF fuse](https://www.schurter.com/en/datasheet/typ_SHF_6.3x32.pdf), [CQP clips](https://www.schurter.com/en/datasheet/typ_CQP.pdf). These sources do not certify the custom assembly.']
(BASE/'insulation_domain_report.md').write_text('\n'.join(md)+'\n', encoding='utf-8', newline='\n')
print('SUMMARY',json.dumps({g:[{'source':q['source']['id'],'target':q['target']['id'],'mm':round(q['distance_mm'],4),'volume':q['common_volume_mm3']}for q in qs[:3]]for g,qs in summary.items()}),flush=True)
print('CHANGED',changed,'INTERSECTIONS',len(intersections),flush=True)
# Compact engineering readout: keep exposed and covered minima distinct.
filters={
 'exposed_primary_to_any_isolated_copper':lambda q:q['target_group']in('isolated_external_copper','isolated_internal_copper','isolated_solder_tails') and q['source']['kind']!='covered_link_core',
 'exposed_primary_to_isolated_external_copper':lambda q:q['target_group']=='isolated_external_copper' and q['source']['kind']!='covered_link_core',
 'bare_link_ends_to_isolated_external_copper':lambda q:q['target_group']=='isolated_external_copper' and q['source']['kind']=='bare_link_end',
 'primary_solder_tails_to_isolated_external_copper':lambda q:q['target_group']=='isolated_external_copper' and q['source']['kind']=='primary_solder_tail',
 'covered_link_core_to_isolated_external_copper':lambda q:q['target_group']=='isolated_external_copper' and q['source']['kind']=='covered_link_core',
 'exposed_primary_to_controls':lambda q:q['target_group']=='accessible_controls_and_guide_envelopes' and q['source']['kind']!='covered_link_core',
 'exposed_primary_to_case_screw_metal':lambda q:q['target_group']=='accessible_case_screws' and q['source']['kind']!='covered_link_core',
 'exposed_primary_to_RF_routing_reservation':lambda q:q['target_group']=='rf_service_loop_reservation' and q['source']['kind']!='covered_link_core',
 'covered_link_core_to_RF_routing_reservation':lambda q:q['target_group']=='rf_service_loop_reservation' and q['source']['kind']=='covered_link_core',
 'covered_link_core_to_case_screw_metal':lambda q:q['target_group']=='accessible_case_screws' and q['source']['kind']=='covered_link_core',
 'covered_link_core_to_controls':lambda q:q['target_group']=='accessible_controls_and_guide_envelopes' and q['source']['kind']=='covered_link_core'}
report['engineering_highlights']={n:min((q for q in nearest if f(q)),key=lambda q:q['distance_mm'])for n,f in filters.items()if any(f(q)for q in nearest)}
report['metal_to_metal_volume_intersections']=[q for q in intersections if q['target_group']in('isolated_external_copper','isolated_internal_copper','isolated_solder_tails')]
report['nominal_geometric_screen']={'target_mm':8.4,'minimum_mm':report['engineering_highlights']['exposed_primary_to_any_isolated_copper']['distance_mm'],'met_nominally':report['engineering_highlights']['exposed_primary_to_any_isolated_copper']['distance_mm']>=8.4,'interpretation':'Project-only nominal 3D screen of exposed primary regions vs isolated main-board metal. Not actual free-air, creepage, solid-insulation or tolerance qualification; intentional remote thermal-head interface treated separately.'}
report['eight_mm_project_review_target']={'status':'NOT a standard-derived or certified limit; project screening target only','exposed_primary_minimum_mm':report['engineering_highlights']['exposed_primary_to_isolated_external_copper']['distance_mm'],'met_by_exposed_pair':report['engineering_highlights']['exposed_primary_to_isolated_external_copper']['distance_mm']>=8,'note':'A nominal distance over8mm would still require actual clearance/creepage/tolerance and insulation coordination review. Covered cores are never classified as8mm-air passes.'}
(BASE/'insulation_domain_report.json').write_text(json.dumps(report,indent=2)+'\n', encoding='utf-8', newline='\n')
readout=['## Key engineering findings','','| Region class | Source | Target | Nominal distance mm |','|---|---|---|---:|']
for n,q in report['engineering_highlights'].items():readout.append(f"| {n} | {name(q,'source')} | {name(q,'target')} | {q['distance_mm']:.4f} |")
readout+=['',('The exposed-primary minimum nominally meets the project 8.4 mm geometric screen.'if report['nominal_geometric_screen']['met_nominally']else'The exposed-primary minimum does NOT meet the project 8.4 mm geometric screen.')+' This is not a standard-derived acceptance criterion or a tolerance/insulation pass. Internal-layer distances include solid insulation. The thermal coupling is a separate 0.5 mm nominal solid-insulation interface.','',f"Metal-to-metal positive-volume crossings in the checked pairs: {len(report['metal_to_metal_volume_intersections'])}. No-crossing does not establish safe insulation.",'']
text=(BASE/'insulation_domain_report.md').read_text(encoding='utf-8');mark='## Smallest pairs by target group';text=text.replace(mark,'\n'.join(readout)+'\n'+mark,1);(BASE/'insulation_domain_report.md').write_text(text, encoding='utf-8', newline='\n')
