"""Conservative projected copper separation, independent of shared Cu layer.
Pads use their bounding rectangle (conservative for round/oblong pads). Tracks are capsules.
NC pads are included according to the physical isolator/relay pin domain.
"""
from pathlib import Path
import sys,json,math,os,hashlib
import pcbnew as p
sys.path.insert(0,str(Path(__file__).parent));from route_signals import domain,xy
R=Path(__file__).resolve().parents[1];board_path=Path(os.environ.get('CARBENTRA_AUDIT_BOARD',str(R/'integrated.kicad_pcb')));b=p.LoadBoard(str(board_path))
def pdist(q,a,z):
 dx=z[0]-a[0];dy=z[1]-a[1];v=dx*dx+dy*dy;t=max(0,min(1,((q[0]-a[0])*dx+(q[1]-a[1])*dy)/(v or 1)));return math.hypot(q[0]-a[0]-t*dx,q[1]-a[1]-t*dy)
def orient(a,z,q):return (z[0]-a[0])*(q[1]-a[1])-(z[1]-a[1])*(q[0]-a[0])
def sdist(a,z,c,d):
 if max(min(a[0],z[0]),min(c[0],d[0]))<=min(max(a[0],z[0]),max(c[0],d[0])) and max(min(a[1],z[1]),min(c[1],d[1]))<=min(max(a[1],z[1]),max(c[1],d[1])) and orient(a,z,c)*orient(a,z,d)<=0 and orient(c,d,a)*orient(c,d,z)<=0:return 0
 return min(pdist(a,c,d),pdist(z,c,d),pdist(c,a,z),pdist(d,a,z))
def item(label,hot,points,r=0):
 xs=[v[0]for v in points];ys=[v[1]for v in points];return dict(label=label,hot=hot,points=points,r=r,bb=(min(xs)-r,min(ys)-r,max(xs)+r,max(ys)+r))
items=[]
for f in b.GetFootprints():
 for q in f.Pads():
  if q.GetAttribute()==p.PAD_ATTRIB_NPTH:continue
  if not any(q.IsOnLayer(l) for l in (p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu)):continue
  bb=q.GetBoundingBox();x1,y1,x2,y2=map(p.ToMM,(bb.GetLeft(),bb.GetTop(),bb.GetRight(),bb.GetBottom()))
  pts=[(x1,y1),(x2,y1),(x2,y2),(x1,y2),(x1,y1)];rad=0
  if q.GetShape() in (p.PAD_SHAPE_CIRCLE,p.PAD_SHAPE_OVAL):
   cx,cy=xy(q.GetPosition());w,h=p.ToMM(q.GetSize().x),p.ToMM(q.GetSize().y);angle=math.radians(-q.GetOrientationDegrees());rad=min(w,h)/2;dx=max(0,(w-h)/2);dy=max(0,(h-w)/2);rx=dx*math.cos(angle)-dy*math.sin(angle);ry=dx*math.sin(angle)+dy*math.cos(angle);pts=[(cx-rx,cy-ry),(cx+rx,cy+ry)]
  items.append(item(f.GetReference()+'.'+q.GetNumber(),domain(f.GetReference(),q.GetNumber(),q.GetNetname()),pts,rad))
for i,t in enumerate(b.GetTracks()):
 if isinstance(t,p.PCB_VIA):a=z=xy(t.GetPosition());w=p.ToMM(t.GetWidth(p.F_Cu))/2
 else:a,z=xy(t.GetStart()),xy(t.GetEnd());w=p.ToMM(t.GetWidth())/2
 items.append(item(f'{t.GetNetname()}:copper{i}',t.GetNetname().startswith('HOT_'),[a,z],w))
# Treat each copper-zone outline as fully filled for a conservative projected audit.
# Holes/cutouts only remove copper, so ignoring them cannot improve a measured gap.
for zi,z in enumerate(b.Zones()):
 if z.GetIsRuleArea():continue
 o=z.Outline()
 for k in range(o.OutlineCount()):
  c=o.COutline(k);pts=[xy(c.CPoint(j))for j in range(c.PointCount())];pts.append(pts[0]);items.append(item('ZONE:'+z.GetNetname()+':'+str(zi),z.GetNetname().startswith('HOT_'),pts))
def contains(q,poly):
 inside=False
 for a,z in zip(poly,poly[1:]):
  if (a[1]>q[1])!=(z[1]>q[1]) and q[0]<(z[0]-a[0])*(q[1]-a[1])/(z[1]-a[1])+a[0]:inside=not inside
 return inside
hot=[i for i in items if i['hot']];cold=[i for i in items if not i['hot']];best=(1e9,None,None);bad=[];margin_bad=[];body_best=(1e9,None,None)
for a in hot:
 for z in cold:
  ax,ay,bx,by=a['bb'];cx,cy,dx,dy=z['bb'];lower=math.hypot(max(ax-dx,cx-bx,0),max(ay-dy,cy-by,0))
  if lower>max(8.401,best[0]):continue
  dist=min(sdist(v,w,q,r) for v,w in zip(a['points'],a['points'][1:]) for q,r in zip(z['points'],z['points'][1:]))-a['r']-z['r']
  if (a['label'].startswith('ZONE:') and any(contains(q,a['points'])for q in z['points'])) or (z['label'].startswith('ZONE:') and any(contains(q,z['points'])for q in a['points'])):dist=0
  if dist<best[0]:best=(dist,a['label'],z['label'])
  if ':copper' not in a['label'] and ':copper' not in z['label'] and not a['label'].startswith('ZONE:') and not z['label'].startswith('ZONE:') and dist<body_best[0]:body_best=(dist,a['label'],z['label'])
  if dist<8.399 and (':copper' in a['label'] or ':copper' in z['label'] or a['label'].startswith('ZONE:') or z['label'].startswith('ZONE:')):margin_bad.append({'distance_mm':dist,'hot':a['label'],'isolated':z['label']})
  if dist<7.999:bad.append({'distance_mm':dist,'hot':a['label'],'isolated':z['label']})
result={'board_sha256':hashlib.sha256(board_path.read_bytes()).hexdigest(),'basis':'all-layer XY projection, conservative pad bounding rectangles; vias/NC pins included; copper-zone outlines included as completely filled conservative regions','copper_items':len(items),'minimum_mm':best[0],'minimum_pair':best[1:],'component_only_minimum':body_best,'routing_margin_below_8p4':margin_bad,'violations_below_8mm':bad,'pass':not bad}
Path(os.environ.get('CARBENTRA_AUDIT_OUTPUT',str(R/'validation/projected_isolation.json'))).write_text(json.dumps(result,indent=2), encoding='utf-8', newline='\n');print(json.dumps(result,indent=2))
