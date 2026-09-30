from pathlib import Path
import pcbnew as p
R=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(R/'carbentra.kicad_pcb'))
def line(n,pts,w,layer=p.F_Cu):
 for a,z in zip(pts,pts[1:]):
  t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));t.SetEnd(p.VECTOR2I(p.FromMM(z[0]),p.FromMM(z[1])));t.SetWidth(p.FromMM(w));t.SetLayer(layer);t.SetNetCode(b.FindNet(n).GetNetCode());b.Add(t)
# Small reduction of candidate terminal copper land (not drill), preserving 0.60mm nominal annulus.
for fp in b.GetFootprints():
 if fp.GetReference() in ('J1','J2','J5'):
  for pad in fp.Pads():pad.SetSize(p.VECTOR2I(p.FromMM(2.5),p.FromMM(2.5)))
line('L_FUSED',[(10,44.8),(10,40.8)],2.4)
line('L_FUSED',[(10,40.8),(10,37.5),(23,37.5)],4.8)
line('L_FUSED',[(23,37.5),(31.7,37.5),(31.7,43),(31.7,50.5)],2.4)
line('L_FUSED',[(21,37.5),(31.7,37.5),(31.7,50.5)],2.4,p.B_Cu)
for x in (21,22,23):
 v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(37.5)));v.SetWidth(p.F_Cu,p.FromMM(.8));v.SetDrill(p.FromMM(.4));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(b.FindNet('L_FUSED').GetNetCode());b.Add(v)
line('L_SWITCHED',[(26.66,43),(26.66,50.5),(24,53.5)],2.4)
line('L_SWITCHED',[(26.66,43),(26.66,50.5)],2.4,p.B_Cu)
line('L_SWITCHED',[(24,53.5),(14,53.5),(14,56)],4.8)
line('L_SWITCHED',[(14,56),(14,60)],2.4)
line('L_NC_UNUSED',[(36.74,43),(36.74,50.5)],1.2)
line('N',[(15.08,44.8),(15.08,49.5)],2.4,p.B_Cu)
line('N',[(15.08,49.5),(19.08,52),(19.08,55.5)],4.8,p.B_Cu)
line('N',[(19.08,55.5),(19.08,60)],2.4,p.B_Cu)
# Auxiliary supply current only on these branches, not the16A socket neutral path.
line('N',[(15.08,44.8),(15.08,38),(9,38),(9,23.2),(4.6,23.2)],.4,p.B_Cu)
line('N',[(4.6,23.2),(.75,23.2),(.75,1.5),(23.08,1.5),(23.08,5.5)],.4,p.B_Cu)
line('L_AUX_FUSED',[(18,5.5),(18,10),(13,10),(13,28),(4.6,28),(4.6,33.95)],.6)
p.SaveBoard(str(R/'carbentra.kicad_pcb'),b)
