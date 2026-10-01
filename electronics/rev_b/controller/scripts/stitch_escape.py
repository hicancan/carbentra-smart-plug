from pathlib import Path
exec(Path(__file__).with_name('route_controller.py').read_text(encoding='utf-8').split('groups={}')[0])
S=.05;NX=1441;NY=1361;xx,yy=np.meshgrid(np.arange(NX)*S,np.arange(NY)*S,indexing='ij');D=.45;DR=.2
zs={0 if z.GetLayer()==p.F_Cu else 1:z for z in b.Zones()};fsp=zs[0].GetFilledPolysList(p.F_Cu);bsp=zs[1].GetFilledPolysList(p.B_Cu)
for i in range(fsp.OutlineCount()):
 o=fsp.Outline(i);bb=o.BBox();center=xy(bb.GetCenter());via=obs('GND_ISO',D/2);vb=via[0]|via[1];candidates=[]
 for x in range(max(620,int(p.ToMM(bb.GetLeft())/S)),min(1420,int(p.ToMM(bb.GetRight())/S))+1):
  for y in range(max(20,int(p.ToMM(bb.GetTop())/S)),min(1340,int(p.ToMM(bb.GetBottom())/S))+1):
   if vb[x,y]:continue
   q=p.VECTOR2I(p.FromMM(x*S),p.FromMM(y*S))
   if fsp.Contains(q,i):candidates.append((math.dist((x*S,y*S),center),x,y))
 if not candidates:print('NO ESCAPE',i,center,flush=True);continue
 # Focus on known isolated source regions only, not already stitched broad areas.
 if not (47<center[0]<53 and 15<center[1]<38):continue
 _,x,y=min(candidates);v=p.PCB_VIA(b);v.SetPosition(p.VECTOR2I(p.FromMM(x*S),p.FromMM(y*S)));v.SetWidth(p.F_Cu,p.FromMM(D));v.SetDrill(p.FromMM(DR));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNetCode(b.FindNet('GND_ISO').GetNetCode());b.Add(v);print('ESCAPE',i,x*S,y*S,flush=True)
 route('GND_ISO',(x*S,y*S),(43.1,33.95),1,1)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(P),b)
