from pathlib import Path
exec(Path(__file__).with_name('route_controller.py').read_text(encoding='utf-8').split('groups={}')[0])
S=.05;NX=1441;NY=1361;xx,yy=np.meshgrid(np.arange(NX)*S,np.arange(NY)*S,indexing='ij');D=.45;DR=.2
route('GND_ISO',(48.2,17.05),(46.5,25.8),0,1)
points=list(dict.fromkeys(xy(pd.GetPosition()) for f in b.GetFootprints() for pd in f.Pads() if pd.GetNetname()=='EN'));tree=[points.pop(0)]
while points:
 _,i,a=min((math.dist(a,z),i,a) for a in tree for i,z in enumerate(points));z=points.pop(i);route('EN',a,z);tree.append(z)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(P),b)
