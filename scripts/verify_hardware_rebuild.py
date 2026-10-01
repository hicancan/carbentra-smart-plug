from carbentra_tools import FREECAD_LIB, FONT_REGULAR, PYTHON, kicad_resource
"""Compare a separate fresh source rebuild with retained native CAD; no CAD writes."""
from pathlib import Path
import argparse,sys,json,hashlib
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--rebuilt-root',type=Path,required=True)
args=parser.parse_args()
R=Path(__file__).resolve().parents[1];W=args.rebuilt_root.resolve()
sys.path.extend([FREECAD_LIB,str(R/'mechanical/rev_b')])
import FreeCAD as A,Part,socket_b_features
from cad_equivalence import compare_shapes,grouped_shapes,negative_controls
controls=negative_controls(Part,A.Vector)
rows=[]
def eq(a,b):
 aa=a.split();bb=b.split()
 if len(aa)!=len(bb):return False
 for x,y in zip(aa,bb):
  if x==y:continue
  try:
   if abs(float(x)-float(y))>1e-10:return False
  except ValueError:return False
 return True
for rel in ['mechanical/rev_b/CARBENTRA-P16-B-base-provisional.FCStd','mechanical/rev_b/CARBENTRA-P16-EVT-B.FCStd','mechanical/rev_b/CARBENTRA-P16-EVT-B_system_assembly.FCStd','electronics/rev_b/integrated/exports/placement_assembly.FCStd']:
 old=A.openDocument(str(R/rel));new=A.openDocument(str(W/rel));os=grouped_shapes(old);ns=grouped_shapes(new);check=[]
 for name in sorted(os.keys() | ns.keys()):
  if name not in os or name not in ns:check.append({'name':name,'passed':False,'missing':True});continue
  if len(os[name])!=len(ns[name]):check.append({'name':name,'passed':False,'count_mismatch':True});continue
  for (old_name,x),(new_name,y) in zip(os[name],ns[name]):
   result=compare_shapes(x,y)
   result.update(name=old_name,rebuilt_name=new_name,clean_brep_numeric_equal_1e_10=eq(x.cleaned().exportBrepToString(),y.cleaned().exportBrepToString()))
   check.append(result)
 rows.append({'file':rel,'object_count':len(check),'passed':all(q['passed'] for q in check),'objects':check})
 A.closeDocument(old.Name);A.closeDocument(new.Name)
 print(rel,rows[-1]['passed'],len(check),flush=True)
def board_signature(path):
    from carbentra_pcb import pcbnew as p
    board=p.LoadBoard(str(path))
    def xy(v):return (v.x,v.y)
    def poly(poly):
        return [[xy(poly.COutline(i).CPoint(j)) for j in range(poly.COutline(i).PointCount())]
                for i in range(poly.OutlineCount())]
    footprints=[]
    for f in board.GetFootprints():
        pads=sorted((q.GetNumber(),xy(q.GetPosition()),xy(q.GetSize()),xy(q.GetDrillSize()),
                     q.GetShape(),q.GetAttribute(),q.GetOrientationDegrees(),q.GetLayerSet().FmtHex(),q.GetNetname()) for q in f.Pads())
        footprints.append((f.GetReference(),f.GetValue(),f.GetFPID().GetLibItemName(),xy(f.GetPosition()),f.GetOrientationDegrees(),f.GetLayer(),pads))
    copper=[]
    for t in board.GetTracks():
        if isinstance(t,p.PCB_VIA):
            copper.append(('via',xy(t.GetPosition()),t.GetWidth(p.F_Cu),t.GetDrillValue(),t.GetNetname()))
        else:
            copper.append(('track',xy(t.GetStart()),xy(t.GetEnd()),t.GetWidth(),t.GetLayer(),t.GetNetname()))
    zones=sorted((z.GetNetname(),z.GetLayer(),poly(z.Outline())) for z in board.Zones())
    return {'layers':board.GetCopperLayerCount(),'footprints':sorted(footprints),'copper':sorted(copper),'zones':zones}

board_rel='electronics/rev_b/integrated/integrated.kicad_pcb'
original_board=board_signature(R/board_rel);rebuilt_board=board_signature(W/board_rel)
# Library nickname and object UUIDs are container metadata; footprint item names and all modeled pad/net geometry remain compared.
board_comparison={key:original_board[key]==rebuilt_board[key] for key in original_board}
if not all(board_comparison.values()):
 (W/'pcb-comparison-diagnostic.json').write_text(json.dumps({'original':original_board,'rebuilt':rebuilt_board},indent=2), encoding='utf-8', newline='\n')
print('Fresh routed PCB comparison',board_comparison,flush=True)
out={'scope':'Fresh source rebuild/export and routing recipe replay compared with retained native geometry; no physical design changed','passed':all(r['passed'] for r in rows) and all(board_comparison.values()),'assemblies':rows,'pcb_rebuild_comparison':board_comparison}
out['geometry_comparator']={'method':'Native OCC validity, solid counts, bounds, area, volume, and bidirectional Boolean difference; BRep serialization reported separately','bbox_tolerance_mm':1e-6,'area_tolerance_mm2':1e-3,'volume_tolerance_mm3':1e-3,'negative_controls':controls}
paths=[r['file'] for r in rows]+[
 'mechanical/rev_b/build_base.py','mechanical/rev_b/design_parameters.json',
 'mechanical/rev_b/socket_b_features.py','mechanical/rev_b/power_links.py',
 'mechanical/rev_b/export_release.py','mechanical/rev_b/artifacts_metadata.py',
 'electronics/rev_b/integrated/scripts/export_geometry.py',
 'electronics/rev_b/integrated/integrated.kicad_pcb',
 'electronics/rev_b/integrated/electrical_manifest.json',
 'electronics/rev_b/integrated/exports/component_envelopes.json',
 'electronics/rev_b/integrated/exports/remote_head_assembled.step',
 'scripts/verify_hardware_rebuild.py']
# Bind generation dependencies, including the Rev B source modules still used by the merger.
for sub in ['controller','meter','feedback','thermal','integrated']:
 for p in (R/'electronics/rev_b'/sub).rglob('*'):
  if p.is_file() and ('scripts' in p.parts or p.suffix in ['.kicad_sch','.kicad_sym','.kicad_mod','.kicad_dru','.kicad_pro']) and '.xdg' not in p.parts and 'validation' not in p.parts and p.suffix not in ['.pyc','.log']:
   paths.append(p.relative_to(R).as_posix())
paths.extend(['electronics/rev_b/'+p for p in ['controller/circuit_manifest.json','controller/carbentra.kicad_pcb','meter/circuit_manifest.json','meter/meter.kicad_pcb','feedback/pin_net_manifest.json','feedback/output_feedback.kicad_pcb','thermal/pin_net_manifest.json','thermal/thermal_controller.kicad_pcb']])
paths.extend(['electronics/rev_b/scripts/replay_routing.py','electronics/scripts/sexpr_util.py','electronics/rev_b/integrated/routing_recipe.json'])
paths.extend(['scripts/cad_equivalence.py','scripts/carbentra_pcb.py','scripts/carbentra_tools.py'])
out['input_sha256']={p:hashlib.sha256((R/p).read_bytes()).hexdigest() for p in paths}
out['tool_versions']={'FreeCAD':A.Version(),'python':sys.version}
(R/'release/hardware_geometry_rebuild.json').write_text(json.dumps(out,indent=2)+'\n', encoding='utf-8', newline='\n')
if not out['passed']:raise SystemExit(1)
