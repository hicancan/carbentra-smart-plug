from pathlib import Path
exec(Path(__file__).with_name('route_meter.py').read_text(encoding='utf-8').split('# Load force copper')[0])
S=.05;NX=1501;NY=901;xx,yy=np.meshgrid(np.arange(NX)*S,np.arange(NY)*S,indexing='ij');D=.45;DR=.2
route('ISO_GND',(60.875,23.555),(63,21.8),0,1);p.SaveBoard(str(P),b)
