from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'))
from sexpr_util import parse,ser,ch
R=Path(__file__).resolve().parents[1];P=R/'integrated.kicad_pcb';s=parse(P.read_text(encoding='utf-8'));stack=parse('''(stackup
(layer "F.SilkS" (type "Top Silk Screen")) (layer "F.Paste" (type "Top Solder Paste")) (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
(layer "F.Cu" (type "copper") (thickness 0.07))
(layer "dielectric 1" (type "prepreg") (thickness 0.175) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
(layer "In1.Cu" (type "copper") (thickness 0.035))
(layer "dielectric 2" (type "core") (thickness 1.02) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
(layer "In2.Cu" (type "copper") (thickness 0.035))
(layer "dielectric 3" (type "prepreg") (thickness 0.175) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02))
(layer "B.Cu" (type "copper") (thickness 0.07)) (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
(layer "B.Paste" (type "Bottom Solder Paste")) (layer "B.SilkS" (type "Bottom Silk Screen")) (copper_finish "ENIG") (dielectric_constraints no))''')
setup=ch(s,'setup');setup[:]=[v for v in setup if not(isinstance(v,list) and v[0]=='stackup')];setup.append(stack);P.write_text(ser(s), encoding='utf-8', newline='\n')
