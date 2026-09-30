import sys,json,os
BASE=os.path.dirname(os.path.abspath(__file__))
sys.path.extend(['/usr/lib/freecad-python3/lib',BASE])
import FreeCAD as App,Part,socket_features
b=BASE+'/'
d=App.openDocument(b+'CarbonMirror_S16_SystemAssembly.FCStd');e=d.ElectronicsAssembly.Shape
out=[]
for o in d.Objects:
 if not hasattr(o,'PartKind'):continue
 vol=e.common(o.Shape).Volume
 if vol>1e-5:out.append({'part':o.Name,'volume_mm3':vol,'intended_terminal_entry':o.Name in ['WireCore_L_IN_POST','WireCore_N_IN','WireCore_L_OUT','WireCore_N_OUT','WireCore_AUX_L_OUT','WireCore_AUX_N']})
json.dump({'electronic_solids':len(e.Solids),'intersections':out},open(b+'system_fit_validation.json','w'),indent=2)
print(json.dumps(out,indent=2))
