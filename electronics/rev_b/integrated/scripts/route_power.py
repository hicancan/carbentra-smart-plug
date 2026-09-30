from pathlib import Path
import pcbnew as p
R=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(R/'integrated.kicad_pcb'))
def line(n,pts,w,layer=p.F_Cu):
 for a,z in zip(pts,pts[1:]):
  t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));t.SetEnd(p.VECTOR2I(p.FromMM(z[0]),p.FromMM(z[1])));t.SetWidth(p.FromMM(w));t.SetLayer(layer);t.SetNetCode(b.FindNet(n).GetNetCode());b.Add(t)
def via(n,x,y):
 v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(p.FromMM(x),p.FromMM(y)));v.SetWidth(p.F_Cu,p.FromMM(.8));v.SetDrill(p.FromMM(.4));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(b.FindNet(n).GetNetCode());b.Add(v)
# Candidate load force copper, not a temperature-rise or short-circuit approval.
line('HOT_GND',[(28.5,62),(32.5,62)],2.4)
line('HOT_GND',[(32.5,62),(35,59.975),(39.15,59.975)],4.8)
line('HOT_LOAD',[(39.15,68.025),(39.15,64),(49.2,64),(49.2,59)],4.8,p.B_Cu)
line('HOT_LOAD',[(49.2,59),(49.2,55),(49.2,47.5)],2.4,p.B_Cu)
for x in (37.5,38.5,39.5,40.5):
 for y in (67.5,68.5):via('HOT_LOAD',x,y)
line('HOT_SWITCHED',[(44.16,55),(44.16,47.5)],2.4)
line('HOT_SWITCHED',[(44.16,47.5),(39,45.76),(32.5,45.76)],4.8)
line('HOT_SWITCHED',[(32.5,45.76),(28.5,45.76)],2.4)
line('HOT_N',[(28.5,38.14),(24,38.14)],2.4,p.B_Cu)
line('HOT_N',[(24,38.14),(24,54.38)],4.8,p.B_Cu)
line('HOT_N',[(24,54.38),(28.5,54.38)],2.4,p.B_Cu)
# Compact buck commutation and bootstrap loops; power/ground connections follow.
line('SW',[(66.138,36),(69.475,36)],.65)
line('SW',[(68.15,36),(68.15,31.05),(67,31.05)],.35)
line('BST',[(66.138,35.05),(67,34.2),(67,32.95)],.2)
line('+3V3_ISO',[(72.525,36),(73.8,36.95),(76,36.95),(80,36.95)],.65)
p.SaveBoard(str(R/'integrated.kicad_pcb'),b)
