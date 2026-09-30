#!/usr/bin/python3
"""Digital travel/contact checks, not a child-safety or durability certification."""
import os,sys,json
B=os.path.dirname(os.path.abspath(__file__));sys.path.extend(['/usr/lib/freecad-python3/lib',B])
import socket_b_features as m
moving=['ShutterSlider','Pawl_L','Pawl_N','PawlSpring_L','PawlSpring_N','ShutterReturnSpring']
static=['ShutterGuide','FrontLid','Carrier']
states=[('closed',0,0,0),('both_released',0,.8,.8),('single_L_attempt',2,.8,0),('single_N_attempt',2,0,.8)]+[('travel_'+str(t),t,.8,.8) for t in [2,4,6,8,10,12.5]]+[('open_rest',12.5,0,0)]
out=[]
fixed={k:m.shape(k) for k in static}
for label,t,l,r in states:
 objs={k:m.shape(k,108,93,65,t,l,r) for k in moving};objs.update(fixed);pairs=[]
 names=list(objs)
 for i,a in enumerate(names):
  for b in names[i+1:]:
   if a in static and b in static:continue
   if not objs[a].BoundBox.intersect(objs[b].BoundBox):continue
   v=objs[a].common(objs[b]).Volume
   if v>1e-5:pairs.append({'a':a,'b':b,'volume_mm3':v})
 passages=[]
 for p in m.S:
  keep=m.slot(2.2,8.4,43.5 if p['name']=='PE' else 46.5,22,p['x'],p['y'],p['angle'])
  occupied=sum(objs[k].common(keep).Volume for k in moving+['ShutterGuide'] if objs[k].BoundBox.intersect(keep.BoundBox))
  passages.append({'pin':p['name'],'blocked_volume_mm3':occupied})
 out.append({'state':label,'travel_mm':t,'pawl_strokes_mm':[l,r],'intersections':pairs,'insertion_paths':passages})
report={'scope':'Provisional digital geometry. Pawl labels L/N in CAD are legacy mechanical side IDs; test left/right strokes are physical sides, not line/neutral nets. Single-pin states must be mechanically blocked; both-released travel must be clear. No force, abuse, tolerance or certification claim.','states':out}
json.dump(report,open(B+'/shutter_kinematic_report.json','w'),indent=2)
for row in out:print(row['state'],row['intersections'],row['insertion_paths'])
