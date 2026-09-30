#!/usr/bin/python3
import complete_lv as a
p=a.p;b=a.b
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA) or t.GetNetname()!='TEMP_ALERT':continue
 if set([a.xy(t.GetStart()),a.xy(t.GetEnd())])==set([(56.375,55.5),(56.375,50.875)]):
  t.SetStart(p.VECTOR2I(p.FromMM(56.375),p.FromMM(55.5)));t.SetEnd(p.VECTOR2I(p.FromMM(56.375),p.FromMM(52)))
  a.seg((56.375,52),(56.5,52),'TEMP_ALERT',0);a.seg((56.5,52),(56.5,50.875),'TEMP_ALERT',0);a.seg((56.5,50.875),(56.375,50.875),'TEMP_ALERT',0);break
# Exact 0.15 mm rules plus the router's 11 um modelling guard for this escape.
a.C=.15
# The grid path has enough actual copper clearance; use the larger guard elsewhere.
a.route('GND_ISO',(57.2875,55),(60.3,56.8),0,1)
p.ZONE_FILLER(b).Fill(b.Zones());p.SaveBoard(str(a.P),b)
