import route_signals as r
p=r.p
for f in r.b.GetFootprints():
 if f.GetReference()=='U202':
  for q in f.Pads():
   if int(q.GetNumber())>8:continue
   a=r.xy(q.GetPosition());z=(65.8,a[1]);n=q.GetNetname();r.seg(a,z,n,0);v=p.PCB_VIA(r.b);v.SetPosition(p.VECTOR2I(p.FromMM(z[0]),p.FromMM(z[1])));v.SetWidth(p.F_Cu,p.FromMM(.45));v.SetDrill(p.FromMM(.2));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(q.GetNetCode());r.b.Add(v)
p.SaveBoard(str(r.P),r.b)
for n,a,z in [('SPI_MISO',(71.25,21.5),(65.8,62.595)),('SPI_MOSI',(71.25,23),(65.8,65.135)),('SPI_CS',(71.25,24.5),(65.8,63.865)),('SPI_SCLK',(71.25,20),(65.8,66.405))]:
 if not r.b.FindNet(n):continue
 r.route(n,a,z,0,3);p.SaveBoard(str(r.P),r.b)
