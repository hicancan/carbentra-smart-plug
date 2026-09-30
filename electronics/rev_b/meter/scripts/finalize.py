from pathlib import Path
import pcbnew as p,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'))
from sexpr_util import parse,ser,ch
R=Path(__file__).resolve().parents[1];P=R/'meter.kicad_pcb';b=p.LoadBoard(str(P))
# Ground pours deliberately omit the neutral/high-voltage divider corridor. They cannot bridge the isolation strip.
for net,coords in [('HOT_GND',[(1,18),(43,18),(43,1),(51.95,1),(51.95,44),(1,44)]),('ISO_GND',[(60.05,1),(74,1),(74,44),(60.05,44)])]:
 zone=p.ZONE(b);zone.SetLayer(p.B_Cu);zone.SetNetCode(b.FindNet(net).GetNetCode());zone.SetLocalClearance(p.FromMM(.2));zone.SetThermalReliefGap(p.FromMM(.25));zone.SetThermalReliefSpokeWidth(p.FromMM(.3));zone.SetPadConnection(p.ZONE_CONNECTION_FULL);zone.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS);zone.SetMinThickness(p.FromMM(.15));poly=zone.Outline();poly.NewOutline()
 for x,y in coords:poly.Append(p.FromMM(x),p.FromMM(y))
 b.Add(zone)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(P),b)
s=parse(P.read_text());setup=ch(s,'setup');stack=parse('''(stackup (layer "F.SilkS" (type "Top Silk Screen")) (layer "F.Paste" (type "Top Solder Paste")) (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01)) (layer "F.Cu" (type "copper") (thickness 0.07)) (layer "dielectric 1" (type "core") (thickness 1.44) (material "FR4") (epsilon_r 4.5) (loss_tangent 0.02)) (layer "B.Cu" (type "copper") (thickness 0.07)) (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01)) (layer "B.Paste" (type "Bottom Solder Paste")) (layer "B.SilkS" (type "Bottom Silk Screen")) (copper_finish "ENIG") (dielectric_constraints no))''');setup[:]=[v for v in setup if not(isinstance(v,list) and v[0]=='stackup')];setup.append(stack);P.write_text(ser(s))
