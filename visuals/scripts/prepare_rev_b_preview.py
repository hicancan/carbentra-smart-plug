from carbentra_tools import FREECAD_LIB, FONT_REGULAR, PYTHON, kicad_resource
"""Read-only native CAD snapshot for internal scene development, never a release export."""
import sys,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.extend([FREECAD_LIB,str(ROOT/'mechanical/rev_b')])
import FreeCAD as App,MeshPart
out=ROOT/'visuals/rev_b/_preview/source';mech=out/'mechanical';(mech/'meshes').mkdir(parents=True,exist_ok=True)
doc=App.openDocument(str(ROOT/'mechanical/rev_b/CARBENTRA-P16-B-base-provisional.FCStd'))
parts=[]
for o in doc.Objects:
 if not hasattr(o,'Shape') or o.Shape.isNull():continue
 s=o.Shape;b=s.BoundBox
 MeshPart.meshFromShape(Shape=s,LinearDeflection=.005 if o.Name in ('RearShell','FrontLid','RearFinish','SeamRing','LocalButton','RearmButton','StatusLightGuide') else .03,AngularDeflection=.15,Relative=False).write(str(mech/'meshes'/f'{o.Name}.stl'))
 group='housing';z=0
 if o.Name=='FrontLid':group='front';z=85
 elif o.Name in ('LocalButton','RearmButton','StatusLightGuide'):group='controls';z=85
 elif any(x in o.Name for x in ('Shutter','Pawl')):group='shutter';z=65
 elif o.Name in ('Carrier','Contact_L','Contact_N','Contact_PE','ThermalPad'):group='receptacle';z=40
 elif o.Name.startswith('Blade'):group='rear_interface';z=-25
 parts.append({'id':o.Name,'name':o.Label,'file':f'meshes/{o.Name}.stl','bbox_mm':[b.XMin,b.YMin,b.ZMin,b.XMax,b.YMax,b.ZMax],'assembly_group':group,'presentation_explode_mm':z,'explode':[0,0,z],'valid':s.isValid(),'solids':len(s.Solids)})
(mech/'parts_manifest.json').write_text(json.dumps({'units':'mm','status':'PROVISIONAL SCENE SETUP ONLY; DO NOT DELIVER','parts':parts},indent=2), encoding='utf-8', newline='\n')
shutil.copy2(ROOT/'mechanical/rev_b/design_parameters.json',mech/'design_parameters.json')
elec=out/'electronics/exports';elec.mkdir(parents=True,exist_ok=True)
shutil.copy2(ROOT/'electronics/rev_b/integrated/exports/integrated_assembly.obj',elec/'pcb_assembly.obj')
print('PROVISIONAL mesh snapshot:',len(parts),out)
