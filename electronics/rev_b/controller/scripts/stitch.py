#!/usr/bin/python3
from pathlib import Path
exec(Path(__file__).with_name('route_controller.py').read_text().split('groups={}')[0])
D=.45;DR=.2
zs={0 if z.GetLayer()==p.F_Cu else 1:z for z in b.Zones()};fsp=zs[0].GetFilledPolysList(p.F_Cu);bsp=zs[1].GetFilledPolysList(p.B_Cu)
for i in range(fsp.OutlineCount()):
 o=fsp.Outline(i);bb=o.BBox();center=xy(bb.GetCenter());via=obs('GND_ISO',D/2);vb=via[0]|via[1];candidates=[]
 for x in range(max(311,int(p.ToMM(bb.GetLeft())/S)),min(710,int(p.ToMM(bb.GetRight())/S))+1):
  for y in range(max(11,int(p.ToMM(bb.GetTop())/S)),min(670,int(p.ToMM(bb.GetBottom())/S))+1):
   if vb[x,y]:continue
   q=p.VECTOR2I(p.FromMM(x*S),p.FromMM(y*S))
   if fsp.Contains(q,i) and bsp.Contains(q):candidates.append((math.dist((x*S,y*S),center),x,y))
 if not candidates:print('NO STITCH LOCATION',i,center,flush=True);continue
 _,x,y=min(candidates);v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(p.FromMM(x*S),p.FromMM(y*S)));v.SetWidth(p.F_Cu,p.FromMM(D));v.SetDrill(p.FromMM(DR));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(b.FindNet('GND_ISO').GetNetCode());b.Add(v);print('STITCH',i,x*S,y*S,flush=True)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(P),b)
