from pathlib import Path
import pcbnew as p,math
R=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(R/'integrated.kicad_pcb'))
def outline(z,points):
 o=z.Outline();o.NewOutline()
 for x,y in points:o.Append(p.FromMM(x),p.FromMM(y))
# Fixed mechanical keepouts on every copper layer, including pours.
for x,y in [(6,6.5),(94,6.5),(6,78.5),(94,78.5)]:
 z=p.ZONE(b);z.SetIsRuleArea(True);ls=p.LSET()
 for l in (p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu):ls.AddLayer(l)
 z.SetLayerSet(ls);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False);z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowCopperPour(True);outline(z,[(x+3.5*math.cos(t*math.pi/32),y+3.5*math.sin(t*math.pi/32))for t in range(64)]);b.Add(z)
z=p.ZONE(b);z.SetLayer(p.In2_Cu);z.SetNetCode(b.FindNet('GND_ISO').GetNetCode());z.SetLocalClearance(p.FromMM(.16));z.SetThermalReliefGap(p.FromMM(.25));z.SetThermalReliefSpokeWidth(p.FromMM(.3));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetMinThickness(p.FromMM(.15));z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
# The entire outline stays outside the independently checked projected hot-copper domain.
outline(z,[(49,1),(99,1),(99,84),(64,84),(64,23),(49,20.5)]);b.Add(z)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(R/'integrated.kicad_pcb'),b)
