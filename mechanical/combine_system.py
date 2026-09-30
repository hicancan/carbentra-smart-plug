#!/usr/bin/python3
"""Combine the validated mechanical document and frozen electronics STEP.
Electronics source remains owned by its native KiCad project.
"""
import os,sys,json
BASE=os.path.dirname(os.path.abspath(__file__))
sys.path.extend(['/usr/lib/freecad-python3/lib',BASE])
import FreeCAD as App,Part,socket_features
pcb_path=os.path.join(BASE,'../electronics/exports/pcb_assembly.step')
d=App.openDocument(BASE+'/CarbonMirror_S16_EVT_A.FCStd')
e=d.addObject('Part::Feature','ElectronicsAssembly');e.Label='KiCad PCB + candidate package envelopes';e.Shape=Part.read(pcb_path)
e.addProperty('App::PropertyString','SourceArtifact').SourceArtifact='electronics/exports/pcb_assembly.step'
e.addProperty('App::PropertyString','ReleaseStatus').ReleaseStatus='Development; unrouted mains and qualification hold'
d.recompute()
assert e.Shape.isValid()
d.saveAs(BASE+'/CarbonMirror_S16_SystemAssembly.FCStd')
objs=[o for o in d.Objects if hasattr(o,'Shape') and not o.Shape.isNull()]
Part.export(objs,BASE+'/CarbonMirror_S16_SystemAssembly.step')
json.dump({'mechanical_bodies':54,'electronics_step_solids':len(e.Shape.Solids),'electronics_shape_valid':e.Shape.isValid(),'source':e.SourceArtifact,'status':'Combined digital assembly; does not supersede qualification holds'},open(BASE+'/system_assembly_manifest.json','w'),indent=2)
print('Combined STEP and FCStd saved; electronic solids:',len(e.Shape.Solids))
