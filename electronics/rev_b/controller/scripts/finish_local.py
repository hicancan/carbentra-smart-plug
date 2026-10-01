from pathlib import Path
exec(Path(__file__).with_name('route_controller.py').read_text(encoding='utf-8').split('groups={}')[0])
S=.05;NX=1441;NY=1361;xx,yy=np.meshgrid(np.arange(NX)*S,np.arange(NY)*S,indexing='ij');D=.45;DR=.2
W=.6;seg((50.1375,33),(52.475,33),'SW',0);W=.15
for a,z in zip([(52.475,33),(52,33),(52,27.05)],[(52,33),(52,27.05),(51,27.05)]):seg(a,z,'SW',0)
route('BST',(50.1375,32.05),(51,28.95));p.SaveBoard(str(P),b)
coords=[(31,1),(71,1),(71,67),(31,67),(31,59),(44,59),(44,29),(31,29)]
for layer in (p.F_Cu,p.B_Cu):
 z=p.ZONE(b);z.SetLayer(layer);z.SetNetCode(b.FindNet('GND_ISO').GetNetCode());z.SetLocalClearance(p.FromMM(.2));z.SetThermalReliefGap(p.FromMM(.25));z.SetThermalReliefSpokeWidth(p.FromMM(.3));z.SetPadConnection(p.ZONE_CONNECTION_FULL);z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS);z.SetMinThickness(p.FromMM(.15));poly=z.Outline();poly.NewOutline()
 for x,y in coords:poly.Append(p.FromMM(x),p.FromMM(y))
 b.Add(z)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(P),b)
