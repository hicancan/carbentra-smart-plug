#!/usr/bin/python3
"""Targeted LV airwire closure on a duplicate board. DRC remains authoritative."""
from pathlib import Path
import pcbnew as p,numpy as np,heapq,math,json,shutil,sys,re
R=Path(__file__).resolve().parents[1];P=R/'candidate_lv.kicad_pcb'
if '--reset' in sys.argv or not P.exists():
 for ext in ('kicad_pcb','kicad_pro','kicad_dru'):shutil.copy2(R/('carbentra.'+ext),R/('candidate_lv.'+ext))
b=p.LoadBoard(str(P)); S=.1;W=.15;D=.5;DR=.3;C=.155;NX=731;NY=691
xx,yy=np.meshgrid(np.arange(NX)*S,np.arange(NY)*S,indexing='ij');mains=('L_FUSED','L_AUX_FUSED','L_SWITCHED','N','L_NC_UNUSED')
def xy(q):return(p.ToMM(q.x),p.ToMM(q.y))
def seg(a,z,n,l):
 if math.dist(a,z)<.00001:return
 t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(*[p.FromMM(x) for x in a]));t.SetEnd(p.VECTOR2I(*[p.FromMM(x) for x in z]));t.SetWidth(p.FromMM(W));t.SetLayer([p.F_Cu,p.B_Cu][l]);t.SetNetCode(b.FindNet(n).GetNetCode());b.Add(t)
def obs(n,radius):
 arr=np.zeros((2,NX,NY),dtype=bool);arr[:,:,:]=((xx<31)|(xx>71)|(yy<1)|(yy>67))
 def rect(x1,y1,x2,y2,l,margin):
  # Rounded expansion around the copper bounding rectangle.
  ix1=max(0,int((x1-margin)/S)-1);ix2=min(NX,int((x2+margin)/S)+2);iy1=max(0,int((y1-margin)/S)-1);iy2=min(NY,int((y2+margin)/S)+2)
  x=xx[ix1:ix2,iy1:iy2];y=yy[ix1:ix2,iy1:iy2]
  mask=np.maximum(np.maximum(x1-x,x-x2),0)**2+np.maximum(np.maximum(y1-y,y-y2),0)**2<margin*margin
  for la in l:arr[la,ix1:ix2,iy1:iy2]|=mask
 def line(a,z,l,margin):
  x1=min(a[0],z[0]);x2=max(a[0],z[0]);y1=min(a[1],z[1]);y2=max(a[1],z[1]);ix1=max(0,int((x1-margin)/S)-1);ix2=min(NX,int((x2+margin)/S)+2);iy1=max(0,int((y1-margin)/S)-1);iy2=min(NY,int((y2+margin)/S)+2)
  x=xx[ix1:ix2,iy1:iy2];y=yy[ix1:ix2,iy1:iy2];dx=z[0]-a[0];dy=z[1]-a[1];q=dx*dx+dy*dy
  t=np.clip(((x-a[0])*dx+(y-a[1])*dy)/(q or 1),0,1);mask=(x-a[0]-t*dx)**2+(y-a[1]-t*dy)**2<margin*margin
  for la in l:arr[la,ix1:ix2,iy1:iy2]|=mask
 for f in b.GetFootprints():
  for pad in f.Pads():
   at=xy(pad.GetPosition());hole=max(p.ToMM(pad.GetDrillSize().x),p.ToMM(pad.GetDrillSize().y))/2
   if pad.GetNetname()!=n:
    bb=pad.GetBoundingBox();layers=[i for i,la in enumerate((p.F_Cu,p.B_Cu)) if pad.IsOnLayer(la)];clear=8.01 if pad.GetNetname() in mains else C
    rect(p.ToMM(bb.GetLeft()),p.ToMM(bb.GetTop()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom()),layers,clear+radius+.011)
   if hole>0:
    # Trace must avoid foreign hole; a via must avoid every existing drill.
    if radius>.1:line(at,at,[0,1],hole+DR/2+.251)
    elif pad.GetNetname()!=n:line(at,at,[0,1],hole+radius+.251)
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):
   at=xy(t.GetPosition())
   if t.GetNetname()!=n:line(at,at,[0,1],p.ToMM(t.GetWidth(p.F_Cu))/2+radius+C+.011)
   if radius>.1:line(at,at,[0,1],p.ToMM(t.GetDrillValue())/2+DR/2+.251)
  elif t.GetNetname()!=n:line(xy(t.GetStart()),xy(t.GetEnd()),[0 if t.GetLayer()==p.F_Cu else 1],p.ToMM(t.GetWidth())/2+radius+C+.011)
 return arr

