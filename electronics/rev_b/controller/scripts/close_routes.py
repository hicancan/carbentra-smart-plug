from pathlib import Path
import re
exec(Path(__file__).with_name('route_controller.py').read_text().split('groups={}')[0])
S=.05;NX=1441;NY=1361;xx,yy=np.meshgrid(np.arange(NX)*S,np.arange(NY)*S,indexing='ij');D=.45;DR=.2
report=(R/'validation/drc.rpt').read_text();pairs=[]
for block in report.split('[unconnected_items]:')[1:]:
 lines=[l for l in block.splitlines() if '@(' in l][:2]
 if len(lines)<2:continue
 net=re.search(r'\[([^\]]+)\]',lines[0]).group(1);pts=[]
 for l in lines:
  m=re.search(r'@\(([\d.-]+) mm, ([\d.-]+) mm\)',l);pts.append(((float(m[1]),float(m[2])),1 if ' on B.Cu' in l else 0))
 if net not in mains:pairs.append((net,pts[0][0],pts[1][0],pts[0][1],pts[1][1]))
for args in pairs:
 route(*args);p.SaveBoard(str(P),b)
