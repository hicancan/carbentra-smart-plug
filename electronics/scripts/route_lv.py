#!/usr/bin/python3
"""Deterministic grid route experiment for isolated LV nets only, subject to KiCad DRC."""
import pcbnew as p, math,heapq,json,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(R/'carbonmirror.kicad_pcb'))
S=.125; CLEAR=.16; WIDTH=.15;PADM=CLEAR+WIDTH/2+.04
pads=[];groups={};holes=[];madevias=set()
for f in b.GetFootprints():
 for pad in f.Pads():
  if pad.GetNumber()=='':continue
  bb=pad.GetBoundingBox();n=pad.GetNetname();xy=(p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y))
  layers=[0,1] if pad.GetAttribute() in (p.PAD_ATTRIB_PTH,p.PAD_ATTRIB_NPTH) else [0]
  r=(p.ToMM(bb.GetLeft()),p.ToMM(bb.GetTop()),p.ToMM(bb.GetRight()),p.ToMM(bb.GetBottom()))
  pads.append((n,r,layers));
  if len(layers)==2:holes.append((xy[0],xy[1],p.ToMM(pad.GetDrillSize().x)/2))
  if n and n not in ('L_FUSED','L_AUX_FUSED','L_SWITCHED','L_NC_UNUSED','N'):groups.setdefault(n,[]).append(xy)
# simplify duplicates/in-footprint overlapping exposed-ground pads into one representative plus tracks later
obstacles={0:[],1:[]};trackobs={0:[],1:[]};routes=[]
if len(sys.argv)>1:
 selected=set(sys.argv[1].split(','));groups={n:v for n,v in groups.items() if n in selected}
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):
  pos=t.GetPosition();x=p.ToMM(pos.x);y=p.ToMM(pos.y)
  for la in(0,1):trackobs[la].append((t.GetNetname(),(x-.3,y-.3,x+.3,y+.3)))
 else:
  a=t.GetStart();z=t.GetEnd();la=0 if t.GetLayer()==p.F_Cu else 1
  trackobs[la].append((t.GetNetname(),(min(p.ToMM(a.x),p.ToMM(z.x)),min(p.ToMM(a.y),p.ToMM(z.y)),max(p.ToMM(a.x),p.ToMM(z.x)),max(p.ToMM(a.y),p.ToMM(z.y)))))

def cells(rect,margin):
 a,c,d,e=rect
 for x in range(math.floor((a-margin)/S),math.ceil((d+margin)/S)+1):
  for y in range(math.floor((c-margin)/S),math.ceil((e+margin)/S)+1):yield(x,y)
def grid(v):return(round(v[0]/S),round(v[1]/S))
def seg(a,z,net,layer):
 t=p.PCB_TRACK(b);t.SetStart(p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1])));t.SetEnd(p.VECTOR2I(p.FromMM(z[0]),p.FromMM(z[1])));t.SetWidth(p.FromMM(WIDTH));t.SetLayer(p.F_Cu if layer==0 else p.B_Cu);t.SetNetCode(b.FindNet(net).GetNetCode());b.Add(t)
 trackobs[layer].append((net,(min(a[0],z[0]),min(a[1],z[1]),max(a[0],z[0]),max(a[1],z[1]))))
def route(a,z,net):
 blocked=[set(),set()]
 for n,rect,layers in pads:
  if n==net:continue
  for la in layers:blocked[la].update(cells(rect,8.1 if n in ('L_FUSED','L_SWITCHED','L_AUX_FUSED','N') else PADM))
 for la in(0,1):
  for n,rect in trackobs[la]:
   if n!=net:blocked[la].update(cells(rect,CLEAR+WIDTH+.045))
 start=(*grid(a),0);end=(*grid(z),0)
 for state in(start,end):blocked[state[2]].discard(state[:2])
 queue=[(0,0,start)];dist={start:0};prev={};found=False
 while queue:
  _,g,cur=heapq.heappop(queue)
  if g!=dist[cur]:continue
  if cur==end:found=True;break
  x,y,l=cur
  for dx,dy in[(1,0),(-1,0),(0,1),(0,-1),(0,0)]:
   nl=1-l if dx==dy==0 else l;nx=x+dx;ny=y+dy;state=(nx,ny,nl)
   if not(31/S<nx<71/S and 2/S<ny<66/S) or (nx,ny) in blocked[nl]:continue
   if nl!=l:
    # via diameter 0.6 needs larger clearance on BOTH layers
    bad=False
    for layer in(0,1):
     if any((nx+ox,ny+oy) in blocked[layer] for ox in range(-3,4) for oy in range(-3,4)):bad=True;break
    if bad or any(math.hypot(nx*S-hx,ny*S-hy)<.3+hr+.26 for hx,hy,hr in holes):continue
   ng=g+(30 if nl!=l else 1)
   if ng<dist.get(state,1e12):dist[state]=ng;prev[state]=cur;heapq.heappush(queue,(ng+abs(nx-end[0])+abs(ny-end[1])+abs(nl-end[2])*30,ng,state))
 if not found:return False
 path=[end]
 while path[-1]!=start:path.append(prev[path[-1]])
 path.reverse();seg(a,(path[0][0]*S,path[0][1]*S),net,0)
 # coalesce straight runs
 last=path[0];direction=None
 for i in range(1,len(path)):
  cur=path[i];pr=path[i-1];d=(cur[0]-pr[0],cur[1]-pr[1],cur[2]-pr[2])
  if d[2]:
   if last!=pr:seg((last[0]*S,last[1]*S),(pr[0]*S,pr[1]*S),net,pr[2])
   v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(p.FromMM(cur[0]*S),p.FromMM(cur[1]*S)));v.SetWidth(p.F_Cu,p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(b.FindNet(net).GetNetCode());b.Add(v)
   for la in(0,1):trackobs[la].append((net,(cur[0]*S-.3,cur[1]*S-.3,cur[0]*S+.3,cur[1]*S+.3)))
   last=cur;direction=None
  elif direction is not None and d!=direction:
   seg((last[0]*S,last[1]*S),(pr[0]*S,pr[1]*S),net,pr[2]);last=pr;direction=d
  else:direction=d
 if last!=path[-1]:seg((last[0]*S,last[1]*S),(path[-1][0]*S,path[-1][1]*S),net,0)
 seg((end[0]*S,end[1]*S),z,net,0);return True
# minimal spanning tree, sensitive local nets first, power last
for net,points in sorted(groups.items(),key=lambda kv:(kv[0] in ('GND_ISO','+3V3_ISO','+5V_ISO'),len(kv[1]))):
 points=list(dict.fromkeys(points));tree=[points.pop(0)]
 while points:
  d,i,a=min((math.dist(a,z),i,a) for a in tree for i,z in enumerate(points));z=points.pop(i)
  ok=route(a,z,net);routes.append(dict(net=net,start=a,end=z,routed=ok));tree.append(z)
  print(net,ok,flush=True)
seen=set()
for t in list(b.GetTracks()):
 if isinstance(t,p.PCB_VIA):
  key=(t.GetPosition().x,t.GetPosition().y)
  if key in seen:b.Remove(t)
  else:seen.add(key)
p.SaveBoard(str(R/'carbonmirror.kicad_pcb'),b)
(R/'validation/routing.json').write_text(json.dumps(routes,indent=2))
