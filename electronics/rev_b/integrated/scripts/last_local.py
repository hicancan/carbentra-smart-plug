import route_signals as r
r.S=.05;r.NX=2001;r.NY=1701;r.xx,r.yy=r.np.meshgrid(r.np.arange(r.NX)*r.S,r.np.arange(r.NY)*r.S,indexing='ij')
r.W=2.4;r.seg((28.5,62),(32.5,62),'HOT_GND',0);r.W=.15
r.route('HOT_CS',(50.4125,59.8),(54.125,63.865),0,0);r.p.SaveBoard(str(r.P),r.b)
