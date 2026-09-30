from pathlib import Path
exec(Path(__file__).with_name('route_controller.py').read_text().split('groups={}')[0])
S=.05;NX=1441;NY=1361;xx,yy=np.meshgrid(np.arange(NX)*S,np.arange(NY)*S,indexing='ij');D=.45;DR=.2
for net in ('SPI_CS','SPI_SCLK'):
 pts=[xy(pd.GetPosition()) for f in b.GetFootprints() for pd in f.Pads() if pd.GetNetname()==net]
 route(net,pts[0],pts[1]);p.SaveBoard(str(P),b)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(P),b)
