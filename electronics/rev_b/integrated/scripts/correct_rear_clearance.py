"""Bounded rear-blade integration correction; actual 3D assembly audit remains required.
Preserves all footprint placement. Replaces only two low-voltage branches and trims plane.
"""
import route_signals as r
import math,hashlib
assert hashlib.sha256(r.P.read_bytes()).hexdigest()=="54485373c84268d072b8abb9a73405d867b58622657f3cf49976cbcab7c0f40a", "This one-time correction only accepts the pre-integration board; use routing_recipe.json for normal rebuilds"
# Original blade top polygon, transformed from mechanical world to native PCB XY.
poly=[(55.42282,50.3074),(56.98166,51.2074),(61.03166,44.1926),(59.47282,43.2926)]
oldobs=r.obs
def block(n,rad):
 a=oldobs(n,rad)
 if n.startswith('HOT_'):return a
 # 6mm projected reserve on bottom/inner copper around the rear tail.
 # Through vias carry their bottom annulus even when their recorded layer is F.Cu.
 inside=r.np.zeros((r.NX,r.NY),bool);near=inside.copy()
 for u,v in zip(poly,poly[1:]+poly[:1]):
  dx=v[0]-u[0];dy=v[1]-u[1];t=r.np.clip(((r.xx-u[0])*dx+(r.yy-u[1])*dy)/(dx*dx+dy*dy),0,1)
  near|=(r.xx-u[0]-t*dx)**2+(r.yy-u[1]-t*dy)**2<(6.0+rad)**2
  inside^=((u[1]>r.yy)!=(v[1]>r.yy))&(r.xx<(v[0]-u[0])*(r.yy-u[1])/(v[1]-u[1]+1e-100)+u[0])
 mask=near|inside
 for l in ([0,1,2,3] if rad>.1 else [1,2,3]):a[l]|=mask
 return a
r.obs=block
remove5={394,395,398,399,400,402,403,404,406,407}
remove3={35,65,184,264,271,285}
held_tracks=list(r.b.GetTracks())
for i,t in enumerate(held_tracks):
 if i in remove5|remove3:r.b.Remove(t)
assert r.route('+5V_ISO',(63.4,38.3),(71.2,53.7),3,3)
assert r.route('+3V3_ISO',(63,34.7),(64,40.825),1,0)
# The filled plane does not approach the rear termination from the right.
for z in r.b.Zones():
 if not z.GetIsRuleArea() and z.GetNetname()=='GND_ISO':
  z.Outline().RemoveAllContours();o=z.Outline();o.NewOutline()
  for x,y in [(49,1),(99,1),(99,84),(64,84),(64,60),(70,60),(70,34),(64,34),(64,23),(49,20.5)]:o.Append(r.p.FromMM(x),r.p.FromMM(y))
r.p.ZONE_FILLER(r.b).Fill(r.b.Zones());r.p.SaveBoard(str(r.P),r.b)
