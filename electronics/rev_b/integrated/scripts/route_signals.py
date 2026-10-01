#!/usr/bin/python3
"""Targeted LV airwire closure on a duplicate board. DRC remains authoritative."""
from pathlib import Path
import pcbnew as p,numpy as np,heapq,math,json,shutil,sys,re
R=Path(__file__).resolve().parents[1];P=R/'integrated.kicad_pcb'
b=p.LoadBoard(str(P)); S=.1;W=.15;D=.45;DR=.2;C=.16;NX=1001;NY=851;LAYERS=[p.F_Cu,p.In1_Cu,p.In2_Cu,p.B_Cu]
xx,yy=np.meshgrid(np.arange(NX)*S,np.arange(NY)*S,indexing='ij');mains=()
def xy(q):return(p.ToMM(q.x),p.ToMM(q.y))
def seg(a,z,n,l):
 if math.dist(a,z)<.00001:return
 t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(*[p.FromMM(x) for x in a]));t.SetEnd(p.VECTOR2I(*[p.FromMM(x) for x in z]));t.SetWidth(p.FromMM(W));t.SetLayer(LAYERS[l]);t.SetNetCode(b.FindNet(n).GetNetCode());b.Add(t)
def domain(ref,num,n):
 if n:return n.startswith('HOT_')
 if ref=='U201':return True
 if ref in ('U202','PS201'):return int(num or 0)>=9
 if ref=='U301':return int(num or 0)<=4
 if ref=='K101':return not num.startswith('A')
 return False
def netclear(a,z):
 if a.startswith('HOT_')!=z.startswith('HOT_'):return 8.41
 other=z if a=='HOT_N' else a
 if 'HOT_N' in (a,z) and other.startswith('HOT_') and not other.startswith('HOT_DIV') and not other.startswith('HOT_FB_'):return 3.01
 if a!=z and ((a in ('HOT_SWITCHED','HOT_NC') and not z.startswith('HOT_FB_')) or (z in ('HOT_SWITCHED','HOT_NC') and not a.startswith('HOT_FB_'))):return 2.51
 if (a in ('HOT_DIV1','HOT_DIV2','HOT_DIV3') or z in ('HOT_DIV1','HOT_DIV2','HOT_DIV3')) and a!=z:return 1.01
 return C
def obs(n,radius):
 arr=np.zeros((4,NX,NY),dtype=bool);# Rounded board inset plus through-routing notches, conservative square notch allowance.
 arr[:,:,:]=((xx<.6)|(xx>99.4)|(yy<.6)|(yy>84.4))
 for cx,cy,cond in [(10,10,(xx<10)&(yy<10)),(90,10,(xx>90)&(yy<10)),(10,75,(xx<10)&(yy>75)),(90,75,(xx>90)&(yy>75))]:arr|=(cond&((xx-cx)**2+(yy-cy)**2>9.4**2))[None,:,:]
 arr|=(((xx<12.6)&(yy>49.9)&(yy<65.1))|((xx>93.4)&(yy>19.9)&(yy<31.1)))[None,:,:]
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
    bb=pad.GetBoundingBox();layers=[i for i,la in enumerate(LAYERS) if pad.IsOnLayer(la)]
    foreign_hot=domain(f.GetReference(),pad.GetNumber(),pad.GetNetname())
    cross=(foreign_hot!=n.startswith('HOT_')) and bool(pad.GetNetname() or f.GetReference() in ('U201','U202','PS201','U301','K101'))
    clear=8.41 if cross else (3.01 if ('HOT_N' in (n,pad.GetNetname()) and n!=pad.GetNetname() and (pad.GetNetname() if n=='HOT_N' else n).startswith('HOT_') and not (pad.GetNetname() if n=='HOT_N' else n).startswith('HOT_DIV') and not (pad.GetNetname() if n=='HOT_N' else n).startswith('HOT_FB_')) else C)
    if cross:layers=list(range(4))
    if not cross and pad.GetNetname():clear=netclear(n,pad.GetNetname())
    rect(p.ToMM(bb.GetLeft()),p.ToMM(bb.GetTop()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom()),layers,clear+radius+.011)
   if f.GetReference().startswith('H'):line(at,at,list(range(4)),3.5+radius)
   if hole>0:
    # Trace must avoid foreign hole; a via must avoid every existing drill.
    if radius>.1:line(at,at,list(range(4)),hole+DR/2+.251)
    elif pad.GetNetname()!=n:line(at,at,list(range(4)),hole+radius+.251)
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA):
   at=xy(t.GetPosition())
   if t.GetNetname()!=n:line(at,at,list(range(4)),p.ToMM(t.GetWidth(p.F_Cu))/2+radius+netclear(n,t.GetNetname())+.011)
   if radius>.1:line(at,at,list(range(4)),p.ToMM(t.GetDrillValue())/2+DR/2+.251)
  elif t.GetNetname()!=n:line(xy(t.GetStart()),xy(t.GetEnd()),list(range(4)) if n.startswith('HOT_')!=t.GetNetname().startswith('HOT_') else [LAYERS.index(t.GetLayer())],p.ToMM(t.GetWidth())/2+radius+netclear(n,t.GetNetname())+.011)
 return arr

def route(n,a,z,al=0,zl=0):
 block=obs(n,W/2);vb=obs(n,D/2);via=np.any(vb,axis=0);start=round(a[0]/S),round(a[1]/S),al;end=round(z[0]/S),round(z[1]/S),zl
 # Endpoints are on their own copper. Grid rounding lies inside the source item.
 for x,y,l in (start,end):block[l,x,y]=False
 q=[(0,0,start)];dist={start:0};prev={};found=False
 while q:
  _,g,cur=heapq.heappop(q)
  if dist.get(cur)!=g:continue
  if cur==end:found=True;break
  x,y,l=cur
  for dx,dy,nl in [(1,0,l),(-1,0,l),(0,1,l),(0,-1,l)]+[(0,0,k) for k in range(4) if k!=l]:
   nx=x+dx;ny=y+dy
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


if __name__=='__main__':
 groups={}
 for f in b.GetFootprints():
  for pd in f.Pads():
   n=pd.GetNetname()
   if n:groups.setdefault(n,[]).append((xy(pd.GetPosition()),0 if pd.IsOnLayer(p.F_Cu) else 3))
 selected=sys.argv[1].split(',') if len(sys.argv)>1 else None
 results=[]
 excluded={'HOT_GND','HOT_N','HOT_LOAD','HOT_SWITCHED','SW','BST','HOT_XIN','HOT_SENSE_UP','HOT_SENSE_DOWN','HOT_I1P','HOT_I1N'}
 for n,points in sorted(groups.items(),key=lambda kv:(kv[0] in ('HOT_GND','GND_ISO','HOT_3V3','+3V3_ISO','+5V_ISO'),len(kv[1]))):
  if (selected and n not in selected) or (not selected and n in excluded):continue
  points=list(dict.fromkeys(points));tree=[points.pop(0)]
  while points:
   d,i,source=min((math.dist(a[0],z[0]),i,a) for a in tree for i,z in enumerate(points));target=points.pop(i)
   ok=route(n,source[0],target[0],source[1],target[1]);results.append(dict(net=n,a=source,b=target,routed=ok));tree.append(target);p.SaveBoard(str(P),b)
 (R/'validation/routing.json').write_text(json.dumps(results,indent=2), encoding='utf-8', newline='\n')
