from pathlib import Path
exec(Path(__file__).with_name('route_meter.py').read_text().split('# Load force copper')[0])
S=.05;NX=1501;NY=901;xx,yy=np.meshgrid(np.arange(NX)*S,np.arange(NY)*S,indexing='ij')
D=.45;DR=.2
pairs=[('HOT_CS',(39.6,23.375),(45.9,29.5),0,1),('HOT_VP',(39.6,28.575),(44,13.9),0,0),('HOT_XIN',(39.6,24.675),(33,35.95),0,0),('HOT_XOUT',(39.6,24.025),(36,35.95),0,0),('ISO_3V3',(60.875,24.825),(62.4,28.9),0,0),('ISO_GND',(60.875,23.555),(63,21),0,0),('ISO_GND',(60.875,31.175),(65,21.8),0,1)]
for args in pairs:
 route(*args);p.SaveBoard(str(P),b)
