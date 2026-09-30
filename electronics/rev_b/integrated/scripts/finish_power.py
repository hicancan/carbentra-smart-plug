from pathlib import Path
import pcbnew as p
R=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(R/'integrated.kicad_pcb'))
def line(n,pts,w,layer=p.F_Cu):
 for a,z in zip(pts,pts[1:]):
  t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));t.SetEnd(p.VECTOR2I(p.FromMM(z[0]),p.FromMM(z[1])));t.SetWidth(p.FromMM(w));t.SetLayer(layer);t.SetNetCode(b.FindNet(n).GetNetCode());b.Add(t)
# Neutral keeps3mm from line-related copper even at unswitched NC pads.
line('HOT_N',[(28.5,38.14),(32,38.14),(35.5,40.5)],2.4,p.B_Cu)
line('HOT_N',[(35.5,40.5),(35.5,48)],4.8,p.B_Cu)
line('HOT_N',[(35.5,48),(35.5,50.5),(28.5,54.38)],2.4,p.B_Cu)
# Feed before the1A auxiliary fuse is sized as a protected16A branch candidate, not an AFE trace.
line('HOT_GND',[(28.5,62),(28.5,71),(21,76),(17.5,81.6)],2.4,p.B_Cu)
line('HOT_GND',[(17.5,81.6),(16.9,83.4)],1.8,p.B_Cu)
p.SaveBoard(str(R/'integrated.kicad_pcb'),b)