def route(n,a,z,al=0,zl=0):
 block=obs(n,W/2);vb=obs(n,D/2);via=vb[0]|vb[1];start=round(a[0]/S),round(a[1]/S),al;end=round(z[0]/S),round(z[1]/S),zl
 # Endpoints are on their own copper. Grid rounding lies inside the source item.
 for x,y,l in (start,end):block[l,x,y]=False
 q=[(0,0,start)];dist={start:0};prev={};found=False
 while q:
  _,g,cur=heapq.heappop(q)
  if dist.get(cur)!=g:continue
  if cur==end:found=True;break
  x,y,l=cur
  for dx,dy in ((1,0),(-1,0),(0,1),(0,-1),(0,0)):
   nx=x+dx;ny=y+dy;nl=1-l if dx==dy==0 else l
   if not(0<nx<NX-1 and 0<ny<NY-1) or block[nl,nx,ny]:continue
   if nl!=l and via[nx,ny]:continue
   st=(nx,ny,nl);ng=g+(18 if nl!=l else 1)
   if ng<dist.get(st,1e99):dist[st]=ng;prev[st]=cur;h=abs(nx-end[0])+abs(ny-end[1])+(nl!=end[2])*18;heapq.heappush(q,(ng+h,ng,st))
 if not found:print('FAILED',n,a,z,'states',len(dist),flush=True);return False
 path=[end]
 while path[-1]!=start:path.append(prev[path[-1]])
 path.reverse();seg(a,(start[0]*S,start[1]*S),n,al);last=path[0];direction=None
 for i,cur in enumerate(path[1:],1):
  pr=path[i-1];d=tuple(cur[j]-pr[j] for j in range(3))
  if d[2]:
   seg((last[0]*S,last[1]*S),(pr[0]*S,pr[1]*S),n,pr[2]);v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(p.FromMM(cur[0]*S),p.FromMM(cur[1]*S)));v.SetWidth(p.F_Cu,p.FromMM(D));v.SetDrill(p.FromMM(DR));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(b.FindNet(n).GetNetCode());b.Add(v);last=cur;direction=None
  elif direction is not None and d!=direction:seg((last[0]*S,last[1]*S),(pr[0]*S,pr[1]*S),n,pr[2]);last=pr;direction=d
  else:direction=d
 seg((last[0]*S,last[1]*S),(end[0]*S,end[1]*S),n,zl);seg((end[0]*S,end[1]*S),z,n,zl);print('ROUTED',n,a,z,'steps',len(path),flush=True);return True
pairs=[
('GATE',(63,44.825),(65,41.175),0,0),('GATE',(58.0625,44.05),(63,44.825),0,0),
('+3V3_ISO',(61,53.875),(58.7125,55),1,0),
('+3V3_ISO',(55.5,31),(46.8625,32.05),0,0),
('+3V3_ISO',(46.8625,32.05),(46.175,22),0,0),
('+3V3_ISO',(61,50.825),(68.125,36),0,0),
('+5V_ISO',(46.875,34),(52,40),0,0),
('BOOT8',(50.25,20),(69.825,31),0,0),
('BOOT9',(69.825,27),(50.25,21.5),0,0),
('BOOT9',(53.62,62),(69.825,27),1,0),
('BUTTON',(60.175,61),(67.75,18.5),0,0),
('SPI_SCLK',(50.25,14),(69,41.08),0,1),
('GND_ISO',(47,17.05),(40.5,15.25),0,0)]
if '--pairs' in sys.argv:pairs=json.loads(Path(sys.argv[sys.argv.index('--pairs')+1]).read_text(encoding='utf-8'))
if __name__=='__main__':
 for pair in pairs:
  route(*pair);p.SaveBoard(str(P),b)
 p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(P),b)
