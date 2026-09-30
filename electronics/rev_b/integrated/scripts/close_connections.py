import route_signals as r
r.S=.05;r.NX=2001;r.NY=1701;r.xx,r.yy=r.np.meshgrid(r.np.arange(r.NX)*r.S,r.np.arange(r.NY)*r.S,indexing='ij')
pairs=[('HOT_GND',(51,62.05),(54.125,60.055),0,0),('HOT_GND',(51,62.05),(50.65,66.5),0,0),('HOT_SWITCHED',(7,31),(28.5,45.76),0,0)]
for n,a,z,al,zl in pairs:r.route(n,a,z,al,zl);r.p.SaveBoard(str(r.P),r.b)
